import tkinter as tk
from tkinter import messagebox
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

API_URL = "http://127.0.0.1:5000"

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Performance Dashboard")
        self.root.geometry("800x500")
        
        # Create the main layout
        self.top_frame = tk.Frame(root, height=200)
        self.top_frame.pack(fill=tk.BOTH, expand=True)
        
        self.bottom_frame = tk.Frame(root, height=300)
        self.bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # Three sections on the top
        self.cpu_frame = tk.Frame(self.top_frame, width=260, height=200, relief=tk.SOLID, borderwidth=2)
        self.cpu_frame.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
        
        self.memory_frame = tk.Frame(self.top_frame, width=260, height=200, relief=tk.SOLID, borderwidth=2)
        self.memory_frame.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
        
        self.disk_frame = tk.Frame(self.top_frame, width=260, height=200, relief=tk.SOLID, borderwidth=2)
        self.disk_frame.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
        
        # Large bottom section for pie chart
        self.pie_chart_frame = tk.Frame(self.bottom_frame, relief=tk.SOLID, borderwidth=2)
        self.pie_chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.update_data()
        self.auto_refresh()
    
    def fetch_data(self):
        try:
            response = requests.get(f"{API_URL}/realtime")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print("Error fetching data:", e)
            return None
    
    def update_data(self):
        data = self.fetch_data()
        if data:
            self.display_data(data)
            self.display_pie_chart(data)
    
    def display_data(self, data):
        for widget in self.cpu_frame.winfo_children():
            widget.destroy()
        for widget in self.memory_frame.winfo_children():
            widget.destroy()
        for widget in self.disk_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.cpu_frame, text=f"CPU: {data.get('cpu', 'N/A')}", font=("Arial", 12)).pack()
        tk.Label(self.memory_frame, text=f"Memory: {data.get('memory', 'N/A')}", font=("Arial", 12)).pack()
        tk.Label(self.disk_frame, text=f"Disk: {data.get('filesystem', 'N/A')}", font=("Arial", 12)).pack()
    
    def display_pie_chart(self, data):
        for widget in self.pie_chart_frame.winfo_children():
            widget.destroy()
        
        labels = ['CPU', 'Memory', 'Disk']
        sizes = [float(data.get('cpu', '0').strip('%')), 
                 float(data.get('memory', '0').split('(')[-1].strip('%)')), 
                 float(data.get('filesystem', '0').strip('%'))]
        
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        
        canvas = FigureCanvasTkAgg(fig, master=self.pie_chart_frame)
        canvas.get_tk_widget().pack()
        canvas.draw()
    
    def auto_refresh(self):
        self.update_data()
        self.root.after(10000, self.auto_refresh)

root = tk.Tk()
dashboard = Dashboard(root)
root.mainloop()
