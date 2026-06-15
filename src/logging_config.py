#!/usr/bin/env python
import logging
import logging.config
import os
import sys
import yaml
import warnings

# =============================================================================
# FORMATTER COULEUR COMPATIBLE YAML
# =============================================================================
class ColoredFormatter(logging.Formatter):
    CLR_RESET = "\033[0m"
    CLR_BLUE = "\033[36m"     # Bleu cyan très lisible
    CLR_YELLOW = "\033[33m"   # Jaune
    CLR_RED = "\033[31m"      # Rouge

    def format(self, record):
        orig_levelname = record.levelname
        if record.levelno == logging.INFO:
            record.levelname = f"{self.CLR_BLUE}{record.levelname:8s}{self.CLR_RESET}"
        elif record.levelno == logging.WARNING:
            record.levelname = f"{self.CLR_YELLOW}{record.levelname:8s}{self.CLR_RESET}"
        elif record.levelno == logging.ERROR or record.levelno == logging.CRITICAL:
            record.levelname = f"{self.CLR_RED}{record.levelname:8s}{self.CLR_RESET}"
        else:
            record.levelname = f"{record.levelname:8s}"
            
        result = super().format(record)
        record.levelname = orig_levelname
        return result

# On enregistre officiellement notre nouveau style pour que le YAML puisse le reconnaître
logging.ColoredFormatter = ColoredFormatter

# Formatter par défaut de secours
default_formatter = ColoredFormatter(
    "%(asctime)s | %(levelname)s |  %(funcName)s | %(message)s",
    "%Y-%m-%d %H:%M:%S",
)

__logger = logging.getLogger(__name__)
__ch = logging.StreamHandler(sys.stdout)
__ch.setFormatter(default_formatter)
__logger.addHandler(__ch)

if not os.path.exists("logs"):
    os.makedirs("logs")

__logger_config_file = "logger_config.yaml"
if os.path.exists(__logger_config_file) and os.path.isfile(__logger_config_file):
    try:
        # Utilisation de 'with' pour fermer proprement le fichier et éliminer le ResourceWarning
        with open(__logger_config_file, "r") as f:
            log_cfg = yaml.safe_load(f)
        logging.config.dictConfig(log_cfg)
    except Exception as ex:
        __logger.error(f"Unexpected error whilst reading logger configuration file {__logger_config_file}")
        __logger.error(f"Exception: {ex}")
        raise
else:
    __logger.warning(f"no configuration file {__logger_config_file} found, using default setting")
    
# Mute repetitive MOSQITO resampling warnings in the terminal
warnings.filterwarnings("ignore", category=UserWarning, module="mosqito")
