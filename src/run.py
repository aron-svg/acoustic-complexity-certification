import glob
import multiprocessing
import numpy as np
import os
import scipy.io.wavfile as wav
from mosqito.sq_metrics import loudness_zwtv, sharpness_din_tv, roughness_dw
from logger_init import logger
from pdf_generator import generate_acoustic_report
from pathlib import Path

def analyze_audio_file(wav_path, folder_name, folder_files_data, folder_pa_scores, all_global_pa_scores):
    
    try:
        filename = os.path.basename(wav_path)
        # 1. Load and preparation
        fs, signal = wav.read(wav_path)
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
        
        return folder_files_data, folder_pa_scores
    except Exception as e:
        logger.error(f"Error while processing file {filename} in folder {folder_name}: {e}", exc_info=True)
        

def process_wav_file(wav_path):
    folder_name = os.path.basename(os.path.dirname(wav_path))
    result = analyze_audio_file(
        wav_path=wav_path,
        folder_name=folder_name,
        folder_files_data=[],
        folder_pa_scores=[],
        all_global_pa_scores=[]
    )
    if result is None:
        return None
    folder_files_data, folder_pa_scores = result
    return folder_name, folder_files_data, folder_pa_scores


def execute_analysis(BASE_RESOURCES_DIR, OUTPUT_PDF_DIR):
    
    folder_path = Path(BASE_RESOURCES_DIR)

    list_of_wav_files = glob.glob(BASE_RESOURCES_DIR + "/**/*.wav", recursive=True)

    max_cpu = multiprocessing.cpu_count()
    logger.info(f"Total .wav files input found in '{BASE_RESOURCES_DIR}': {len(list_of_wav_files)}")
    logger.info(f"CPU cores available: {max_cpu}")

    # Master structure to store data for all folders
    # Format: { 'A': { 'files': [...], 'average_pa': 14.5 }, 'B': ... }
    all_folders_data = {}
    all_global_pa_scores = []

    with multiprocessing.Pool(processes=max_cpu) as pool:
        results = pool.map(process_wav_file, list_of_wav_files)

    for result in results:
        if result is None:
            continue
        folder_name, folder_files_data, folder_pa_scores = result
        all_global_pa_scores.extend(folder_pa_scores)
        if folder_pa_scores:
            folder_avg_pa = np.mean(folder_pa_scores)
            logger.info(f"<<< FINISHED FOLDER [Category {folder_name}] — Mean Annoyance Score: {folder_avg_pa:.2f}")
            all_folders_data[folder_name] = {
                "files": folder_files_data,
                "average_pa": folder_avg_pa
            }

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
