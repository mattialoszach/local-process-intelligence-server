import os
import time
import platform
import psutil
import shutil
from mcp.server.fastmcp import FastMCP

# Create a MCP server
mcp = FastMCP("MCP Local Process Intelligence")

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

@mcp.tool()
def get_cpu_usage():
    """Returns the current CPU usage in percentage."""
    return {"cpu_percent": psutil.cpu_percent(interval=1)}

@mcp.tool()
def get_memory_usage():
    """Returns memory & swap usage (in GB)."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "RAM": {
            "total_gb": round(mem.total / 1e9, 2),
            "used_gb": round(mem.used / 1e9, 2),
            "free_gb": round(mem.available / 1e9, 2),
            "percent": mem.percent
        },
        "SWAP": {
            "total_gb": round(swap.total / 1e9, 2),
            "used_gb": round(swap.used / 1e9, 2),
            "percent": swap.percent
        }
    }

@mcp.tool()
def get_disk_usage():
    """Returns disk usage of the root filesystem."""
    usage = shutil.disk_usage("/")
    return {
        "total_gb": round(usage.total / 1e9, 2),
        "used_gb": round(usage.used / 1e9, 2),
        "free_gb": round(usage.free / 1e9, 2),
        "percent_used": round(usage.used / usage.total * 100, 1)
    }

@mcp.tool()
def get_top_processes(n=10, delay=1.0, include_self: bool = False):
    """
    Returns the top N processes by CPU usage after a short sampling delay.

    Parameters:
    - n (int): Number of processes to return (default: 10)
    - delay (float): Delay in seconds between CPU usage initialization and measurement (default: 0.1)
    - include_self (bool): If False, the current MCP server process (Python) is excluded from the results.

    Notes:
    - The function measures real CPU usage by first initializing CPU counters,
      then waiting for a short delay before collecting values.
    - By default, it excludes the MCP Python process to avoid distortion in rankings.
    - On systems with few logical CPUs, even short Python activity may bias percentages significantly.
    """

    own_pid = os.getpid()

    # Initialize CPU percent calculation
    for p in psutil.process_iter():
        try:
            p.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(delay)

    # Collect process info
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = p.info
            if info['cpu_percent'] is not None:
                if include_self or info['pid'] != own_pid:
                    procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    top = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:n]
    return top

@mcp.tool()
def find_process_by_name(name: str):
    """Returns all processes that match the given name (partial match allowed)."""
    matches = []
    for p in psutil.process_iter(['pid', 'name', 'status']):
        if name.lower() in p.info['name'].lower():
            matches.append(p.info)
    return matches

@mcp.tool()
def get_process_tree(pid: int):
    """Returns the child process tree of a given PID."""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        return {
            "parent": f"{parent.name()} ({pid})",
            "children": [f"{c.name()} ({c.pid})" for c in children]
        }
    except psutil.NoSuchProcess:
        return {"error": f"No process with PID {pid}"}

@mcp.tool()
def detect_spikes(threshold: int = 80):
    """
    Detects if CPU or Memory usage exceeds the specified threshold (%).
    Returns warnings if limits are crossed.
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    mem_percent = mem.percent

    warnings = []
    if cpu_percent > threshold:
        warnings.append(f"High CPU usage detected: {cpu_percent:.1f}%")
    if mem_percent > threshold:
        warnings.append(f"High Memory usage detected: {mem_percent:.1f}%")

    return {
        "cpu_percent": cpu_percent,
        "memory_percent": mem_percent,
        "threshold": threshold,
        "warnings": warnings if warnings else ["System usage normal."]
    }

@mcp.tool()
def analyze_process_anomalies():
    """
    Analyzes processes for suspicious patterns, such as:
    - Very high memory and 0% CPU (possible leak or hung process)
    - Zombie or defunct processes
    - Unusually high memory usage (>1GB)
    """
    anomalies = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
        try:
            info = proc.info
            mem_info = info.get('memory_info')
            cpu = info.get('cpu_percent')
            status = info.get('status')

            if mem_info:
                mem_mb = mem_info.rss / 1e6  # Resident Set Size in MB
                if mem_mb > 1000 and cpu is not None and cpu < 1:
                    anomalies.append({
                        "pid": info['pid'],
                        "name": info['name'],
                        "issue": f"High memory ({mem_mb:.1f}MB), low CPU ({cpu}%)"
                    })

            if status in ("zombie", "defunct"):
                anomalies.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "issue": f"Zombie/defunct process"
                })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return anomalies if anomalies else ["No anomalies detected."]