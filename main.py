import tkinter as tk
from tkinter import messagebox
from Dashboard import MainApplication
from MetricsClient import MetricsClient
import json

def test_connections(servers):
    """Test connections to all servers before starting dashboard"""
    client = MetricsClient(servers)
    results = client.get_current_metrics()
    
    status = {}
    for name, data in results.items():
        if data is None:
            status[name] = False
            print(f"Failed to connect to {name}")
        else:
            try:
                # Verify JSON structure
                required_fields = ["time", "cpu", "memory", "io", "filesystem", "load"]
                if all(field in data for field in required_fields):
                    status[name] = True
                    print(f"Successfully connected to {name}")
                    print(f"Current metrics: {json.dumps(data, indent=2)}")
                else:
                    status[name] = False
                    print(f"Missing required fields in response from {name}")
            except Exception as e:
                status[name] = False
                print(f"Error processing data from {name}: {e}")
    
    return status

def main():
    # Server configurations
    SERVERS = {
        "Server Connor": "34.56.72.213", 
        "Server Tirth": "34.122.192.54",  
        "Server Piash": "35.222.69.252"    
    }

    # Test connections first
    connection_status = test_connections(SERVERS)
    
    # Initialize main window
    root = tk.Tk()
    
    # Show connection status
    if not any(connection_status.values()):
        messagebox.showerror("Connection Error", "Could not connect to any servers!")
        root.destroy()
        return
    
    # Create and start dashboard
    app = MainApplication(root, SERVERS)
    
    # Update UI to show initial connection status
    for server_name, connected in connection_status.items():
        if not connected:
            dashboard = app.dashboards.get(server_name)
            if dashboard:
                dashboard.ax.set_facecolor('red')
                dashboard.canvas.draw()
    
    # Start update cycle
    app.update_all()
    root.mainloop()

if __name__ == "__main__":
    main()