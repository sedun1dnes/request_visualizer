import pandas as pd
import json

df = pd.read_csv("admin-select-20240114-203528.csv", header = 0, delimiter=';')

headers = ["request", "lifecycle"]


result = df.groupby("ticket_id")[['queue_id', 'owner_id']].apply(lambda x: x.values.tolist()[::-1]).reset_index()
unique_pairs = df[['queue_id', 'owner_id']].drop_duplicates().apply(tuple, axis=1)

result.to_csv('processed_data.csv', index=False, header = headers)
unique_pairs.to_csv('graph_nodes.csv', index = False, header = ["status_node"])

edges = []

index_iterator = result.index
for index in index_iterator:
    value = result.iloc[index, 1]
    edges.extend([[str(tuple(value[i])), str(tuple(value[i+1]))] for i in range(len(value)-1)])

print(edges)
unique_tuples = {tuple(lst) for lst in edges}
unique_lists = [list(t) for t in unique_tuples]

with open("edges.json", "w") as f:
    json.dump(unique_lists, f)
