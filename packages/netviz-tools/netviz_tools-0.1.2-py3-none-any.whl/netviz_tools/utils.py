"""
Utilities for the netviz_tools package.

This module provides constants and configurations used throughout the netviz_tools package.

Constants include:
- CONTINENT_COLORS: A dictionary mapping continents to their respective colors for visualizations.
- PACKAGE_DIR: The directory where the package is located.
- DATA_DIR: The directory where data files are stored.
- LOG_DIR: The directory where log files are stored.
- LOG_FILE: The path to the log file for the package.
"""

from pathlib import Path

# Color mapping for continents in visualizations
CONTINENT_COLORS: dict[str, str] = {
    "Africa": "red",
    "Asia": "green",
    "Europe": "blue",
    "Northern America": "purple",
    "Oceania": "orange",
    "South America": "pink",
    "Central America": "cyan",
    "Caribbean": "brown",
}

# Constants
PACKAGE_DIR: Path = Path(__file__).parent
DATA_DIR: Path = PACKAGE_DIR / "data"
LOG_DIR: Path = PACKAGE_DIR / "logs"
LOG_FILE: Path = LOG_DIR / "netviz_tools.log"


# Verify directories exist and log file is created
def directory_setup():
    """Ensure necessary directories exist and log file is created."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.touch()
