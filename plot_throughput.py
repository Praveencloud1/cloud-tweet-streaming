import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('cloud/timelog_results.csv')
df['Size'] = df['Size'].astype(int)
df['RunType'] = df['RunType'].str.strip()

pivot_df = df.pivot(index='Size', columns='RunType', values='Seconds')
ax = pivot_df.plot(kind='bar', figsize=(8, 5), colormap='Set2')
for container in ax.containers:
    ax.bar_label(container, fmt='%.2f', fontsize=9, label_type='edge')

plt.title("Benchmark: Plain Python vs MRJob at Different Input Sizes")
plt.xlabel("Input Size (Lines)")
plt.ylabel("Execution Time (Seconds)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("benchmark_scaled_comparison.png")
plt.show()
