import os
import platform
import psutil
import shutil
from mcp_instance import mcp
from cpu_monitor import get_cpu_usage
from memory_monitor import get_memory_usage, get_disk_usage
from process_monitor import get_top_processes, find_process_by_name, get_process_tree
from anomaly_detection import detect_spikes, analyze_process_anomalies

@mcp.tool()
def get_system_summary():
    """
    Retrieve a high-level summary of the current system's key hardware and OS details.

    Returns:
        dict: A dictionary containing:
            - os (str): Human-readable platform identifier (e.g., 'macOS-13.5-arm64').
            - cpu (str): CPU name or identifier string.
            - cpu_count (int): Number of logical CPU cores.
            - ram_total_gb (float): Total RAM in gigabytes.
            - disk_total_gb (float): Total disk capacity in gigabytes (root partition).
            - boot_time (float): System boot time as a Unix timestamp.
    """
    return {
        "os": platform.platform(),
        "cpu": platform.processor(),
        "cpu_count": os.cpu_count(),
        "ram_total_gb": round(psutil.virtual_memory().total / (2**30), 2),
        "disk_total_gb": round(shutil.disk_usage("/").total / 1e9, 2),
        "boot_time": psutil.boot_time()
    }

if __name__ == "__main__":
    print(get_system_summary())