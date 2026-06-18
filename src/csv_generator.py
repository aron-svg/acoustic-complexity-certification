#!/usr/bin/env python
import csv
import os
from datetime import datetime
from logger_init import logger

def generate_acoustic_csv(all_folders_data, global_average, base_resources_dir, output_dir="./data/analysis"):
    """
    Exports acoustic certification data to a flat CSV file.

    :param all_folders_data: Dict of folder names mapping to a dict with 'files' list and 'average_pa' float.
    :param global_average: Float representing the combined average across all directories.
    :param base_resources_dir: Path of the root resources directory.
    :param output_dir: Destination path where the CSV will be saved.
    """
    logger.info("Initializing CSV acoustic report generation...")

    if not all_folders_data:
        logger.warning("No multi-folder data discovered. Aborting CSV export.")
        return

    try:
        os.makedirs(output_dir, exist_ok=True)
        csv_filename = f"global_acoustic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output_csv_path = os.path.join(output_dir, csv_filename)

        with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)

            writer.writerow(["Category", "Sample ID", "Loudness (sone)", "Sharpness (acum)", "Roughness (asper)", "Annoyance (PA)"])

            for folder_name, data in all_folders_data.items():
                for row in data["files"]:
                    writer.writerow([
                        folder_name,
                        row["filename"],
                        f"{row['loudness']:.2f}",
                        f"{row['sharpness']:.2f}",
                        f"{row['roughness']:.2f}",
                        f"{row['annoyance']:.2f}",
                    ])

                writer.writerow([
                    f"AVERAGE — {folder_name}",
                    "",
                    "",
                    "",
                    "",
                    f"{data['average_pa']:.2f}",
                ])

            writer.writerow([])
            writer.writerow(["GLOBAL COMPREHENSIVE AVERAGE", "", "", "", "", f"{global_average:.2f}"])

        logger.info(f"Successfully exported CSV acoustic report to: {output_csv_path}")

    except Exception as e:
        logger.error(f"Critical error whilst creating CSV report: {e}", exc_info=True)
