import psutil
from mcp_instance import mcp

@mcp.tool()
def get_cpu_usage():
    """Returns the current CPU usage in percentage."""
    return {"cpu_percent": psutil.cpu_percent(interval=1)}