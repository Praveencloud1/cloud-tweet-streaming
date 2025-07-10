import time
import re
import subprocess
import csv
import sys
import os
import inspect
import pandas as dream_io
import boto3
from collections import Counter
from mrjob.job import MRJob

WORD_SCANNER = re.compile(r"[\w']+")

class ParallelWordAnalyzer(MRJob):
    def mapper(self, _, paragraph):
        for token in WORD_SCANNER.findall(paragraph):
            yield (token.lower(), 1)

    def combiner(self, token, batch_counts):
        yield (token, sum(batch_counts))

    def reducer(self, token, all_counts):
        yield (token, sum(all_counts))

def run_plain_python_check(cloud_entries):
    print("\n[LOCAL-MODE] Counting words using simple Python...")
    tick_start = time.time()
    manual_count_sheet = Counter()

    for single_line in cloud_entries:
        chopped = re.findall(r"[\w']+", single_line)
        for item in chopped:
            manual_count_sheet[item.lower()] += 1

    tick_end = time.time()
    time_spent = tick_end - tick_start
    print(f"[LOCAL-MODE] Completed in {time_spent:.2f} seconds.")
    return manual_count_sheet, time_spent

def run_mrjob_check(input_plaintext):
    print("\n[MRJOB-MODE] Distributing task using temporary MRJob script...")
    timer_begin = time.time()

    cloud_script = "backup_counter_script.py"
    with open(cloud_script, "w", encoding="utf-8") as file_writer:
        file_writer.write("from mrjob.job import MRJob\n")
        file_writer.write("import re\n")
        file_writer.write("WORD_SCANNER = re.compile(r\"[\\w']+\")\n\n")
        file_writer.write(inspect.getsource(ParallelWordAnalyzer))
        file_writer.write("\n\nif __name__ == '__main__':\n")
        file_writer.write("    ParallelWordAnalyzer.run()\n")

    output_path = "mrjob_output.txt"
    execute_job = subprocess.Popen(
        ['python3', cloud_script, input_plaintext, '--output', output_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    _, raw_errors = execute_job.communicate()

    timer_end = time.time()
    time_spent = timer_end - timer_begin
    print(f"[MRJOB-MODE] Finished in {time_spent:.2f} seconds.")

    merged_results = {}
    if os.path.exists(output_path) and os.path.isdir(output_path):
        for fname in os.listdir(output_path):
            fpath = os.path.join(output_path, fname)
            with open(fpath, 'r', encoding='utf-8') as reader:
                for raw_row in reader:
                    if raw_row.strip():
                        try:
                            parts = raw_row.strip().split('\t')
                            if len(parts) == 2:
                                word = parts[0].strip('"')
                                count = int(parts[1])
                                merged_results[word] = count
                        except:
                            continue
        for fname in os.listdir(output_path):
            os.remove(os.path.join(output_path, fname))
        os.rmdir(output_path)
    else:
        print("MRJob finished, but output folder was not found or was empty.")

    if os.path.exists(cloud_script):
        os.remove(cloud_script)

    return merged_results, time_spent

def archive_timings(local_secs, cloud_secs, filename='timelog_results.csv', size=None, total_records=None):
    write_header = not os.path.exists(filename)

    with open(filename, 'a') as tracker:
        if write_header:
            tracker.write("Size,RunType,Seconds,Throughput,Latency\n")

        if size is not None and total_records is not None:
            tracker.write(f"{size},PlainPython,{local_secs:.2f},{total_records/local_secs:.2f},{local_secs/total_records:.6f}\n")
            tracker.write(f"{size},DistributedMRJob,{cloud_secs:.2f},{total_records/cloud_secs:.2f},{cloud_secs/total_records:.6f}\n")
        else:
            tracker.write(f"PlainPython,{local_secs:.2f},,,\n")
            tracker.write(f"DistributedMRJob,{cloud_secs:.2f},,,\n")

    print(f"[ARCHIVE] Timing data appended to '{filename}'")

def upload_file_to_s3(local_path, bucket_name, s3_key):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(local_path, bucket_name, s3_key)
        print(f"[S3 UPLOAD] '{local_path}' uploaded to 's3://{bucket_name}/{s3_key}'")
    except Exception as e:
        print(f"[S3 ERROR] Failed to upload to S3: {e}")

if __name__ == '__main__':
    structured_csv_file = 'twitter_1000.csv'
    interim_txt_input = 'intermediate_lines.txt'

    if not os.path.exists(structured_csv_file):
        print(f"Dataset missing: {structured_csv_file}")
        sys.exit(1)

    full_sheet = dream_io.read_csv(structured_csv_file, names=['id', 'topic', 'sentiment', 'text'], skiprows=1)
    if 'text' not in full_sheet.columns:
        print("No 'text' column present in the CSV. Check column names.")
        sys.exit(1)

    extracted_lines = full_sheet['text'].dropna().astype(str).tolist()
    record_count = len(extracted_lines)
    print(f"Total records processed: {record_count}")

    with open(interim_txt_input, 'w', encoding='utf-8') as file_dumper:
        for text_entry in extracted_lines:
            file_dumper.write(text_entry + "\n")

    handwritten_result, python_time = run_plain_python_check(extracted_lines)
    parallel_result, mrjob_time = run_mrjob_check(interim_txt_input)

    sequential_throughput = record_count / python_time
    parallel_throughput = record_count / mrjob_time

    sequential_latency = python_time / record_count
    parallel_latency = mrjob_time / record_count

    print("\n[SIMPLE] Top 5 Words:")
    print(Counter(handwritten_result).most_common(5))

    print("\n[DISTRIBUTED] Top 5 Words:")
    print(Counter(parallel_result).most_common(5))

    print(f"\n[METRICS]")
    print(f"Sequential Throughput: {sequential_throughput:.2f} records/sec")
    print(f"Parallel Throughput:   {parallel_throughput:.2f} records/sec")
    print(f"Sequential Latency:    {sequential_latency:.6f} sec/record")
    print(f"Parallel Latency:      {parallel_latency:.6f} sec/record")

    archive_timings(python_time, mrjob_time, size=record_count, total_records=record_count)

    s3_bucket = "catweetstreambucket"
    s3_key = "metrics/timelog_results.csv"
    upload_file_to_s3("timelog_results.csv", s3_bucket, s3_key)

    if os.path.exists(interim_txt_input):
        os.remove(interim_txt_input)
