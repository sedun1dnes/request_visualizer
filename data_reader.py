from typing import Any
import pandas as pd
import json

class Data_reader:
    def __init__(self, path) -> None:
        self.path = path
        
    def load_data(self):
        self.df = pd.read_csv(self.path, header = 0, delimiter=';')
        self.result = self.df.groupby("ticket_id")[['queue_id', 'owner_id']].apply(lambda x: x.values.tolist()[::-1]).reset_index()
        

    def get_edges(self):
        edges = []
        print(self.result)

        
        for values in self.result.values():
            for i in range(len(values)-1):
                edges.extend([[str(tuple(values[i])), str(tuple(values[i+1]))] for i in range(len(values)-1)])

        unique_tuples = {tuple(lst) for lst in edges}
        unique_lists = [tuple(t) for t in unique_tuples]
        return unique_lists

    def get_requests(self):
        self.result = dict(zip(self.result['ticket_id'], self.result[0]))
#        self.result.to_csv('processed_data.csv', index=False, header = headers)
        return self.result
    
    def get_nodes(self):
        unique_pairs = self.df[['queue_id', 'owner_id']].drop_duplicates().apply(tuple, axis=1)
        unique_pairs = [str(unique_pair) for unique_pair in unique_pairs]
        return unique_pairs
        

