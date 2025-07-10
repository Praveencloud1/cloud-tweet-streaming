# Cloud-Based Tweet Text Processing using MapReduce & Kinesis

This project demonstrates a scalable cloud processing pipeline that ingests tweet data, applies parallel word counting using both local and distributed (MapReduce) methods, and benchmarks performance across different dataset sizes. Built with Python and AWS services like Kinesis, this project simulates both streaming and batch-based analytics in the cloud.

---

## Project Structure

- **csv_tweet_feeder_to_stream.py** Pushes tweet data row by row into AWS Kinesis stream
- **csv_tweet_reader_from_stream.py** Consumes and processes records from Kinesis stream
- **dual_mode_text_counter.py** Runs word count using Plain Python and MRJob (MapReduce)
- **plot_throughput.py** Plots benchmark comparison (execution time vs input size)
- **twitter_*.csv** Multiple test datasets of varying sizes
- **benchmark_full_results.csv** Stores execution times for PlainPython and MRJob runs
- **benchmark_scaled_comparison.png** Visualization of benchmark results


---

## Features

- **Text Data Ingestion**: Reads CSV tweets and streams them to AWS Kinesis
- **Real-time Stream Processing**: Consumes Kinesis data in near real-time
- **Parallel Word Counting**:
  - `PlainPython`: sequential mode using `collections.Counter`
  - `MRJob`: distributed mode using MapReduce paradigm
- **Performance Benchmarking**: Measures execution time for both modes
- **Data Visualization**: Creates grouped bar chart comparing speed at different input sizes

---

## Benchmark Example

Benchmarks are saved in `timelog_results.csv` and visualized using `plot_throughput.py`.

| Size   | Run Type         | Seconds | Throughput (Records/sec) |
|--------|------------------|---------|---------------------------|
| 996    | PlainPython      | 0.01    | 79461.45                  |
| 996    | DistributedMRJob | 0.38    | 2638.61                   |
| 9888   | PlainPython      | 0.11    | 87312.72                  |
| 9888   | DistributedMRJob | 1.63    | 6050.18                   |
| 29738  | PlainPython      | 0.33    | 91395.26                  |
| 29738  | DistributedMRJob | 4.12    | 7226.38                   |
| 73317  | PlainPython      | 0.81    | 89981.80                  |
| 73317  | DistributedMRJob | 9.97    | 7356.72                   |

---

## How to Run

1. Upload your tweet dataset (CSV format) to the EC2 instance.
2. Activate your virtual environment.
3. Stream the tweets to Kinesis: python3 csv_tweet_feeder_to_stream.py ```
4. Consume the stream: python3 csv_tweet_reader_from_stream.py
5. Run the benchmarking test: python3 dual_mode_text_counter.py
6. Generate the graph: python3 plot_throughput.py

## Requirements

- Python 3.12+
- AWS CLI configured
- boto3
- pandas
- matplotlib
- mrjob
## Install via:

pip install -r requirements.txt
