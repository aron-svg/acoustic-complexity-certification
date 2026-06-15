#!/usr/bin/env python
import os
from datetime import datetime
from xhtml2pdf import pisa
from logger_init import logger

def generate_acoustic_report(all_folders_data, global_average, base_resources_dir, output_dir="./data/analysis"):
    """
    Generates a corporate multi-folder certification PDF report using xhtml2pdf.
    Presents each folder's samples in distinct tables and concludes with a global directory summary.
    Optimized to bypass xhtml2pdf @page nesting limitations.
    
    :param all_folders_data: Dict of folder names mapping to a dict with 'files' list and 'average_pa' float.
    :param global_average: Float representing the combined average across all directories.
    :param base_resources_dir: Path of the root ressources directory.
    :param output_dir: Destination path where the PDF will be saved.
    """
    logger.info("Initializing native xhtml2pdf multi-folder PDF report generation...")
    
    if not all_folders_data:
        logger.warning("No multi-folder data discovered. Aborting layout construction.")
        return

    # Determine global status categorization based on global average
    if global_average < 12:
        interpretation = "Low Nuisance / Tolerable"
        badge_style = "background-color: #def7ec; color: #03543f;"
    elif global_average < 25:
        interpretation = "Moderate to Significant"
        badge_style = "background-color: #fde8e8; color: #9b1c1c;"
    else:
        interpretation = "High to Critical Nuisance"
        badge_style = "background-color: #fde8e8; color: #9b1c1c;"

    try:
        # 1. Build distinct HTML sections for EACH folder dynamically
        folder_sections_html = ""
        for folder_name, data in all_folders_data.items():
            
            # Build individual rows for the files inside this folder
            table_rows_html = ""
            for row in data['files']:
                table_rows_html += f"""
                <tr>
                    <td>{row['filename']}</td>
                    <td class="text-right">{row['loudness']:.2f}</td>
                    <td class="text-right">{row['sharpness']:.2f}</td>
                    <td class="text-right">{row['roughness']:.2f}</td>
                    <td class="text-right highlighted-cell">{row['annoyance']:.2f}</td>
                </tr>
                """
            
            # Append the completed table structure for this specific folder
            folder_sections_html += f"""
            <div class="folder-section">
                <h2>Experimental Data Log &mdash; Category {folder_name}</h2>
                <div class="folder-meta">
                    <strong>Category Mean Score (PA):</strong> <span style="color: #2b3e50; font-weight: bold;">{data['average_pa']:.2f}</span>
                </div>
                <table class="results-table">
                    <thead>
                        <tr>
                            <th style="width: 40%;">Sample ID</th>
                            <th class="text-right" style="width: 15%;">Loudness (sone)</th>
                            <th class="text-right" style="width: 15%;">Sharpness (acum)</th>
                            <th class="text-right" style="width: 15%;">Roughness (asper)</th>
                            <th class="text-right">Annoyance (PA)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows_html}
                    </tbody>
                </table>
            </div>
            <div class="page-break"></div>
            """

        # 2. Build the final GENERAL Summary Array rows
        general_summary_rows_html = ""
        for folder_name, data in all_folders_data.items():
            row_color_style = "color: #03543f; font-weight: bold;" if data['average_pa'] < 12 else "color: #9b1c1c; font-weight: bold;"
            general_summary_rows_html += f"""
            <tr>
                <td style="font-weight: bold;">Category {folder_name}</td>
                <td class="text-center">{len(data['files'])} files</td>
                <td class="text-right" style="{row_color_style}">{data['average_pa']:.2f}</td>
            </tr>
            """

        # 3. Complete core printable HTML document with compatible CSS definitions
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Multi-Category Acoustic Certification Report</title>
            <style>
                @page {{
                    size: a4;
                    margin: 20mm 15mm 20mm 15mm;
                }}
                
                body {{
                    font-family: Helvetica, Arial, sans-serif;
                    color: #2d3748;
                    font-size: 10pt;
                    line-height: 1.4;
                }}

                /* Footer styles for xhtml2pdf system tags */
                #footer-content {{
                    font-family: Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    color: #718096;
                    border-top: 1px solid #cbd5e0;
                    padding-top: 5px;
                }}

                .banner {{
                    padding: 20px;
                    background-color: #2b3e50;
                    color: #ffffff;
                    margin-bottom: 20px;
                }}
                
                .banner h1 {{
                    font-size: 20pt;
                    font-weight: bold;
                    margin: 0;
                    text-transform: uppercase;
                }}
                
                .banner .subtitle {{
                    font-size: 10pt;
                    color: #cbd5e0;
                    margin-top: 5px;
                }}

                .meta-table {{
                    width: 100%;
                    margin-bottom: 20px;
                }}
                
                .meta-table td {{
                    padding: 5px 0;
                    font-size: 10pt;
                }}
                
                .meta-label {{
                    font-weight: bold;
                    color: #4a5568;
                    width: 20%;
                }}
                
                .meta-value {{ color: #2d3748; width: 30%; }}

                .badge {{
                    padding: 3px 6px;
                    font-size: 9pt;
                    font-weight: bold;
                    text-transform: uppercase;
                }}

                .summary-card {{
                    background-color: #f8fafc;
                    border-left: 4px solid #2b3e50;
                    padding: 15px;
                    margin-bottom: 25px;
                }}
                
                .summary-card h3 {{
                    margin: 0 0 5px 0;
                    color: #2b3e50;
                    font-size: 11pt;
                    text-transform: uppercase;
                }}
                
                .summary-score-highlight {{ font-size: 14pt; color: #1a202c; font-weight: bold; }}

                h2 {{
                    color: #2b3e50;
                    font-size: 12pt;
                    font-weight: bold;
                    text-transform: uppercase;
                    border-bottom: 1px solid #e2e8f0;
                    padding-bottom: 5px;
                    margin-top: 20px;
                    margin-bottom: 10px;
                }}

                .folder-section {{
                    margin-bottom: 20px;
                }}
                
                .folder-meta {{
                    font-size: 10pt;
                    margin-bottom: 10px;
                    color: #4a5568;
                }}

                table.results-table {{
                    width: 100%;
                }}
                
                table.results-table th {{
                    background-color: #f1f5f9;
                    color: #4a5568;
                    font-weight: bold;
                    text-align: left;
                    padding: 8px;
                    font-size: 9pt;
                    border-bottom: 2px solid #cbd5e0;
                }}
                
                table.results-table td {{
                    padding: 7px 8px;
                    font-size: 9.5pt;
                    border-bottom: 1px solid #e2e8f0;
                }}
                
                .text-right {{ text-align: right; }}
                .text-center {{ text-align: center; }}
                
                .highlighted-cell {{
                    font-weight: bold;
                    color: #2b3e50;
                    background-color: #f1f5f9;
                }}

                .page-break {{ page-break-after: always; }}

                /* General Directory Summary Styling */
                table.summary-matrix {{
                    width: 100%;
                }}
                
                table.summary-matrix th {{
                    background-color: #2b3e50;
                    color: #ffffff;
                    font-weight: bold;
                    padding: 8px;
                    font-size: 10pt;
                    text-transform: uppercase;
                }}
                
                table.summary-matrix td {{
                    padding: 8px;
                    font-size: 10pt;
                    border: 1px solid #e2e8f0;
                }}
            </style>
        </head>
        <body>
            
            <div id="footer-content">
                <table style="width: 100%;">
                    <tr>
                        <td style="text-align: left;">MULTI-CATEGORY QUALITY CERTIFICATION | METHODOLOGY: PA MODEL</td>
                        <td style="text-align: right;">Page <pdf:pagenumber /></td>
                    </tr>
                </table>
            </div>

            <div class="banner">
                <h1>Multi-Category Acoustic Certification</h1>
                <div class="subtitle">Comprehensive Psychoacoustic Quality Assessment</div>
            </div>

            <table class="meta-table">
                <tr>
                    <td class="meta-label">Execution Date:</td>
                    <td class="meta-value">{datetime.now().strftime('%B %d, %Y')}</td>
                    <td class="meta-label">Ressources Path:</td>
                    <td class="meta-value">data/ressources/</td>
                </tr>
                <tr>
                    <td class="meta-label">Total Categories:</td>
                    <td class="meta-value">{len(all_folders_data)} directories</td>
                    <td class="meta-label">Global Status:</td>
                    <td class="meta-value"><span class="badge" style="{badge_style}">{interpretation}</span></td>
                </tr>
            </table>

            <div class="summary-card">
                <h3>Executive Core Cross-Validation</h3>
                <div class="summary-text">
                    This automated document certifies the empirical psychoacoustic scores processed across all directories found inside the base resources pathway. The cumulative cross-category <strong>Global Mean Annoyance Score (PA)</strong> is: 
                    <span class="summary-score-highlight">{global_average:.2f}</span>
                </div>
            </div>

            <div class="page-break"></div>

            {folder_sections_html}

            <div class="global-summary-section">
                <h2>General Directories Performance Summary (Recap Matrix)</h2>
                <table class="summary-matrix">
                    <thead>
                        <tr>
                            <th style="text-align: left;">Directory Target Name</th>
                            <th class="text-center" style="width: 30%;">Total Audio Volumes</th>
                            <th class="text-right" style="width: 30%;">Mean Annoyance Index (PA)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {general_summary_rows_html}
                        <tr style="background-color: #f1f5f9; font-weight: bold;">
                            <td>GLOBAL COMPREHENSIVE AVERAGE</td>
                            <td class="text-center">&mdash;</td>
                            <td class="text-right" style="color: #2b3e50; font-size: 11pt;">{global_average:.2f}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

        </body>
        </html>
        """

        # Generate output PDF safely
        os.makedirs(output_dir, exist_ok=True)
        pdf_filename = f"global_acoustic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_pdf_path = os.path.join(output_dir, pdf_filename)
        
        with open(output_pdf_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
            
        if pisa_status.err:
            logger.error("Error occurred during PDF rendering inside xhtml2pdf engine.")
        else:
            logger.info(f"Successfully exported multi-folder native PDF report to: {output_pdf_path}")
        
    except Exception as e:
        logger.error(f"Critical error whilst creating multi-folder report: {e}", exc_info=True)