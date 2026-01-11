# Email Automation System - Configuration Loader
# Loads environment variables from .env file

import os
from pathlib import Path

def load_env_file(env_path: str = ".env"):
    """Load environment variables from a .env file"""
    env_file = Path(env_path)
    
    if not env_file.exists():
        print(f"Warning: {env_path} not found. Using system environment variables.")
        return
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse key=value
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove surrounding quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                os.environ[key] = value

# Auto-load .env file when this module is imported
load_env_file()
