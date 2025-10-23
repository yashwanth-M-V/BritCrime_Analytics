import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    db_path: str = "data/crime_data.db"
    backup_path: str = "data/backups/crime_data_backup.db"

@dataclass
class APIConfig:
    base_url: str = "https://data.police.uk/api/"
    timeout: int = 30
    max_retries: int = 3

@dataclass
class ETLConfig:
    police_forces: list = None
    months_to_fetch: int = 12  
    batch_size: int = 50000
    
    def __post_init__(self):
        if self.police_forces is None:
            self.police_forces = ['metropolitan', 'west-midlands', 'greater-manchester']

class Config:
    database = DatabaseConfig()
    api = APIConfig()
    etl = ETLConfig()
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    SQL_DIR = PROJECT_ROOT / "sql"
    LOG_DIR = PROJECT_ROOT / "logs"         # 👈 Added this
    LOG_FILE = LOG_DIR / "etl_pipeline.log" # 👈 And this

    def setup_directories(self):
        """Create necessary directories"""
        self.DATA_DIR.mkdir(exist_ok=True)
        (self.DATA_DIR / "raw").mkdir(exist_ok=True)
        (self.DATA_DIR / "processed").mkdir(exist_ok=True)
        (self.DATA_DIR / "backups").mkdir(exist_ok=True)
        self.SQL_DIR.mkdir(exist_ok=True)
        self.LOG_DIR.mkdir(exist_ok=True)   # 👈 Ensure logs folder exists

# Global config instance
config = Config()
config.setup_directories()
