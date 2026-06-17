import os
import sys
from logger_init import logger

# =============================================================================
# CUSTOM MODULES IMPORTS
# =============================================================================
from logger_init import logger
from run import execute_analysis

# =============================================================================
# CONFIGURATION ROOT PATH
# =============================================================================
BASE_RESOURCES_DIR = os.getenv("AUDIO_RESOURCES_DIR", "./data/input")
OUTPUT_PDF_DIR = "./data/output"

def check_parameters():
    if not os.path.exists(BASE_RESOURCES_DIR):
        logger.error(f"The root resources directory '{BASE_RESOURCES_DIR}' does not exist.")
        sys.exit(1)
    

if __name__ == "__main__":

    # Step 1: Check parameters and environment setup
    check_parameters()
    execute_analysis(BASE_RESOURCES_DIR, OUTPUT_PDF_DIR)