import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('timelog_results.csv')
df.columns = df.columns.str.strip()
df['Size'] = df['Size'].astype(int)
df['RunType'] = df['RunType'].str.strip()
df['Throughput'] = df['Throughput'].astype(float)
df['Latency'] = df['Latency'].astype(float)
time_df = df.pivot(index='Size', columns='RunType', values='Seconds')
throughput_df = df.pivot(index='Size', columns='RunType', values='Throughput')
latency_df = df.pivot(index='Size', columns='RunType', values='Latency')

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(21, 6))
time_df.plot(kind='bar', ax=ax1, colormap='Set2')
ax1.set_title("Execution Time")
ax1.set_xlabel("Input Size (Records)")
ax1.set_ylabel("Time (Seconds)")
ax1.set_xticklabels(time_df.index, rotation=0)
for container in ax1.containers:
    ax1.bar_label(container, fmt='%.2f', fontsize=8, label_type='edge')

throughput_df.plot(kind='bar', ax=ax2, colormap='viridis')
ax2.set_title("Throughput")
ax2.set_xlabel("Input Size (Records)")
ax2.set_ylabel("Records per Second")
ax2.set_xticklabels(throughput_df.index, rotation=0)
for container in ax2.containers:
    ax2.bar_label(container, fmt='%.0f', fontsize=8, label_type='edge')

latency_df.plot(kind='bar', ax=ax3, colormap='plasma')
ax3.set_title("Latency")
ax3.set_xlabel("Input Size (Records)")
ax3.set_ylabel("Seconds per Record")
ax3.set_xticklabels(latency_df.index, rotation=0)
for container in ax3.containers:
    ax3.bar_label(container, fmt='%.6f', fontsize=8, label_type='edge')
plt.tight_layout()
plt.savefig("benchmark_all_metrics.png")
plt.show()
