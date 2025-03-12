import tkinter as tk
from tkinter import messagebox
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

API_URL = "http://your-server-ip:5000"

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Performance Dashboard")
        self.root.geometry("600x400")
        
        self.label = tk.Label(root, text="Real-Time Performance", font=("Arial", 14))
        self.label.pack()
        
        self.canvas = tk.Canvas(root, width=500, height=200)
        self.canvas.pack()
        
        self.refresh_button = tk.Button(root, text="Refresh", command=self.update_data)
        self.refresh_button.pack()
        
        self.threshold = 80
        self.update_data()
        self.auto_refresh()
    
    def fetch_data(self):
        try:
            response = requests.get(f"{API_URL}/realtime")
            return response.json()
        except:
            return None
    
    def update_data(self):
        data = self.fetch_data()
        if data:
            self.canvas.delete("all")
            
            # Display Metrics
            self.canvas.create_text(250, 50, text=f"CPU: {data['cpu']}%", font=("Arial", 12))
            self.canvas.create_text(250, 80, text=f"Memory: {data['memory']}%", font=("Arial", 12))
            self.canvas.create_text(250, 110, text=f"Disk: {data['disk']}%", font=("Arial", 12))
            
            if data['cpu'] > self.threshold or data['memory'] > self.threshold:
                messagebox.showwarning("Warning", "High CPU or Memory Usage!")
    
    def auto_refresh(self):
        self.update_data()
        self.root.after(10000, self.auto_refresh)

root = tk.Tk()
dashboard = Dashboard(root)
root.mainloop()
