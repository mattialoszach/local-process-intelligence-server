import psutil
import shutil
from mcp_instance import mcp

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