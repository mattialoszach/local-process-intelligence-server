import psutil
from mcp_instance import mcp

@mcp.tool()
def get_cpu_usage():
    """
    Measure the current CPU usage as a percentage of total processing capacity.

    Returns:
        dict: A dictionary containing:
            - cpu_percent (float): CPU usage over a 1-second interval, as a percentage (0.0–100.0).
    """
    return {"cpu_percent": psutil.cpu_percent(interval=1)}