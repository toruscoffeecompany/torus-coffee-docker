import sys
import os

venv_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
site_packages = os.path.join(venv_root, "Lib", "site-packages")

# Remove Hermes agent paths that leak into subprocess execution
sys.path = [p for p in sys.path if "hermes-agent" not in p]
# Prepend venv site-packages so local dependencies are used
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

from uvicorn.main import run

if __name__ == "__main__":
    run(app="app.main:app", host="127.0.0.1", port=8000, reload=False)
