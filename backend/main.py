import sys
import importlib.util
from pathlib import Path

# Locate ml-service directory
ml_service_dir = Path(__file__).resolve().parent.parent / "ml-service"
sys.path.insert(0, str(ml_service_dir))

# Explicitly load main module from ml-service
spec = importlib.util.spec_from_file_location("ml_service_main", ml_service_dir / "main.py")
ml_module = importlib.util.module_from_spec(spec)
sys.modules["ml_service_main"] = ml_module
spec.loader.exec_module(ml_module)

app = ml_module.app
