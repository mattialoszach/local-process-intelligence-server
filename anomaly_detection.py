import psutil
from mcp_instance import mcp

mcp.tool()
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