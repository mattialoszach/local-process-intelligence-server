import os
import time
import platform
import psutil
import shutil
from mcp_instance import mcp

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