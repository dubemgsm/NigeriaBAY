import os
import pandas as pd
import time

def build_dashboard():
    summary_path = "/workspaces/NigeriaBAY/data/processed/nga_bay_lga_summary.csv"
    output_path = "/workspaces/NigeriaBAY/index.html"
    
    if not os.path.exists(summary_path):
        print(f"Error: summary dataset not found at {summary_path}")
        return
        
    # Read the data
    df = pd.read_csv(summary_path)
    
    # Calculate KPI values
    total_idps = int(df["idp_population"].sum())
    total_schools = int(df["total_schools"].sum())
    total_closed = int(df["closed_schools"].sum())
    closed_percentage = (total_closed / total_schools * 100) if total_schools > 0 else 0.0
    
    idx_max = df["risk_score"].idxmax()
    highest_risk_lga = df.loc[idx_max]["LGA"]
    highest_risk_state = df.loc[idx_max]["state"]
    
    # Get top 10 LGAs by risk_score
    df_sorted = df.sort_values(by="risk_score", ascending=False).head(10)
    
    # Load Top 10 priority LGAs from outputs/maps/top_10_lgas.csv
    top_10_csv_path = "/workspaces/NigeriaBAY/outputs/maps/top_10_lgas.csv"
    if os.path.exists(top_10_csv_path):
        df_top_10 = pd.read_csv(top_10_csv_path)
    else:
        df_top_10 = df_sorted.copy()
        df_top_10["rank"] = range(1, len(df_top_10) + 1)
        
    priority_table_rows = ""
    for idx, row in df_top_10.iterrows():
        rank = int(row['rank'])
        lga = row['LGA']
        risk_score = float(row['risk_score'])
        priority_table_rows += f"""                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{rank}</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{lga}</td>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; text-align: right;">{risk_score:.4f}</td>
                        </tr>\n"""

    # Generate table rows
    table_rows = ""
    for rank, (idx, row) in enumerate(df_sorted.iterrows(), 1):
        rank_class = f"rank-{rank}" if rank <= 3 else "rank-other"
        table_rows += f"""                        <tr>
                            <td style="text-align: center;"><span class="rank-badge {rank_class}">#{rank}</span></td>
                            <td>{row['LGA']}</td>
                            <td>{row['state']}</td>
                            <td><strong>{row['risk_score']:.4f}</strong></td>
                            <td>{int(row['school_age_population']):,}</td>
                            <td>{int(row['idp_population']):,}</td>
                            <td>{int(row['conflict_count']):,}</td>
                            <td>{int(row['closed_schools']):,}</td>
                        </tr>\n"""
                        
    # HTML template with enhanced styling
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Education Disruption Dashboard – BAY States Nigeria</title>
    <style>
        body {{
            font-family: Arial, Helvetica, sans-serif;
            background-color: #f8fafc;
            color: #334155;
            margin: 0;
            padding: 0;
        }}
        .dashboard-container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
            font-family: Arial, Helvetica, sans-serif;
        }}
        h1 {{
            text-align: center;
            color: #0f172a;
            font-size: 32px;
            margin-bottom: 50px;
            font-weight: 800;
        }}
        .section-wrapper {{
            margin-bottom: 50px;
        }}
        .section-title {{
            font-size: 22px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 20px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }}
        
        /* KPI Styles - Prominent Numbers & Slate-Blue Theme */
        .kpi-container {{
            display: flex;
            justify-content: space-between;
            gap: 20px;
        }}
        .kpi-box {{
            flex: 1;
            padding: 24px 20px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            text-align: center;
            background-color: #ffffff;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        }}
        .kpi-value {{
            font-size: 36px;
            font-weight: 800;
            color: #2563eb;
            margin-bottom: 8px;
            line-height: 1.1;
        }}
        .kpi-label {{
            font-size: 13px;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Key Insight Styles */
        .insight-box {{
            padding: 24px;
            background-color: #eff6ff;
            border-left: 5px solid #2563eb;
            border-top: 1px solid #dbeafe;
            border-right: 1px solid #dbeafe;
            border-bottom: 1px solid #dbeafe;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.03);
        }}
        .insight-title {{
            font-size: 14px;
            font-weight: 800;
            color: #1e40af;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.75px;
        }}
        .insight-text {{
            font-size: 15px;
            color: #1e293b;
            line-height: 1.6;
            margin: 0;
        }}

        /* Map Styles - Centered and Wide */
        .map-container {{
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            overflow: hidden;
            height: 600px;
            background-color: #ffffff;
        }}
        .map-container iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}

        /* Table Styles */
        .table-container {{
            overflow-x: auto;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            background-color: #ffffff;
        }}
        .top-lgas-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 14px;
        }}
        .top-lgas-table th {{
            background-color: #f1f5f9;
            font-weight: 700;
            color: #0f172a;
            padding: 14px 18px;
            border-bottom: 2px solid #e2e8f0;
        }}
        .top-lgas-table td {{
            padding: 14px 18px;
            border-bottom: 1px solid #e2e8f0;
            color: #334155;
        }}
        .top-lgas-table tr:last-child td {{
            border-bottom: none;
        }}
        .top-lgas-table tr:hover {{
            background-color: #f8fafc;
        }}
        .rank-badge {{
            display: inline-block;
            width: 24px;
            height: 24px;
            line-height: 24px;
            text-align: center;
            border-radius: 50%;
            font-weight: 800;
            font-size: 11px;
        }}
        .rank-1 {{ background-color: #fef08a; color: #854d0e; border: 1px solid #eab308; }}
        .rank-2 {{ background-color: #e2e8f0; color: #475569; border: 1px solid #94a3b8; }}
        .rank-3 {{ background-color: #ffedd5; color: #c2410c; border: 1px solid #f97316; }}
        .rank-other {{ background-color: #f1f5f9; color: #64748b; border: 1px solid #cbd5e1; }}

        /* Risk Model Styles */
        .model-box {{
            padding: 24px;
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        .model-title {{
            font-size: 18px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 16px;
        }}
        .formula-box {{
            background-color: #f8fafc;
            border: 1.5px solid #e2e8f0;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 16px;
        }}
        .formula-text {{
            font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 15px;
            font-weight: 700;
            color: #1e293b;
            line-height: 1.5;
            margin: 0;
            text-align: center;
        }}
        .model-explanation {{
            font-size: 14px;
            color: #64748b;
            line-height: 1.6;
            margin: 0;
        }}

        /* Usage Styles */
        .usage-box {{
            padding: 24px;
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        .usage-title {{
            font-size: 18px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 16px;
        }}
        .usage-steps {{
            padding-left: 20px;
            margin: 0;
        }}
        .usage-step {{
            font-size: 14px;
            color: #334155;
            line-height: 1.8;
            margin-bottom: 8px;
        }}
        .usage-step:last-child {{
            margin-bottom: 0;
        }}

        /* Limitations Styles */
        .limitations-box {{
            padding: 20px;
            background-color: #f8fafc;
            border: 1px dashed #cbd5e1;
            border-radius: 8px;
            margin-top: 40px;
        }}
        .limitations-title {{
            font-size: 14px;
            font-weight: 700;
            color: #64748b;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .limitations-list {{
            padding-left: 20px;
            margin: 0;
            font-size: 13px;
            color: #64748b;
            line-height: 1.6;
        }}
        .limitations-item {{
            margin-bottom: 6px;
        }}
        .limitations-item:last-child {{
            margin-bottom: 0;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <h1>Education Disruption Dashboard – BAY States Nigeria</h1>
        <div style="display:flex; justify-content:space-between; margin:20px 0; gap: 15px;">
            <div style="flex: 1; padding: 20px; border: 1px solid #ccc; text-align: center;">
                <div style="font-size: 24px; font-weight: bold;">{total_idps:,}</div>
                <div style="font-size: 14px; color: #666; margin-top: 5px;">Total IDPs</div>
            </div>
            <div style="flex: 1; padding: 20px; border: 1px solid #ccc; text-align: center;">
                <div style="font-size: 24px; font-weight: bold;">{total_schools:,}</div>
                <div style="font-size: 14px; color: #666; margin-top: 5px;">Total Schools</div>
            </div>
            <div style="flex: 1; padding: 20px; border: 1px solid #ccc; text-align: center;">
                <div style="font-size: 24px; font-weight: bold;">{closed_percentage:.2f}%</div>
                <div style="font-size: 14px; color: #666; margin-top: 5px;">Closed Schools (%)</div>
            </div>
            <div style="flex: 1; padding: 20px; border: 1px solid #ccc; text-align: center;">
                <div style="font-size: 24px; font-weight: bold;">{highest_risk_lga} ({highest_risk_state})</div>
                <div style="font-size: 14px; color: #666; margin-top: 5px;">Highest Risk LGA</div>
            </div>
        </div>
        <div style="background-color: #f4f6f7; padding: 20px; margin: 20px 0; border-radius: 6px;">
            <h3 style="margin-top: 0; margin-bottom: 10px; font-weight: bold; font-size: 18px; color: #0f172a;">Key Insight</h3>
            <p style="margin: 0; line-height: 1.5;">
                Education disruption is concentrated in a small number of LGAs in Borno State, where conflict intensity, displacement, and school closures overlap.
            </p>
        </div>

        <!-- 1. KPI Section -->
        <div class="section-wrapper">
            <div class="kpi-container">
                <div class="kpi-box">
                    <div class="kpi-value">{total_idps:,}</div>
                    <div class="kpi-label">Total IDP Population</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-value">{total_schools:,}</div>
                    <div class="kpi-label">Total Schools</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-value">{closed_percentage:.2f}%</div>
                    <div class="kpi-label">Percentage of Closed Schools</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-value" style="font-size: 28px; padding-top: 6px; padding-bottom: 2px;">{highest_risk_lga} ({highest_risk_state})</div>
                    <div class="kpi-label">Highest Risk LGA</div>
                </div>
            </div>
        </div>

        <!-- 2. Key Insight -->
        <div class="section-wrapper">
            <div class="insight-box">
                <div class="insight-title">Key Insight</div>
                <p class="insight-text">
                    Education disruption is concentrated in a small number of LGAs in Borno State, where high conflict intensity overlaps with large IDP populations and high school closure rates.
                </p>
            </div>
        </div>

        <!-- 3. Embedded Map -->
        <div style="margin: 40px auto; width: 100%; display: flex; flex-direction: column; align-items: center;">
            <div class="section-title" style="width: 100%;">Interactive Education Disruption & Risk Map</div>
            <div class="map-container" style="width: 100%; margin: 0 auto;">
                <iframe src="outputs/maps/education_disruption_map.html?v={int(time.time())}" id="map-iframe" title="Education Disruption Map" style="width: 100%; height: 100%; border: none;"></iframe>
            </div>
        </div>

        <!-- Priority Table Section -->
        <div style="margin: 30px auto; width: 100%;">
            <div class="section-title" style="width: 100%;">Top 10 Priority LGAs</div>
            <div style="overflow-x: auto; width: 100%;">
                <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px;">
                    <thead>
                        <tr style="background-color: #f1f5f9;">
                            <th style="padding: 12px 10px; border: 1px solid #ddd; font-weight: bold; text-align: center; width: 80px;">Rank</th>
                            <th style="padding: 12px 10px; border: 1px solid #ddd; font-weight: bold; text-align: left;">LGA</th>
                            <th style="padding: 12px 10px; border: 1px solid #ddd; font-weight: bold; text-align: right; width: 150px;">Risk Score</th>
                        </tr>
                    </thead>
                    <tbody>
{priority_table_rows}                    </tbody>
                </table>
            </div>
        </div>

        <!-- 4. Risk Model Section -->
        <div class="section-wrapper" style="margin-top: 40px;">
            <div class="model-box">
                <div class="model-title">How Risk is Calculated</div>
                <div class="formula-box">
                    <div class="formula-text">
                        Risk Score = 30% Conflict + 25% IDP Population + 25% School Closure Rate + 20% School-age Population
                    </div>
                </div>
                <p class="model-explanation">
                    This model identifies LGAs where children are most at risk of losing access to education.
                </p>
            </div>
        </div>

        <!-- 5. How to Use Section -->
        <div class="section-wrapper">
            <div class="usage-box">
                <div class="usage-title">How to Use This Dashboard</div>
                <ol class="usage-steps">
                    <li class="usage-step">Focus on red (high-risk) LGAs</li>
                    <li class="usage-step">Identify LGAs with high IDP population</li>
                    <li class="usage-step">Examine areas with many closed schools</li>
                    <li class="usage-step">Prioritize these LGAs for intervention</li>
                </ol>
            </div>
        </div>

        <!-- 6. Top 10 LGA Table -->
        <div class="section-wrapper">
            <div class="section-title">Top 10 High-Risk LGAs</div>
            <div class="table-container">
                <table class="top-lgas-table">
                    <thead>
                        <tr>
                            <th style="text-align: center;">Rank</th>
                            <th>LGA Name</th>
                            <th>State</th>
                            <th>Risk Score</th>
                            <th>School-Age Pop</th>
                            <th>IDP Population</th>
                            <th>Conflict Count</th>
                            <th>Closed Schools</th>
                        </tr>
                    </thead>
                    <tbody>
{table_rows}                    </tbody>
                </table>
            </div>
        </div>

        <!-- 7. Limitations Section -->
        <div class="section-wrapper" style="margin-bottom: 0;">
            <div class="limitations-box">
                <div class="limitations-title">Limitations</div>
                <ul class="limitations-list">
                    <li class="limitations-item">School status data may be incomplete</li>
                    <li class="limitations-item">IDP data may not be up-to-date</li>
                    <li class="limitations-item">Some LGAs may have limited data coverage</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""

    with open(output_path, "w") as f:
        f.write(html_content)
    print(f"Dashboard compiled successfully to {output_path}")

if __name__ == "__main__":
    build_dashboard()
