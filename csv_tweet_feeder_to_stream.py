import boto3
import pandas as project_sheets
import json
import time
from datetime import datetime, timezone

CSV_DATA_SOURCE = 'twitter_training.csv'
STREAM_CHANNEL = 'TweetStream'

cloud_faucet = boto3.client('kinesis', region_name='us-east-1')

try:
    tweet_archive = project_sheets.read_csv(CSV_DATA_SOURCE, header=None,
                                            names=['entry_id', 'discussion', 'emotion', 'content'])
except FileNotFoundError:
    print("Source CSV missing. Please check the filename.")
    exit()

print(f"Loaded {len(tweet_archive)} tweet samples.")

for index, tweet_row in tweet_archive.iterrows():
    if index >= 100:
        break

    content_block = tweet_row.get('content', '')
    if not isinstance(content_block, str) or len(content_block.split()) < 4:
        print(f"Skipping row {index + 1}: short or invalid → '{content_block}'")
        continue

    tweet_packet = {
        'tweet_text': content_block,
        'written_at': datetime.now(timezone.utc).isoformat()
    }

    try:
        stream_push = cloud_faucet.put_record(
            StreamName=STREAM_CHANNEL,
            Data=json.dumps(tweet_packet),
            PartitionKey='csv-sim-key'
        )
        print(f"Sent row {index + 1}: {content_block[:80]}")
    except Exception as dispatch_error:
        print("Error pushing to Kinesis:", dispatch_error)

    time.sleep(0.3)
