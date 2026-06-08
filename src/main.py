import os
import sys
import warnings
import numpy as np
import scipy.io.wavfile as wav
from mosqito.sq_metrics import loudness_zwtv, sharpness_din_tv, roughness_dw

# =============================================================================
# CUSTOM MODULES IMPORTS
# =============================================================================
from logger_init import logger
from pdf_generator import generate_acoustic_report

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Mute repetitive MOSQITO resampling warnings in the terminal
warnings.filterwarnings("ignore", category=UserWarning, module="mosqito")

# =============================================================================
# CONFIGURATION ROOT PATH
# =============================================================================
BASE_RESOURCES_DIR = os.getenv("AUDIO_RESOURCES_DIR", "./data/ressources")
OUTPUT_PDF_DIR = "./data/analysis"

if not os.path.exists(BASE_RESOURCES_DIR):
    logger.error(f"The root resources directory '{BASE_RESOURCES_DIR}' does not exist.")
    sys.exit(1)

# Retrieve all sub-directories inside data/ressources/
all_folders = [f for f in os.listdir(BASE_RESOURCES_DIR) if os.path.isdir(os.path.join(BASE_RESOURCES_DIR, f))]
all_folders.sort()  # Sort alphanumerically (Category A, B, C...)

if not all_folders:
    logger.warning(f"No directories found inside '{BASE_RESOURCES_DIR}'. Checking if base folder itself contains audio...")
    # Fallback to current directory as a single folder name if no subfolders exist
    all_folders = ["."]

logger.info(f"Multi-directory scan started. Found {len(all_folders)} target folder(s) inside '{BASE_RESOURCES_DIR}'.")
print("=" * 60)

# Master structure to store data for all folders
# Format: { 'A': { 'files': [...], 'average_pa': 14.5 }, 'B': ... }
all_folders_data = {}
all_global_pa_scores = []

# =============================================================================
# MASTER DIRECTORY LOOP
# =============================================================================
for folder_name in all_folders:
    current_folder_path = os.path.join(BASE_RESOURCES_DIR, folder_name) if folder_name != "." else BASE_RESOURCES_DIR
    
    # List wav files inside this specific sub-folder
    audio_files = [f for f in os.listdir(current_folder_path) if f.lower().endswith('.wav')]
    audio_files.sort()
    
    if not audio_files:
        logger.warning(f"Skipping folder '{folder_name}': No .wav file specimens found.")
        continue
        
    logger.info(f">>> ENTERING FOLDER [Category {folder_name}] — Found {len(audio_files)} files.")
    print("-" * 50)
    
    folder_files_data = []
    folder_pa_scores = []
    
    # --- Inside loop file by file analysis ---
    for filename in audio_files:
        file_path = os.path.join(current_folder_path, filename)
        logger.info(f"Processing ({folder_name}): {filename} ...")
        
        try:
            # 1. Load and preparation
            fs, signal = wav.read(file_path)
            if signal.ndim == 2:
                signal = signal.mean(axis=1)
            signal = signal.astype(np.float32) / np.iinfo(np.int16).max
            
            # 2. Extract metrics
            N, _, _, _ = loudness_zwtv(signal, fs, field_type="free")
            N_5 = np.percentile(N, 95)
            
            S, _ = sharpness_din_tv(signal, fs, skip=0.2)
            S_mean = np.mean(S)
            
            R, _, _, _ = roughness_dw(signal, fs)
            R_mean = np.mean(R)
            
            # 3. Compute Annoyance Score (PA)
            w_S = (S_mean - 1.75) * np.log(N_5 + 2) if S_mean > 1.75 else 0
            w_FR = np.sqrt((0.3 * R_mean) ** 2)
            psychoacoustic_annoyance = N_5 * (1 + np.sqrt(w_S**2 + w_FR**2))
            
            folder_pa_scores.append(psychoacoustic_annoyance)
            all_global_pa_scores.append(psychoacoustic_annoyance)
            
            folder_files_data.append({
                "filename": filename,
                "loudness": N_5,
                "sharpness": S_mean,
                "roughness": R_mean,
                "annoyance": psychoacoustic_annoyance
            })
            
        except Exception as e:
            logger.error(f"Error while processing file {filename} in folder {folder_name}: {e}", exc_info=True)
            
    # Compute this directory's performance average
    if folder_pa_scores:
        folder_avg_pa = np.mean(folder_pa_scores)
        logger.info(f"<<< FINISHED FOLDER [Category {folder_name}] — Mean Annoyance Score: {folder_avg_pa:.2f}")
        
        # Save metrics under the master dictionary database structure
        all_folders_data[folder_name] = {
            "files": folder_files_data,
            "average_pa": folder_avg_pa
        }
    print("=" * 60)

# =============================================================================
# COMPILE CROSS-CATEGORY VALIDATION AND EXPORT REPORT
# =============================================================================
if all_global_pa_scores:
    global_comprehensive_average = np.mean(all_global_pa_scores)
    
    logger.info("=== COMPREHENSIVE MULTI-DIRECTORY RESULTS ===")
    logger.info(f"Total processed folders : {len(all_folders_data)}")
    logger.info(f"Total analyzed audio volumes : {len(all_global_pa_scores)}")
    logger.info(f"GLOBAL COMPREHENSIVE AVERAGE SCORE (PA) : {global_comprehensive_average:.2f}")
    print("-" * 60)
    
    # Execute the layout mapping and hand off data to PDF generator module
    generate_acoustic_report(
        all_folders_data=all_folders_data,
        global_average=global_comprehensive_average,
        base_resources_dir=BASE_RESOURCES_DIR,
        output_dir=OUTPUT_PDF_DIR
    )
else:
    logger.warning("No audio volumes could be parsed from any target subfolder. Process aborted.")