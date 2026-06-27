import os
import pandas as pd
import json

def build_dashboard():
    summary_path = "/workspaces/NigeriaBAY/data/processed/nga_bay_lga_summary.csv"
    output_path = "/workspaces/NigeriaBAY/index.html"
    
    if not os.path.exists(summary_path):
        print(f"Error: summary dataset not found at {summary_path}")
        return
        
    # Read the data
    df = pd.read_csv(summary_path)
    
    # Convert dataframe to JSON records
    lga_data_json = df.to_json(orient="records")
    
    # Build HTML Content with embedded JSON data and interactive filtering
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Education Disruption Dashboard – BAY States</title>
    <!-- Modern Typography -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;500;700&display=swap" rel="stylesheet">
    <!-- Chart.js CDN for interactive charts -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: rgba(17, 24, 39, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent-primary: #ff7e5f;
            --accent-secondary: #feb47b;
            --accent-gradient: linear-gradient(135deg, #ff7e5f 0%, #feb47b 100%);
            --glow-color: rgba(255, 126, 95, 0.15);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            align-items: center;
        }}

        /* Ambient Glow backgrounds */
        body::before {{
            content: '';
            position: absolute;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(255, 126, 95, 0.08) 0%, rgba(0,0,0,0) 70%);
            top: -100px;
            left: -100px;
            z-index: -1;
            pointer-events: none;
        }}

        body::after {{
            content: '';
            position: absolute;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(254, 180, 123, 0.06) 0%, rgba(0,0,0,0) 70%);
            top: 400px;
            right: -100px;
            z-index: -1;
            pointer-events: none;
        }}

        .dashboard-container {{
            max-width: 1400px;
            width: 100%;
            padding: 2.5rem 2rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }}

        header {{
            text-align: center;
            margin-bottom: 0.5rem;
        }}

        h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
            animation: fadeInDown 0.8s ease-out;
        }}

        .subtitle {{
            font-size: 1.1rem;
            color: var(--text-secondary);
            font-weight: 300;
            animation: fadeInUp 0.8s ease-out;
        }}

        /* Filter Controls */
        .controls-panel {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 1rem;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1rem;
            max-width: 500px;
            margin: 0 auto;
            width: 100%;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            animation: fadeInUp 0.8s ease-out;
        }}

        .controls-panel label {{
            font-weight: 600;
            font-size: 1rem;
            color: var(--text-primary);
        }}

        .controls-panel select {{
            background: #1e293b;
            color: var(--text-primary);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 0.5rem 1.5rem 0.5rem 1rem;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
            cursor: pointer;
            outline: none;
            transition: border-color 0.3s ease;
        }}

        .controls-panel select:focus {{
            border-color: var(--accent-primary);
        }}

        /* KPI Section */
        .kpi-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            animation: fadeIn 1s ease-out;
        }}

        .kpi-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.75rem 1.5rem;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: var(--accent-gradient);
            opacity: 0.7;
        }}

        .kpi-card:hover {{
            transform: translateY(-4px);
            border-color: rgba(255, 126, 95, 0.4);
            box-shadow: 0 15px 30px rgba(255, 126, 95, 0.1);
        }}

        .kpi-value {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem;
            font-weight: 800;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}

        .kpi-label {{
            font-size: 0.95rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Visualizations Layout */
        .visualizations-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            animation: fadeIn 1.2s ease-out;
        }}

        .visual-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 1.5rem;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }}

        .visual-card h2 {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.4rem;
            font-weight: 600;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 0.75rem;
            color: var(--text-primary);
        }}

        .map-frame-container {{
            height: 550px;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
            background: #ffffff;
        }}

        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}

        .chart-container {{
            height: 550px;
            border-radius: 12px;
            padding: 1rem;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.05);
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        canvas {{
            width: 100% !important;
            height: 100% !important;
        }}

        /* Insight Section */
        .insight-section {{
            background: linear-gradient(135deg, rgba(255, 126, 95, 0.05) 0%, rgba(254, 180, 123, 0.05) 100%);
            border: 1px dashed rgba(255, 126, 95, 0.3);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            box-shadow: inset 0 0 20px rgba(255, 126, 95, 0.02);
            animation: fadeIn 1.4s ease-out;
            max-width: 1000px;
            margin: 0 auto;
            width: 100%;
        }}

        .insight-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--accent-primary);
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }}

        .insight-text {{
            font-size: 1.2rem;
            line-height: 1.7;
            color: var(--text-primary);
            font-weight: 400;
            font-style: italic;
        }}

        /* Downloads Section */
        .downloads-bar {{
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            flex-wrap: wrap;
            margin-top: 0.5rem;
        }}

        .btn-download {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 0.8rem 1.8rem;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .btn-download:hover {{
            background: var(--accent-gradient);
            border-color: transparent;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 126, 95, 0.2);
            color: #ffffff;
        }}

        footer {{
            width: 100%;
            padding: 2rem;
            text-align: center;
            border-top: 1px solid var(--border-color);
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: auto;
        }}

        /* Animations */
        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}

        /* Table Styles */
        .table-container {{
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            background: rgba(15, 23, 42, 0.4);
            margin-top: 0.5rem;
        }}

        .top-lgas-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.9rem;
        }}

        .top-lgas-table th {{
            background-color: rgba(30, 41, 59, 0.6);
            color: var(--accent-primary);
            font-weight: 700;
            padding: 1rem;
            border-bottom: 2px solid rgba(255, 255, 255, 0.08);
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.5px;
        }}

        .top-lgas-table td {{
            padding: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            color: var(--text-primary);
        }}

        .top-lgas-table tr:hover {{
            background-color: rgba(255, 126, 95, 0.05);
        }}

        /* Responsive design */
        @media (max-width: 1024px) {{
            .visualizations-grid {{
                grid-template-columns: 1fr;
            }}
            .map-frame-container, .chart-container {{
                height: 500px;
            }}
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 2rem;
            }}
            .dashboard-container {{
                padding: 1.5rem 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <header>
            <h1>Education Disruption Dashboard – BAY States</h1>
            <p class="subtitle">Northeast Nigeria Spatial Vulnerability Analysis</p>
        </header>

        <!-- Dropdown State Selector -->
        <section class="controls-panel">
            <label for="state-select">Select Region / State:</label>
            <select id="state-select" onchange="onStateChange(this.value)">
                <option value="All">All States (BAY Region)</option>
                <option value="Adamawa">Adamawa</option>
                <option value="Borno">Borno</option>
                <option value="Yobe">Yobe</option>
            </select>
        </section>

        <!-- KPI Cards Section -->
        <section class="kpi-section">
            <div class="kpi-card">
                <div class="kpi-value" id="val-idps">-</div>
                <div class="kpi-label">Total IDPs</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value" id="val-schools">-</div>
                <div class="kpi-label">Total Schools</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value" id="val-closed-ratio">-</div>
                <div class="kpi-label">% Closed Schools</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value" id="val-high-risk">-</div>
                <div class="kpi-label" id="label-high-risk">Highest Risk LGA</div>
            </div>
        </section>

        <!-- Visualizations Grid -->
        <section class="visualizations-grid">
            <!-- Map Card -->
            <div class="visual-card">
                <h2>Interactive Education Disruption & Risk Map</h2>
                <div class="map-frame-container">
                    <iframe src="outputs/maps/education_disruption_map.html" id="map-iframe" title="Education Disruption Map" onload="onIframeLoad()"></iframe>
                </div>
            </div>

            <!-- Chart Card -->
            <div class="visual-card">
                <h2>Top 10 High-Risk LGAs</h2>
                <div class="chart-container">
                    <canvas id="risk-chart"></canvas>
                </div>
            </div>
        </section>

        <!-- Detailed Table Card -->
        <section class="table-section">
            <div class="visual-card">
                <h2>Top 10 High-Risk LGAs - Detailed Indicator Breakdown</h2>
                <div class="table-container">
                    <table class="top-lgas-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>LGA Name</th>
                                <th>State</th>
                                <th>Risk Score</th>
                                <th>School-Age Pop</th>
                                <th>IDP Population</th>
                                <th>Conflict Count</th>
                                <th>Closed Schools</th>
                            </tr>
                        </thead>
                        <tbody id="top-lgas-table-body">
                            <!-- Populated dynamically via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- Insights Section -->
        <section class="insight-section">
            <div class="insight-title">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
                    <line x1="12" y1="9" x2="12" y2="13"></line>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                Core Insight
            </div>
            <p class="insight-text">
                "Education disruption is concentrated in LGAs where conflict activity, high IDP populations, and school closures overlap. These LGAs should be prioritized for intervention."
            </p>
        </section>

        <!-- Downloads bar -->
        <section class="downloads-bar">
            <a href="outputs/maps/final_dataset.csv" class="btn-download" target="_blank">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Full Dataset (.csv)
            </a>
            <a href="outputs/maps/top_10_lgas.csv" class="btn-download" target="_blank">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Top 10 LGAs List (.csv)
            </a>
        </section>
    </div>

    <!-- Data Injection -->
    <script>
        const rawLgaData = {lga_data_json};
        
        let chartInstance = null;

        function updateDashboard(state) {{
            // 1. Filter Data
            const filteredData = state === "All" 
                ? rawLgaData 
                : rawLgaData.filter(item => item.state === state);

            // 2. Compute KPIs
            const totalIdps = filteredData.reduce((sum, item) => sum + (item.idp_population || 0), 0);
            const totalSchools = filteredData.reduce((sum, item) => sum + (item.total_schools || 0), 0);
            const totalClosed = filteredData.reduce((sum, item) => sum + (item.closed_schools || 0), 0);
            
            const closedRatio = totalSchools > 0 
                ? ((totalClosed / totalSchools) * 100).toFixed(2) + "%"
                : "0.00%";

            // Find highest risk LGA in this subset
            let highestRiskLga = "N/A";
            let highestRiskScore = -1;
            filteredData.forEach(item => {{
                if (item.risk_score > highestRiskScore) {{
                    highestRiskScore = item.risk_score;
                    highestRiskLga = item.LGA;
                }}
            }});

            // 3. Update DOM KPI Values
            document.getElementById("val-idps").textContent = totalIdps.toLocaleString();
            document.getElementById("val-schools").textContent = totalSchools.toLocaleString();
            document.getElementById("val-closed-ratio").textContent = closedRatio;
            
            const highRiskValNode = document.getElementById("val-high-risk");
            highRiskValNode.textContent = highestRiskLga;
            // Shrink text slightly if name is too long to prevent spillover
            if (highestRiskLga.length > 12) {{
                highRiskValNode.style.fontSize = "1.8rem";
            }} else {{
                highRiskValNode.style.fontSize = "2.2rem";
            }}

            const labelHighRisk = document.getElementById("label-high-risk");
            labelHighRisk.textContent = state === "All" ? "Highest Risk LGA" : `Highest Risk LGA in ${{state}}`;

            // 4. Update Chart (Top 10 LGAs by Risk Score)
            // Sort by risk_score desc and take top 10
            const top10 = [...filteredData]
                .sort((a, b) => b.risk_score - a.risk_score)
                .slice(0, 10);

            const labels = top10.map(item => item.LGA);
            const scores = top10.map(item => item.risk_score);

            updateChart(labels, scores);

            // 5. Update Map State Outlines
            const mapIframe = document.getElementById("map-iframe");
            if (mapIframe && mapIframe.contentWindow && typeof mapIframe.contentWindow.highlightState === 'function') {{
                mapIframe.contentWindow.highlightState(state);
            }}

            // 6. Update Table
            updateTable(top10);
        }}

        function updateChart(labels, scores) {{
            const ctx = document.getElementById('risk-chart').getContext('2d');
            
            // Build dynamic colors corresponding to YlOrRd colormap
            const colors = scores.map(score => {{
                // Interpolate colors between yellow (low score) and red (high score)
                // Yellow: rgba(255, 237, 160, 0.85) -> Red: rgba(189, 0, 38, 0.9)
                const r = Math.round(255 - (255 - 189) * score);
                const g = Math.round(237 - (237 - 0) * score);
                const b = Math.round(160 - (160 - 38) * score);
                return `rgba(${{r}}, ${{g}}, ${{b}}, 0.85)`;
            }});

            const borderColors = scores.map(score => {{
                const r = Math.round(255 - (255 - 189) * score);
                const g = Math.round(237 - (237 - 0) * score);
                const b = Math.round(160 - (160 - 38) * score);
                return `rgb(${{r}}, ${{g}}, ${{b}})`;
            }});

            if (chartInstance) {{
                chartInstance.data.labels = labels;
                chartInstance.data.datasets[0].data = scores;
                chartInstance.data.datasets[0].backgroundColor = colors;
                chartInstance.data.datasets[0].borderColor = borderColors;
                chartInstance.update();
            }} else {{
                chartInstance = new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: labels,
                        datasets: [{{
                            label: 'Risk Score',
                            data: scores,
                            backgroundColor: colors,
                            borderColor: borderColors,
                            borderWidth: 1.5,
                            borderRadius: 6,
                            barPercentage: 0.6
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            tooltip: {{
                                backgroundColor: '#1e293b',
                                titleColor: '#f3f4f6',
                                bodyColor: '#9ca3af',
                                borderColor: 'rgba(255,255,255,0.1)',
                                borderWidth: 1,
                                padding: 10,
                                font: {{
                                    family: "'Plus Jakarta Sans', sans-serif"
                                }},
                                callbacks: {{
                                    label: function(context) {{
                                        return ` Risk Score: ${{context.raw.toFixed(4)}}`;
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            x: {{
                                grid: {{
                                    display: false
                                }},
                                ticks: {{
                                    color: '#e5e7eb',
                                    font: {{
                                        family: "'Plus Jakarta Sans', sans-serif",
                                        size: 11,
                                        weight: '500'
                                    }},
                                    maxRotation: 45,
                                    minRotation: 45
                                }}
                            }},
                            y: {{
                                min: 0,
                                max: 1.0,
                                grid: {{
                                    color: 'rgba(255,255,255,0.06)'
                                }},
                                ticks: {{
                                    color: '#9ca3af',
                                    font: {{
                                        family: "'Plus Jakarta Sans', sans-serif",
                                        size: 10
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }}
        }}

        function updateTable(top10) {{
            const tbody = document.getElementById("top-lgas-table-body");
            if (!tbody) return;
            tbody.innerHTML = "";
            top10.forEach((item, index) => {{
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td style="font-weight: 700; color: var(--accent-secondary);">${{index + 1}}</td>
                    <td style="font-weight: 600;">${{item.LGA}}</td>
                    <td>${{item.state}}</td>
                    <td style="font-weight: 700; color: var(--accent-primary);">${{item.risk_score.toFixed(4)}}</td>
                    <td>${{(item.school_age_population || 0).toLocaleString()}}</td>
                    <td>${{(item.idp_population || 0).toLocaleString()}}</td>
                    <td>${{item.conflict_count || 0}}</td>
                    <td>${{item.closed_schools || 0}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function onIframeLoad() {{
            const selectEl = document.getElementById("state-select");
            const state = selectEl ? selectEl.value : "All";
            const mapIframe = document.getElementById("map-iframe");
            if (mapIframe && mapIframe.contentWindow && typeof mapIframe.contentWindow.highlightState === 'function') {{
                mapIframe.contentWindow.highlightState(state);
            }}
        }}

        function onStateChange(value) {{
            updateDashboard(value);
        }}

        // Initialize on load
        window.addEventListener('DOMContentLoaded', () => {{
            updateDashboard("All");
        }});
    </script>
</body>
</html>
"""
    
    with open(output_path, "w") as f:
        f.write(html_content)
        
    print(f"Dashboard successfully compiled and written to {output_path}")

if __name__ == "__main__":
    build_dashboard()
