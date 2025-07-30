# tests\test_test.py

from pathlib import Path
from toml_init.manager import ConfigManager



# Initialize and validate
cm = ConfigManager(
    base_path=Path("configs"),
    defaults_path=Path("configs/defaults"),
    master_filename="config.toml"
)
cm.initialize()

# Access validated settings
settings = cm.get_block("QuickBooks.Invoices.Saver")
print(settings["WINDOW_LOAD_DELAY"])  # e.g. 0.5