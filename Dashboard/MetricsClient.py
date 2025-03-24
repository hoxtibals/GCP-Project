import requests
from datetime import datetime
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import json

class MetricsClient:
    def __init__(self, servers_dict):
        """Initialize with dictionary of server names and IPs"""
        self.servers = servers_dict
        self.port = 5000
        
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

    def get_current_metrics(self):
        """Get current metrics from all servers"""
        results = {}
        for name, ip in self.servers.items():
            try:  
                url = f"http://{ip}:{self.port}"
                response = self.session.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                results[name] = data
                
                response.close()
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to {name}: {e}")
                results[name] = None
            except json.JSONDecodeError as e:
                print(f"Invalid JSON from {name}: {e}")
                results[name] = None
        return results

    def get_history(self, start_time):
        """Get history from all servers for given time"""
        results = {}
        for name, ip in self.servers.items():
            try:
                url = f"http://{ip}:{self.port}/history?time={start_time}"
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                results[name] = response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error getting history from {name}: {e}")
                results[name] = None
        return results
    
    
    def __del__(self):
        """Cleanup session on object destruction"""
        if hasattr(self, 'session'):
            self.session.close()

# Test the client
if __name__ == "__main__":
    test_servers = {
        "Server Connor": "FIRST_GCP_IP",
        "Server Tirth": "SECOND_GCP_IP",
        "Server Piash": "THIRD_GCP_IP"
    }
    
    client = MetricsClient(test_servers)
    
    # Test current metrics
    current = client.get_current_metrics()
    print("Current metrics:", json.dumps(current, indent=2))
    
    # Test history
    history = client.get_history("10:00")
    print("History:", json.dumps(history, indent=2))