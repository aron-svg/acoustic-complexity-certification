#!/usr/bin/env python
import os
from datetime import datetime
from weasyprint import HTML
from logger_init import logger

def generate_acoustic_report(all_folders_data, global_average, base_resources_dir, output_dir="./data/analysis"):
    """
    Generates a high-fidelity corporate multi-folder certification PDF report.
    Presents each folder's samples in distinct tables and concludes with a global directory summary.
    
    :param all_folders_data: Dict of folder names mapping to a dict with 'files' list and 'average_pa' float.
    :param global_average: Float representing the combined average across all directories.
    :param base_resources_dir: Path of the root ressources directory.
    :param output_dir: Destination path where the PDF will be saved.
    """
    logger.info("Initializing high-fidelity multi-folder PDF report generation...")
    
    if not all_folders_data:
        logger.warning("No multi-folder data discovered. Aborting layout construction.")
        return

    # Determine global status categorization based on global average
    if global_average < 12:
        interpretation = "Low Nuisance / Tolerable"
        badge_class = "badge-quiet"
    elif global_average < 25:
        interpretation = "Moderate to Significant"
        badge_class = "badge-warning"
    else:
        interpretation = "High to Critical Nuisance"
        badge_class = "badge-critical"

    # Logo resolution
    logo_path = os.path.abspath("data/logo/origenes.png")
    logo_img_tag = f'<img src="file://{logo_path}" class="logo-image" alt="Origenes Logo">' if os.path.exists(logo_path) else '<span class="logo-text">@origenes</span>'

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
                    <td class="text-right font-numeric">{row['loudness']:.2f}</td>
                    <td class="text-right font-numeric">{row['sharpness']:.2f}</td>
                    <td class="text-right font-numeric">{row['roughness']:.2f}</td>
                    <td class="text-right font-numeric highlighted-cell">{row['annoyance']:.2f}</td>
                </tr>
                """
            
            # Append the completed table structure for this specific folder
            folder_sections_html += f"""
            <div class="folder-section">
                <h2>Experimental Data Log — Category {folder_name}</h2>
                <div class="folder-meta">
                    <strong>Category Mean Score (PA):</strong> <span style="color: #2b3e50; font-weight: bold;">{data['average_pa']:.2f}</span>
                </div>
                <table class="results-table">
                    <thead>
                        <tr>
                            <th style="width: 36%;">Sample ID</th>
                            <th class="text-right" style="width: 16%;">Loudness<br><small>(sone)</small></th>
                            <th class="text-right" style="width: 16%;">Sharpness<br><small>(acum)</small></th>
                            <th class="text-right" style="width: 16%;">Roughness<br><small>(asper)</small></th>
                            <th class="text-right">Annoyance Score<br><small>(PA)</small></th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows_html}
                    </tbody>
                </table>
            </div>
            """

        # 2. Build the final GENERAL Summary Array rows
        general_summary_rows_html = ""
        for folder_name, data in all_folders_data.items():
            # Apply dynamic text colors depending on row metrics
            row_color_style = "color: #03543f; font-weight: bold;" if data['average_pa'] < 12 else "color: #9b1c1c; font-weight: bold;"
            general_summary_rows_html += f"""
            <tr>
                <td style="font-weight: bold;">Category {folder_name}</td>
                <td class="text-center">{len(data['files'])} files</td>
                <td class="text-right font-numeric" style="{row_color_style}">{data['average_pa']:.2f}</td>
            </tr>
            """

        # 3. Complete core printable HTML document with corporate CSS layout definitions
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Multi-Category Acoustic Certification Report</title>
            <style>
                @page {{
                    size: A4;
                    margin: 18mm 15mm;
                    @bottom-right {{
                        content: "Page " counter(page) " of " counter(pages);
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        font-size: 8.5pt;
                        color: #718096;
                    }}
                    @bottom-left {{
                        content: "MULTI-CATEGORY QUALITY CERTIFICATION | METHODOLOGY: PA MODEL (ZWICKER & FASTL)";
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        font-size: 8.5pt;
                        letter-spacing: 0.5px;
                        color: #718096;
                    }}
                }}
                
                body {{
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    color: #2d3748;
                    margin: 0;
                    padding: 0;
                    line-height: 1.5;
                    background-color: #ffffff;
                }}

                .banner {{
                    margin: -18mm -15mm 25px -15mm;
                    padding: 25px 15mm 20px 15mm;
                    background-color: #2b3e50;
                    color: #ffffff;
                    border-bottom: 4px solid #4a5568;
                }}
                
                .banner-table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                
                .banner-table td {{
                    vertical-align: middle;
                    padding: 0;
                    border: none;
                }}
                
                .title-area h1 {{
                    font-size: 19pt;
                    font-weight: bold;
                    margin: 0;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                }}
                
                .title-area subtitle {{
                    font-size: 10pt;
                    color: #cbd5e0;
                    display: block;
                    margin-top: 4px;
                    font-style: italic;
                }}
                
                .logo-area {{ text-align: right; }}
                .logo-image {{ max-height: 45px; max-width: 180px; object-fit: contain; }}
                .logo-text {{ font-size: 14pt; font-weight: bold; color: #cbd5e0; letter-spacing: 1px; }}

                .meta-container {{
                    width: 100%;
                    margin-bottom: 25px;
                    border-collapse: collapse;
                }}
                
                .meta-container td {{
                    padding: 6px 0;
                    font-size: 9.5pt;
                    border: none;
                }}
                
                .meta-label {{
                    font-weight: bold;
                    color: #4a5568;
                    width: 20%;
                    text-transform: uppercase;
                    font-size: 8.5pt;
                    letter-spacing: 0.5px;
                }}
                
                .meta-value {{ color: #2d3748; width: 30%; }}

                .summary-card {{
                    background-color: #f8fafc;
                    border-left: 5px solid #2b3e50;
                    padding: 15px 20px;
                    margin-bottom: 30px;
                }}
                
                .summary-card h3 {{
                    margin: 0 0 8px 0;
                    color: #2b3e50;
                    font-size: 11pt;
                    text-transform: uppercase;
                }}
                
                .summary-text {{ font-size: 10.5pt; color: #4a5568; }}
                .summary-score-highlight {{ font-size: 16pt; color: #1a202c; font-weight: bold; margin-left: 5px; }}

                h2 {{
                    color: #2b3e50;
                    font-size: 12pt;
                    font-weight: bold;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    border-bottom: 2px solid #e2e8f0;
                    padding-bottom: 6px;
                    margin-top: 25px;
                    margin-bottom: 10px;
                }}

                .folder-section {{
                    margin-bottom: 35px;
                    page-break-inside: auto;
                }}
                
                .folder-meta {{
                    font-size: 10pt;
                    margin-bottom: 8px;
                    color: #4a5568;
                }}

                table.results-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 15px;
                    page-break-inside: auto;
                }}
                
                table.results-table tr {{ page-break-inside: avoid; }}
                
                table.results-table th {{
                    background-color: #f1f5f9;
                    color: #4a5568;
                    font-weight: bold;
                    text-align: left;
                    padding: 9px 12px;
                    font-size: 8.5pt;
                    text-transform: uppercase;
                    border-top: 1px solid #cbd5e0;
                    border-bottom: 2px solid #cbd5e0;
                }}
                
                table.results-table td {{
                    padding: 8px 12px;
                    font-size: 9.5pt;
                    border-bottom: 1px solid #e2e8f0;
                }}
                
                table.results-table tr:nth-child(even) {{ background-color: #f8fafc; }}
                
                .text-right {{ text-align: right !important; }}
                .text-center {{ text-align: center !important; }}
                .font-numeric {{ font-variant-numeric: tabular-nums; }}
                
                .highlighted-cell {{
                    font-weight: bold;
                    color: #2b3e50;
                    background-color: #f1f5f9;
                    width: 16%;
                }}

                /* General Directory Summary Styling */
                .global-summary-section {{
                    margin-top: 40px;
                    page-break-inside: avoid;
                }}
                
                table.summary-matrix {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                
                table.summary-matrix th {{
                    background-color: #2b3e50;
                    color: #ffffff;
                    font-weight: bold;
                    padding: 10px 12px;
                    font-size: 9pt;
                    text-transform: uppercase;
                    border: 1px solid #2b3e50;
                }}
                
                table.summary-matrix td {{
                    padding: 10px 12px;
                    font-size: 10pt;
                    border: 1px solid #e2e8f0;
                }}

                .badge {{
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 8.5pt;
                    font-weight: bold;
                    text-transform: uppercase;
                    display: inline-block;
                }}
                .badge-quiet {{ background-color: #def7ec; color: #03543f; }}
                .badge-warning {{ background-color: #fde8e8; color: #9b1c1c; }}
                .badge-critical {{ background-color: #fde8e8; color: #9b1c1c; }}
            </style>
        </head>
        <body>
            
            <div class="banner">
                <table class="banner-table">
                    <tr>
                        <td class="title-area">
                            <h1>Multi-Category Acoustic Certification</h1>
                            <subtitle>Comprehensive Psychoacoustic Quality Assessment</subtitle>
                        </td>
                        <td class="logo-area">
                            {logo_img_tag}
                        </td>
                    </tr>
                </table>
            </div>

            <table class="meta-container">
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
                    <td class="meta-value"><span class="badge {badge_class}">{interpretation}</span></td>
                </tr>
            </table>

            <div class="summary-card">
                <h3>Executive Core Cross-Validation</h3>
                <div class="summary-text">
                    This automated document certifies the empirical psychoacoustic scores processed across all directories found inside the base resources pathway. The cumulative cross-category <strong>Global Mean Annoyance Score (PA)</strong> is: 
                    <span class="summary-score-highlight">{global_average:.2f}</span>
                </div>
            </div>

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
                            <td class="text-center">—</td>
                            <td class="text-right font-numeric" style="color: #2b3e50; font-size: 11pt;">{global_average:.2f}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

        </body>
        </html>
        """

        # Generate output PDF filename
        pdf_filename = f"global_acoustic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_pdf_path = os.path.join(output_dir, pdf_filename)
        
        HTML(string=html_content).write_pdf(output_pdf_path)
        logger.info(f"Successfully exported multi-folder corporate PDF report to: {output_pdf_path}")
        
    except Exception as e:
        logger.error(f"Critical error whilst creating multi-folder styled report from module: {e}", exc_info=True)