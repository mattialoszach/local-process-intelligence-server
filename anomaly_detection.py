import psutil
from mcp_instance import mcp

mcp.tool()
def detect_spikes(threshold: int = 80):
    """
    Detect CPU or memory usage spikes that exceed a specified percentage threshold.

    Args:
        threshold (int, optional): The usage percentage threshold (0–100) above which a warning is triggered.
                                   Defaults to 80, but it can be adjusted.

    Returns:
        dict: A dictionary containing:
            - cpu_percent (float): Current CPU usage in percentage.
            - memory_percent (float): Current memory usage in percentage.
            - threshold (int): The threshold value used for detection.
            - warnings (list of str): List of warning messages if any usage exceeds the threshold.
                                      Returns ['System usage normal.'] if no issues are found.
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
    Analyze currently running processes for common anomalies, including:

    - High memory usage (>1000 MB) combined with near-zero CPU usage (possible memory leak or stalled process)
    - Zombie or defunct processes

    Returns:
        list: A list of anomaly reports, each as a dictionary with:
            - pid (int): Process ID.
            - name (str): Process name.
            - issue (str): Description of the detected anomaly.
        If no anomalies are found, returns a single-item list: ['No anomalies detected.']
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