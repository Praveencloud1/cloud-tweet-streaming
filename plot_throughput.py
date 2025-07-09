import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('timelog_results.csv')

plt.figure(figsize=(6, 4))
plt.bar(df['RunType'], df['Seconds'], color=['orange', 'skyblue'])

plt.title("Word Count Benchmark: Sequential vs MRJob")
plt.ylabel("Duration (seconds)")
plt.tight_layout()
plt.savefig('single_benchmark_bar.png')
plt.show()
