# modules/server_monitor.py - Oracle Server Monitoring

import subprocess
import asyncio
from datetime import datetime
from config import ORACLE_HOST, ORACLE_USER, ORACLE_KEY_PATH


def check_server_ping():
    """Ping server and return True if online."""
    try:
        result = subprocess.run(
            ["ping", "-n", "1", ORACLE_HOST],  # Windows: -n, Linux: -c
            capture_output=True, timeout=10
        )
        return result.returncode == 0
    except:
        return False


def run_ssh_command(command):
    """Run a command on Oracle server via SSH."""
    try:
        result = subprocess.run(
            ["ssh", "-i", ORACLE_KEY_PATH, "-o", "StrictHostKeyChecking=no",
             f"{ORACLE_USER}@{ORACLE_HOST}", command],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        return f"SSH error: {e}"


def get_server_status():
    """Get full server status report."""
    if not check_server_ping():
        return "⚠️ Oracle server is OFFLINE or unreachable!"

    status = []
    status.append("✅ Oracle Server Status Report")
    status.append(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    status.append("")

    # CPU usage
    cpu = run_ssh_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
    status.append(f"💻 CPU Usage: {cpu}%")

    # Memory
    mem = run_ssh_command("free -h | grep Mem | awk '{print $3\"/\"$2}'")
    status.append(f"🧠 Memory: {mem}")

    # Disk
    disk = run_ssh_command("df -h / | tail -1 | awk '{print $3\"/\"$2\" (\"$5\" used)\"}'")
    status.append(f"💾 Disk: {disk}")

    # Uptime
    uptime = run_ssh_command("uptime -p")
    status.append(f"⏱️ Uptime: {uptime}")

    # Running services
    services = run_ssh_command("systemctl list-units --type=service --state=running | grep -c running")
    status.append(f"⚙️ Running services: {services}")

    return "\n".join(status)


async def monitor_loop(send_message_func):
    """Background loop that monitors server and sends alerts."""
    server_was_online = True

    while True:
        is_online = check_server_ping()

        if not is_online and server_was_online:
            await send_message_func("🚨 ALERT: Your Oracle server just went OFFLINE!")
            server_was_online = False
        elif is_online and not server_was_online:
            await send_message_func("✅ Your Oracle server is back ONLINE!")
            server_was_online = True

        # Check every 5 minutes
        await asyncio.sleep(300)
