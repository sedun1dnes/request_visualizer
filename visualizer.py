import tkinter as tk
from tkinter import *
import pandas as pd
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from tkinter import filedialog
import json
import ast
import math
from data_reader import Data_reader

class Application:

    def distribute_points(self, x, y, radius, n):
        points = []
        for i in range(n):
            angle = i * (360/n)
            x_i = x + radius * math.cos(math.radians(angle))
            y_i = y + radius * math.sin(math.radians(angle))
            points.append((x_i, y_i))
        return points

    def get_pos_values(self, nodes):
        pos = {}

        for node in nodes:
            queue, employee = ast.literal_eval(node)
            if queue not in pos:
                pos[queue] = {}
            pos[queue][employee] = 0
        
        i = 0
        for queue, persons_dict in pos.items():
            for person in persons_dict.keys():
                if person == 1:
                    pos[queue][person] = self.distribute_points(300, 400, 2*len(pos), len(pos))[i]
                    i += 1
        
        for queue, persons_dict in pos.items():
            i = 0
            for person in persons_dict.keys():
                if person != 1:
                    pos[queue][person] = self.distribute_points(pos[queue][1][0], pos[queue][1][1], len(pos[queue])-1, len(pos[queue])-1)[i]
                    i += 1
        return pos
        
    def get_pos_array(self, pos):
        self.pos = {}
        for queue, persons_dict in pos.items():
            for person in persons_dict.keys():
                self.pos[str(tuple([queue, person]))] = pos[queue][person]
        return self.pos


    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

        if file_path:
            self.reader = Data_reader(file_path)
            self.data = self.reader.load_data()

            for item in self.tree.get_children():
                self.tree.delete(item)
            self.requests = self.reader.get_requests()
            for id, lifecycle in self.requests.items():
                self.tree.insert("", "end", text=id, values=(id, str(lifecycle)))
        self.init_graph()
        


    def on_tree_click(self, event):
        item = self.tree.focus() 
        print("Clicked on item:", self.tree.item(item, "text"))
        lifecycle = self.requests[self.tree.item(item, "text")]
        edges = self.get_edges(lifecycle)
        plt.clf()
        colors = nx.get_edge_attributes(self.G, "color")
        for edge in edges:
            colors[tuple(edge)] = "red"
        nx.draw_networkx_nodes(self.G, self.pos, node_color="tab:blue", node_size=100, alpha=0.4)
        #nx.draw(self.G, pos = self.pos, with_labels=False, node_size=50, edge_color=self.colors)
        nx.draw_networkx_labels(self.G, pos=self.pos, font_size = 6, font_weight="bold")  

        nx.draw_networkx_edges(
                                    self.G,
                                    self.pos,
                                    edgelist=self.G.edges,
                                    edge_color=colors.values(),
                                )       
    
        # Обновляем холст Matplotlib
        self.figure = plt.gcf()
        self.canvas.draw()

        # Упаковываем холст в окно Tkinter
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def init_graph(self):
        self.G = nx.DiGraph()
        data = self.reader.get_nodes()
        print(data)
        self.G.add_nodes_from(data)
        pos = self.get_pos_values(data)
        self.get_pos_array(pos)
        self.G.add_edges_from(self.reader.get_edges(), color = "grey")
        self.draw_graph()
    
    def draw_graph(self):
        nx.draw_networkx_nodes(self.G, self.pos, node_color="tab:blue", node_size=100, alpha=0.5)
        nx.draw_networkx_labels(self.G, pos=self.pos, font_size = 6, font_weight="bold")  
        nx.draw_networkx_edges(
                                    self.G,
                                    self.pos,
                                    edgelist=self.G.edges,
                                    edge_color="grey",
                                )

        self.figure = plt.gcf()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_canvas)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_canvas)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def get_edges(self, request):
        edges = []
        for i in range(len(request)-1):
            edges.append([str(tuple(request[i])), str(tuple(request[i+1]))])
        return edges

    def __init__(self, root):

        self.root = root
        self.root.title("Request visualizer")
        
        self.graph_canvas = tk.Canvas(root, width=600, height=800)
        self.graph_canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(root, columns=("request", "lifecycle"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("#1", text="Request ID")
        self.tree.heading("#2", text="Lifecycle")
        self.tree.column("#0", stretch=tk.NO, width=0)
        self.tree.column("#1", stretch=tk.NO, width=50)
        self.tree.column("#2", stretch=tk.NO, width=250)
        v_scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=v_scrollbar.set)
        v_scrollbar.pack(side="right", fill="y")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

        import_button = tk.Button(root, text="Import CSV", command=self.import_csv)
        import_button.pack()

        #df = pd.read_csv('processed_data.csv', header=None, names=['key', 'value'])
        #self.requests = dict(zip(df.drop(0)['key'], df.drop(0)['value']))
    


root = tk.Tk()
app = Application(root)
root.mainloop()


