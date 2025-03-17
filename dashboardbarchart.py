import tkinter as tk
from tkinter import ttk
import requests
import time
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ENDPOINT_URL = "http://YOUR_SERVER_IP_OR_DOMAIN/stats"  

# Thresholds for triggering a color change or alert
CPU_THRESHOLD = 80.0      # e.g. 80% CPU usage
MEM_THRESHOLD = 75.0      # e.g. 75% memory usage
DISK_THRESHOLD = 80.0     # e.g. 80% disk usage
NET_THRESHOLD = 10.0      # e.g. 10 MB/s
LOAD_THRESHOLD = 2.0      # e.g. load average of 2

x_data = []
cpu_data = []
mem_data = []
disk_data = []
net_data = []
load_data = []

start_time = time.time()

def fetch_stats():
    """
    Fetch JSON data from the remote agent endpoint.
    """
    try:
        resp = requests.get(ENDPOINT_URL, timeout=2)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return None

def update_plot():
    stats = fetch_stats()
    if stats:
        current_time = time.time() - start_time
        x_data.append(current_time)
        cpu_data.append(stats["cpu"])
        mem_data.append(stats["mem"])
        disk_data.append(stats["disk"])
        net_data.append(stats["network"])
        load_data.append(stats["load"])

        selected = metric_var.get()
        metric_values = {
            "CPU": cpu_data,
            "Memory": mem_data,
            "Disk": disk_data,
            "Network": net_data,
            "Load": load_data,
        }
        
        current_metric_data = metric_values[selected][-1] if metric_values[selected] else 0
        
        # Update the bar chart
        ax_bar.clear()
        ax_bar.bar([selected], [current_metric_data], color="blue")
        ax_bar.set_ylabel("Metric Value")
        ax_bar.set_ylim(0, 100)
        canvas_bar.draw()
    
    root.after(2000, update_plot)

root = tk.Tk()
root.title("Server Performance Dashboard")
root.geometry("1200x800")  

options_frame = ttk.Frame(root)
options_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

metric_var = tk.StringVar(value="CPU")
metrics = ["CPU", "Memory", "Disk", "Network", "Load"]
for m in metrics:
    r = ttk.Radiobutton(options_frame, text=m, variable=metric_var, value=m)
    r.pack(side=tk.LEFT, padx=5)

fig_bar, ax_bar = plt.subplots()
ax_bar.set_ylabel("Metric Value")
ax_bar.set_ylim(0, 100)
canvas_bar = FigureCanvasTkAgg(fig_bar, master=root)
canvas_bar_widget = canvas_bar.get_tk_widget()
canvas_bar_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

root.after(0, update_plot)
root.mainloop()
