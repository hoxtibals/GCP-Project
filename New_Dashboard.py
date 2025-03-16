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
    Expects a JSON object like:
    {
      "cpu": 32.5,
      "mem": 45.0,
      "disk": 20.1,
      "network": 1.25,
      "load": 0.85
    }
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

        # Update the data for each of the five lines.
        line_cpu.set_xdata(x_data)
        line_cpu.set_ydata(cpu_data)

        line_mem.set_xdata(x_data)
        line_mem.set_ydata(mem_data)

        line_disk.set_xdata(x_data)
        line_disk.set_ydata(disk_data)

        line_net.set_xdata(x_data)
        line_net.set_ydata(net_data)

        line_load.set_xdata(x_data)
        line_load.set_ydata(load_data)

        # Basic threshold checks and color changes
        # (Uses the latest data point for color logic)
        if cpu_data[-1] > CPU_THRESHOLD:
            line_cpu.set_color("red")
        else:
            line_cpu.set_color("blue")

        if mem_data[-1] > MEM_THRESHOLD:
            line_mem.set_color("red")
        else:
            line_mem.set_color("green")

        if disk_data[-1] > DISK_THRESHOLD:
            line_disk.set_color("red")
        else:
            line_disk.set_color("orange")

        if net_data[-1] > NET_THRESHOLD:
            line_net.set_color("red")
        else:
            line_net.set_color("purple")

        if load_data[-1] > LOAD_THRESHOLD:
            line_load.set_color("red")
        else:
            line_load.set_color("brown")

    # Determine which metric is selected, and show/hide lines accordingly.
    selected = metric_var.get()
    line_cpu.set_visible(selected == "CPU")
    line_mem.set_visible(selected == "Memory")
    line_disk.set_visible(selected == "Disk")
    line_net.set_visible(selected == "Network")
    line_load.set_visible(selected == "Load")

    # Recalculate axis limits & redraw
    ax.relim()
    ax.autoscale_view()
    canvas.draw()

    # Schedule the next update
    root.after(2000, update_plot)  

root = tk.Tk()
root.title("Server Performance Dashboard")
root.geometry("1200x800")  

# Create a frame to hold the radio buttons for choosing the metric
options_frame = ttk.Frame(root)
options_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

metric_var = tk.StringVar(value="CPU")

# Create radio buttons for each metric
metrics = ["CPU", "Memory", "Disk", "Network", "Load"]
for m in metrics:
    r = ttk.Radiobutton(options_frame, text=m, variable=metric_var, value=m)
    r.pack(side=tk.LEFT, padx=5)

# Create a figure and axis for plotting
fig, ax = plt.subplots()
ax.set_xlabel("Time (s)")
ax.set_ylabel("Metric Value")

# Create lines for each metric (all on the same axis initially).
line_cpu, = ax.plot([], [], label="CPU Usage", color="blue")
line_mem, = ax.plot([], [], label="Memory Usage", color="green")
line_disk, = ax.plot([], [], label="Disk Usage", color="orange")
line_net, = ax.plot([], [], label="Network Usage", color="purple")
line_load, = ax.plot([], [], label="Load Average", color="brown")

ax.legend(loc="upper left")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

root.after(0, update_plot)
root.geometry("1200x1200")  

root.mainloop()
