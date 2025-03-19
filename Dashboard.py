import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from MetricsClient import MetricsClient
import time


# Thresholds and colors
THRESHOLDS = {
    "CPU": {"warn": 70.0, "critical": 80.0},
    "Memory": {"warn": 65.0, "critical": 75.0},
    "Disk": {"warn": 70.0, "critical": 80.0},
    "Network": {"warn": 8.0, "critical": 10.0},
    "Load": {"warn": 1.5, "critical": 2.0}
}

def get_metric_color(value, metric):
    if value >= THRESHOLDS[metric]["critical"]:
        return "red"
    elif value >= THRESHOLDS[metric]["warn"]:
        return "orange"
    return "blue"

class ServerDashboard:
    def __init__(self, root, server_name, server_ip):
        self.frame = ttk.LabelFrame(root, text=server_name)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.client = MetricsClient({server_name: server_ip})
        self.server_name = server_name
        self.metric_var = tk.StringVar(value="CPU")
        
        self.setup_ui()
        self.data = {metric: [] for metric in ["CPU", "Memory", "Disk", "Network", "Load"]}
        self.x_data = []
        self.start_time = time.time()

    def setup_ui(self):
        # Radio buttons for metrics
        for m in ["CPU", "Memory", "Disk", "Network", "Load"]:
            r = ttk.Radiobutton(self.frame, text=m, variable=self.metric_var, value=m)
            r.pack(side=tk.TOP, padx=5)

        # Setup matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(4, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update(self):
        try:
            stats = self.client.get_current_metrics()
            server_stats = stats.get(self.server_name)
            
            if server_stats and isinstance(server_stats, dict):
                current_time = time.time() - self.start_time
                self.x_data.append(current_time)
                
                # Update data for each metric with safe access
                try:
                    metric_mapping = {
                        "CPU": float(server_stats.get("cpu", "0%").strip('%')),
                        "Memory": float(server_stats.get("memory", "0/0 MB (0%)").split('(')[1].strip('%)')),
                        "Disk": float(server_stats.get("filesystem", "0%").strip('%')),
                        "Network": float(server_stats.get("io", "0")),
                        "Load": float(server_stats.get("load", "0"))
                    }
                    
                    for metric, value in metric_mapping.items():
                        self.data[metric].append(value)

                    # Update plot
                    selected = self.metric_var.get()
                    current_value = self.data[selected][-1]
                    
                    self.ax.clear()
                    bar_color = get_metric_color(current_value, selected)
                    self.ax.bar([selected], [current_value], color=bar_color)
                    self.ax.set_ylabel(f"{selected} Value")
                    self.ax.set_ylim(0, 100 if selected != "Load" else 5)
                    self.canvas.draw()
                
                except (ValueError, KeyError, IndexError) as e:
                    print(f"Error processing metrics for {self.server_name}: {e}")
                    self.ax.set_facecolor('red')
                    self.canvas.draw()
            else:
                print(f"No valid data for {self.server_name}")
                self.ax.set_facecolor('red')
                self.canvas.draw()
                
        except Exception as e:
            print(f"Update failed for {self.server_name}: {e}")
            self.ax.set_facecolor('red')
            self.canvas.draw()

class MainApplication:
    def __init__(self, root, servers_dict):
        self.root = root
        self.root.title("Multi-Server Performance Dashboard")
        self.root.geometry("1800x600")
        
        self.dashboards = {}
        for server_name, server_ip in servers_dict.items():
            self.dashboards[server_name] = ServerDashboard(root, server_name, server_ip)
    
    def update_all(self):
        for dashboard in self.dashboards.values():
            dashboard.update()
        self.root.after(6000, self.update_all)  # Update every 6 seconds

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    app.update_all()
    root.mainloop()