import os
import time
import platform
import psutil
import shutil
from mcp_instance import mcp

@mcp.tool()
def get_top_processes(n=10, delay=1.0, include_self: bool = False):
    """
    Return a list of top N processes sorted by CPU usage.

    Args:
        n (int, optional): Number of top processes to return. Defaults to 10.
        delay (float, optional): Sampling delay (in seconds) between CPU usage reads. Defaults to 1.0.
        include_self (bool, optional): Whether to include the MCP server process in results. Defaults to False.

    Returns:
        list of dict: Each dictionary contains:
            - pid (int): Process ID.
            - name (str): Process name.
            - cpu_percent (float): CPU usage percentage.
            - memory_percent (float): Memory usage percentage.

    Notes:
        The function initializes CPU counters and measures usage after a short delay to get meaningful values.
        Excluding the current Python process avoids artificial inflation of CPU usage by the MCP server itself.
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
    """
    Find all currently running processes that match a given name substring.

    Args:
        name (str): Name or partial name to match (case-insensitive).

    Returns:
        list of dict: A list of matching processes with:
            - pid (int): Process ID.
            - name (str): Process name.
            - status (str): Process status (e.g., 'running', 'sleeping').
    """
    matches = []
    for p in psutil.process_iter(['pid', 'name', 'status']):
        if name.lower() in p.info['name'].lower():
            matches.append(p.info)
    return matches

@mcp.tool()
def get_process_tree(pid: int):
    """
    Retrieve the full child process tree for a given parent process ID (PID).

    Args:
        pid (int): Process ID of the parent process.

    Returns:
        dict: A dictionary containing:
            - parent (str): Parent process name and PID.
            - children (list of str): List of child process names and their PIDs.
        If the process is not found, returns:
            - error (str): Error message.
    """
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        return {
            "parent": f"{parent.name()} ({pid})",
            "children": [f"{c.name()} ({c.pid})" for c in children]
        }
    except psutil.NoSuchProcess:
        return {"error": f"No process with PID {pid}"}