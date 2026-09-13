"""Initialize a mounted data volume, then run the service as the unprivileged user."""
import os
from pathlib import Path
root = Path(os.environ.get("BAYAN_DATA", "/data"))
root.mkdir(parents=True, exist_ok=True)
if os.geteuid() == 0:
    os.chown(root, 10001, 10001)
    os.setgroups([])
    os.setgid(10001)
    os.setuid(10001)
os.execvp("python", ["python", "/app/worker.py"])
