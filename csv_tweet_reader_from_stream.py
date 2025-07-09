import boto3
import json
import time
from collections import deque, Counter
from datetime import datetime, timedelta, timezone

STREAM_LABEL = 'TweetStream'
PRIMARY_SHARD = 'shardId-000000000000'

cloud_connector = boto3.client('kinesis', region_name='us-east-1')

initial_position = cloud_connector.get_shard_iterator(
    StreamName=STREAM_LABEL,
    ShardId=PRIMARY_SHARD,
    ShardIteratorType='LATEST'
)['ShardIterator']

rolling_window = deque()
window_duration = timedelta(minutes=5)

print("Listening to incoming Kinesis records...")

while True:
    kinesis_batch = cloud_connector.get_records(ShardIterator=initial_position, Limit=10)
    capture_time = datetime.now(timezone.utc)

    for each_entry in kinesis_batch['Records']:
        unpacked_payload = json.loads(each_entry['Data'])
        content_piece = unpacked_payload['tweet_text']
        written_timestamp = datetime.fromisoformat(unpacked_payload['written_at'])
        rolling_window.append((written_timestamp, content_piece))

    while rolling_window and (capture_time - rolling_window[0][0]) > window_duration:
        rolling_window.popleft()

    frequency_chart = Counter()
    for _, snippet in rolling_window:
        keywords = [word.lower() for word in snippet.split() if len(word) > 3]
        frequency_chart.update(keywords)

    hot_trends = frequency_chart.most_common(5)
    print(f"\nTrending Words (last 5 min) — Total: {len(rolling_window)} messages")
    for trend_word, count in hot_trends:
        print(f"{trend_word}: {count}")

    initial_position = kinesis_batch['NextShardIterator']
    time.sleep(5)
