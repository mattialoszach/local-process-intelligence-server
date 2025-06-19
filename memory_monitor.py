import psutil
import shutil
from mcp_instance import mcp

@mcp.tool()
def get_memory_usage():
    """
    Retrieve current RAM and swap memory usage.

    Returns:
        dict: A dictionary containing:
            - RAM (dict):
                - total_gb (float): Total physical memory in GB.
                - used_gb (float): Used memory in GB.
                - free_gb (float): Available memory in GB.
                - percent (float): Percentage of RAM used.
            - SWAP (dict):
                - total_gb (float): Total swap space in GB.
                - used_gb (float): Used swap space in GB.
                - percent (float): Percentage of swap space used.
    """
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
    """
    Retrieve disk usage statistics of the root ("/") filesystem.

    Returns:
        dict: A dictionary containing:
            - total_gb (float): Total disk capacity in GB.
            - used_gb (float): Used disk space in GB.
            - free_gb (float): Free disk space in GB.
            - percent_used (float): Percentage of disk space used.
    """
    usage = shutil.disk_usage("/")
    return {
        "total_gb": round(usage.total / 1e9, 2),
        "used_gb": round(usage.used / 1e9, 2),
        "free_gb": round(usage.free / 1e9, 2),
        "percent_used": round(usage.used / usage.total * 100, 1)
    }