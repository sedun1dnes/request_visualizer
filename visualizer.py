import tkinter as tk
from tkinter import *
import pandas as pd
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from tkinter import filedialog
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
            
            self.root.config(cursor="wait")
            self.reader = Data_reader(file_path)
            self.data = self.reader.load_data()
            

            for item in self.request_tree.get_children():
                self.request_tree.delete(item)
            self.requests = self.reader.get_requests()
            for id, lifecycle in self.requests.items():
                self.request_tree.insert("", "end", text=id, values=(id, str(lifecycle)))

            self.lifecycle_stat = dict(sorted(self.get_requests_of_lifecycle_data().items(), key = lambda x: len(x[1]), reverse = True))
            for item in self.lifecycle_tree.get_children():
                self.lifecycle_tree.delete(item)
            for lifecycle, requests in self.lifecycle_stat.items():
                self.lifecycle_tree.insert("", "end", text=id, values=(str(lifecycle), len(requests)))
        
            self.init_graph()
        
    def get_requests_of_lifecycle_data(self):
        requests_of_lifecycle = {}
        data = self.reader.result

        for key, value in data.items():
            new_key = [tuple(point) for point in value]
            requests_of_lifecycle.setdefault(tuple(new_key), []).append(key)
        return requests_of_lifecycle

    def get_statistic(self, lifecycle):
        amount_of_requests = len(self.lifecycle_stat[lifecycle])
        return (f"кол-во заявок с таким же жизненным циклом: {amount_of_requests}")

    def on_tree_click(self, event):
        item = self.request_tree.focus() 
        print("Clicked on item:", self.request_tree.item(item, "text"))
        lifecycle = self.requests[self.request_tree.item(item, "text")]
        
        edges = self.get_edges(lifecycle)

        plt.clf()
        
        colors = nx.get_edge_attributes(self.G, "color")

        for edge in edges:
            colors[tuple(edge)] = "red"

        nx.draw_networkx_nodes(self.G, self.pos, node_color="tab:blue", node_size=100, alpha=0.4)
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
        #self.statistic_canvas.clipboard_clear()
        #self.statistic_canvas.create_text(200, 100, text = self.get_statistic(tuple([tuple(point) for point in lifecycle])))

        # Упаковываем холст в окно Tkinter
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def init_graph(self):
        self.G = nx.DiGraph()
        data = self.reader.get_nodes()
        self.G.add_nodes_from(data)
        pos = self.get_pos_values(data)
        self.get_pos_array(pos)
        self.G.add_edges_from(self.reader.get_edges(), color = "grey")
        self.draw_graph()
    
    def draw_graph(self):
        self.graph_canvas.destroy()
        self.graph_canvas = tk.Canvas(self.root, width=600, height=800)
        self.graph_canvas.pack(anchor = NW, side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.figure = plt.figure()

        nx.draw_networkx_nodes(self.G, self.pos, node_color="tab:blue", node_size=100, alpha=0.5)
        nx.draw_networkx_labels(self.G, pos=self.pos, font_size = 6, font_weight="bold")  
        nx.draw_networkx_edges(
                                    self.G,
                                    self.pos,
                                    edgelist=self.G.edges,
                                    edge_color="grey",
                                )

        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_canvas)
        self.canvas.draw()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_canvas)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.root.config(cursor = "")

    def get_edges(self, request):
        edges = []
        for i in range(len(request)-1):
            edges.append([str(tuple(request[i])), str(tuple(request[i+1]))])
        return edges

    def __init__(self, root):

        self.root = root
        self.root.title("Request visualizer")
        
        self.graph_canvas = tk.Canvas(self.root, width=600, height=800)
        self.graph_canvas.pack(anchor = NW, side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.forest_frame = ttk.Frame(self.root)

        import_button = tk.Button(master = self.forest_frame, text="Import CSV", command=self.import_csv)
        import_button.pack(anchor = NW)

        self.request_frame = ttk.Frame(master = self.forest_frame)
        self.request_frame.config(cursor = "hand2")
        self.request_tree = ttk.Treeview(self.request_frame, columns=("request", "lifecycle"))
        self.request_tree.heading("#0", text="ID")
        self.request_tree.heading("#1", text="Request ID")
        self.request_tree.heading("#2", text="Lifecycle")
        self.request_tree.column("#0", stretch=tk.NO, width=0)
        self.request_tree.column("#1", stretch=tk.YES, width=80)
        self.request_tree.column("#2", stretch=tk.YES, width=300)
        v_scrollbar = ttk.Scrollbar(master = self.request_frame, orient="vertical", command=self.request_tree.yview)
        self.request_tree.configure(yscroll=v_scrollbar.set)
        v_scrollbar.pack(side = tk.RIGHT, fill = Y, expand = True)
        self.request_tree.bind("<ButtonRelease-1>", self.on_tree_click)
        self.request_tree.pack(anchor = NW, side = tk.LEFT, fill = Y, expand = True)
        self.request_frame.pack(anchor = NW, side = tk.TOP, fill = Y, expand=True)

        self.lifecycle_frame = ttk.Frame(master = self.forest_frame)
        self.lifecycle_tree = ttk.Treeview(self.lifecycle_frame, columns=("lifecycle", "cases"))
        self.lifecycle_tree.heading("#0", text="ID")
        self.lifecycle_tree.heading("#1", text="Lifecycle")
        self.lifecycle_tree.heading("#2", text="Cases")
        self.lifecycle_tree.column("#0", stretch=tk.NO, width=0)
        self.lifecycle_tree.column("#1", stretch=tk.YES, width=300)
        self.lifecycle_tree.column("#2", stretch=tk.YES, width=80)
        v_scrollbar_LC = ttk.Scrollbar(master = self.lifecycle_frame, orient="vertical", command=self.lifecycle_tree.yview)
        self.lifecycle_tree.configure(yscroll=v_scrollbar_LC.set)
        v_scrollbar_LC.pack(side=tk.RIGHT, fill = Y, expand = True)
        self.lifecycle_tree.pack(anchor = NW, fill = Y, expand=True, side = tk.LEFT)
        self.lifecycle_frame.pack(anchor = NW, side = tk.BOTTOM, fill = Y, expand=True)

        self.forest_frame.pack(anchor = NW, side = LEFT, fill = Y, expand = False)
        
       # self.statistic_canvas = tk.Canvas(self.frame, bg = 'white', highlightthickness=1, highlightbackground = 'black')
       # self.statistic_canvas.pack(anchor = NW, fill = BOTH)


root = tk.Tk()
app = Application(root)
root.mainloop()


