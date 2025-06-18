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
    """Returns a high-level summary of the system (OS, CPU, RAM, Disk)."""
    return {
        "os": platform.platform(),
        "cpu": platform.processor(),
        "cpu_count": os.cpu_count(),
        "ram_total_gb": round(psutil.virtual_memory().total / 1e9, 2),
        "disk_total_gb": round(shutil.disk_usage("/").total / 1e9, 2),
        "boot_time": psutil.boot_time()
    }