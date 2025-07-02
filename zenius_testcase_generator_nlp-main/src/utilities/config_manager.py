import os
from typing import Dict, Any
import yaml

def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables and config file.
    Returns a dictionary with configuration settings.
    """
    config = {
        # Ollama settings
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "llama2"),
        
        # MongoDB settings
        "mongodb_uri": os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        "mongodb_database": os.getenv("MONGODB_DATABASE", "ZeniusAITestCaseGenerator"),
        
        # Server settings
        "server_port": int(os.getenv("SERVER_PORT", "8081")),
        "server_host": os.getenv("SERVER_HOST", "0.0.0.0"),
        
        # File upload settings
        "max_file_size": int(os.getenv("MAX_FILE_SIZE", "10485760")),  # 10MB in bytes
        "allowed_file_types": ["pdf", "docx", "txt"],
        
        # Output settings
        "output_directory": os.getenv("OUTPUT_DIRECTORY", "./GeneratedExcelFiles"),
        
        # Template settings
        "template_path": os.getenv("TEMPLATE_PATH", "static/Sample_TestCaseTemplate.xlsx"),
    }
    
    # Load additional settings from config file if it exists
    config_file = os.getenv("CONFIG_FILE", "config.yaml")
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            file_config = yaml.safe_load(f)
            if file_config:
                config.update(file_config)
    
    return config
