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
    
    # Generate table rows
    table_rows = ""
    for idx, row in df_sorted.iterrows():
        table_rows += f"""                        <tr>
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
            max-width: 1200px;
            margin: 0 auto;
            padding: 50px 20px;
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
        .formula-title {{
            font-size: 16px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 10px;
        }}
        .formula-list {{
            list-style-type: none;
            padding: 0;
            margin: 0;
            font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 14px;
            color: #334155;
            line-height: 1.7;
        }}
        .formula-item {{
            padding-left: 8px;
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
    </style>
</head>
<body>
    <div class="dashboard-container">
        <h1>Education Disruption Dashboard &ndash; BAY States Nigeria</h1>

        <!-- 1. KPI Section -->
        <div class="section-wrapper">
            <div class="kpi-container">
                <div class="kpi-box">
                    <div class="kpi-value">{total_idps:,}</div>
                    <div class="kpi-label">Total IDPs</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-value">{total_schools:,}</div>
                    <div class="kpi-label">Total Schools</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-value">{closed_percentage:.2f}%</div>
                    <div class="kpi-label">% Closed Schools</div>
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
                    Education disruption is concentrated in a small number of LGAs in Borno State, where conflict intensity, large displaced populations, and high school closure rates overlap.
                </p>
            </div>
        </div>

        <!-- 3. Embedded Map -->
        <div class="section-wrapper">
            <div class="section-title">Interactive Education Disruption & Risk Map</div>
            <div class="map-container">
                <iframe src="outputs/maps/education_disruption_map.html?v={int(time.time())}" id="map-iframe" title="Education Disruption Map"></iframe>
            </div>
        </div>

        <!-- 4. Top 10 LGA Table -->
        <div class="section-wrapper">
            <div class="section-title">Top 10 High-Risk LGAs</div>
            <div class="table-container">
                <table class="top-lgas-table">
                    <thead>
                        <tr>
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

        <!-- 5. Risk Model Section -->
        <div class="section-wrapper">
            <div class="model-box">
                <div class="model-title">How Risk is Calculated</div>
                <div class="formula-box">
                    <div class="formula-title">Risk Score =</div>
                    <ul class="formula-list">
                        <li class="formula-item">&bull; 30% Conflict +</li>
                        <li class="formula-item">&bull; 25% IDP Population +</li>
                        <li class="formula-item">&bull; 25% School Closure Rate +</li>
                        <li class="formula-item">&bull; 20% School-age Population</li>
                    </ul>
                </div>
                <p class="model-explanation">
                    This model identifies areas where children are most at risk of losing access to education.
                </p>
            </div>
        </div>

        <!-- 6. How to Use Section -->
        <div class="section-wrapper">
            <div class="usage-box">
                <div class="usage-title">How to Use This Dashboard</div>
                <ol class="usage-steps">
                    <li class="usage-step">Focus on red (high-risk) LGAs</li>
                    <li class="usage-step">Check IDP population levels</li>
                    <li class="usage-step">Identify areas with high numbers of closed schools</li>
                    <li class="usage-step">Prioritize these LGAs for intervention</li>
                </ol>
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
