import tkinter as tk
from tkinter import messagebox, ttk
from Dashboard.Dashboard import MainApplication
from MetricsClient import MetricsClient
import json

class ConfigWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dashboard Configuration")
        self.root.geometry("400x500")
        
        # Server inputs
        self.server_entries = []
        
        # Server section
        ttk.Label(self.root, text="Server Configuration", 
                 font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        for i, default_ip in enumerate([
            "0.0.0.0", "0.0.0.0", "0.0.0.0"
        ]):
            frame = ttk.LabelFrame(self.root, text=f"Server {i+1}")
            frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
            name_entry = ttk.Entry(frame)
            name_entry.insert(0, f"Server {i+1}")
            name_entry.grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(frame, text="IP:").grid(row=1, column=0, padx=5, pady=5)
            ip_entry = ttk.Entry(frame)
            ip_entry.insert(0, default_ip)
            ip_entry.grid(row=1, column=1, padx=5, pady=5)
            
            self.server_entries.append((name_entry, ip_entry))
        
        ttk.Label(self.root, text="Threshold Configuration", 
                 font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        threshold_frame = ttk.Frame(self.root)
        threshold_frame.pack(fill="x", padx=10)
        """     
        #default thresholds
        DEFAULT_THRESHOLDS = {
    "CPU": {"warn": 70.0, "critical": 80.0},
    "Memory": {"warn": 65.0, "critical": 75.0},
    "Disk": {"warn": 70.0, "critical": 80.0},
    "Network": {"warn": 8.0, "critical": 10.0},
    "Load": {"warn": 1.5, "critical": 2.0}
    }"""
        
        ttk.Label(threshold_frame, text="Warning (CPU, MEM, DISK 0.0-99.9):").grid(row=0, column=0, padx=5, pady=5)
        self.warn_entry = ttk.Entry(threshold_frame)
        self.warn_entry.insert(0, "70.0")
        self.warn_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(threshold_frame, text="Critical (CPU, MEM, DISK 0.0-99.9):").grid(row=1, column=0, padx=5, pady=5)
        self.crit_entry = ttk.Entry(threshold_frame)
        self.crit_entry.insert(0, "80.0")
        self.crit_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(threshold_frame, text="Warning (NETWORK 8.0-10.0):").grid(row=0, column=2, padx=5, pady=5)
        self.warn_entry = ttk.Entry(threshold_frame)
        self.warn_entry.insert(0, "8.6")
        self.warn_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(threshold_frame, text="Critical (NETWORK 8.0-1.0):").grid(row=1, column=2, padx=5, pady=5)
        self.crit_entry = ttk.Entry(threshold_frame)
        self.crit_entry.insert(0, "9.0")
        self.crit_entry.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(threshold_frame, text="Warning (LOAD 1.5-2.0):").grid(row=0, column=4, padx=5, pady=5)
        self.warn_entry = ttk.Entry(threshold_frame)
        self.warn_entry.insert(0, "1.55")
        self.warn_entry.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(threshold_frame, text="Critical (LOAD 1.5-2.0):").grid(row=1, column=4, padx=5, pady=5)
        self.crit_entry = ttk.Entry(threshold_frame)
        self.crit_entry.insert(0, "1.7")
        self.crit_entry.grid(row=1, column=5, padx=5, pady=5)
        
        ttk.Button(self.root, text="Start Dashboard", 
                  command=self.start_dashboard).pack(pady=20)
        
        self.servers_dict = None
        self.thresholds = None
    
    def start_dashboard(self):
        #Validate and collect configurations
        self.servers_dict = {}
        for name_entry, ip_entry in self.server_entries:
            name = name_entry.get().strip()
            ip = ip_entry.get().strip()
            if name and ip:
                self.servers_dict[name] = ip
        
        if not self.servers_dict:
            messagebox.showerror("Error", "At least one server must be configured")
            return
            
        try:
            warn = float(self.warn_entry.get())
            crit = float(self.crit_entry.get())
            if warn >= crit:
                raise ValueError("Warning threshold must be less than critical")
            self.thresholds = {"warn": warn, "critical": crit}
            self.root.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))




def main():
    # Server configurations
    config = ConfigWindow()
    config.root.mainloop()

    #fail start
    if not config.servers_dict:
        return
    
    # Initialize main window
    root = tk.Tk()
    
    # Show connection status
    if not any(config.servers_dict.values()):
        messagebox.showerror("Connection Error", "Could not connect to any servers!")
        root.destroy()
        return
    
    # Create and start dashboard
    app = MainApplication(root, config.servers_dict)
    
    # Update UI to show initial connection status
    for server_name in config.servers_dict.items():
        dashboard = app.dashboards.get(server_name)
        if dashboard:
            dashboard.ax.set_facecolor('red')
            dashboard.canvas.draw()
    
    # Start update cycle
    app.update_all()
    root.mainloop()

if __name__ == "__main__":
    main()