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
        
    # Calculate percentage of IDPs in top 5 LGAs
    df_top_5 = df_top_10.head(5)
    top_5_idp_population = int(df_top_5["idp_population"].sum())
    pct_idps_top5 = (top_5_idp_population / total_idps * 100) if total_idps > 0 else 0.0
    
    # Calculate percentage of total risk in top 10 LGAs
    total_risk_all = df["risk_score"].sum()
    top_10_risk_sum = df_top_10["risk_score"].sum()
    pct_risk_top10 = (top_10_risk_sum / total_risk_all * 100) if total_risk_all > 0 else 0.0

    # --------------------------------------------------------------------------
    # Compute conflict temporal patterns for the entire BAY states (2011+)
    # --------------------------------------------------------------------------
    conflict_path = "/workspaces/NigeriaBAY/data/clean/conflict.csv"
    monthly_rows = ""
    holiday_rows = ""
    tactical_rows = ""
    
    if os.path.exists(conflict_path):
        import holidays
        from datetime import datetime, timedelta
        
        df_conflict_raw = pd.read_csv(conflict_path)
        df_conflict_raw['date_dt'] = pd.to_datetime(df_conflict_raw['date_start'])
        df_conflict_raw['lga_clean'] = df_conflict_raw['adm_2'].str.lower().str.replace(' lga', '', regex=False).str.strip()
        
        # Filter for dates from 2011 upwards across the entire BAY states (no LGA restriction)
        df_matched = df_conflict_raw[df_conflict_raw['date_dt'].dt.year >= 2011].copy()
        
        # Ramadan dates
        ramadan_dates_dict = {
            2003: ('2003-10-27', '2003-11-25'),
            2004: ('2004-10-15', '2004-11-13'),
            2005: ('2005-10-04', '2005-11-02'),
            2006: ('2006-09-24', '2006-10-23'),
            2007: ('2007-09-13', '2007-10-12'),
            2008: ('2008-09-01', '2008-09-29'),
            2009: ('2009-08-22', '2009-09-19'),
            2010: ('2010-08-11', '2010-09-09'),
            2011: ('2011-08-01', '2011-08-29'),
            2012: ('2012-07-20', '2012-08-18'),
            2013: ('2013-07-09', '2013-08-07'),
            2014: ('2014-06-28', '2014-07-27'),
            2015: ('2015-06-18', '2015-07-16'),
            2016: ('2016-06-06', '2016-07-05'),
            2017: ('2017-05-27', '2017-06-24'),
            2018: ('2018-05-16', '2018-06-14'),
            2019: ('2019-05-06', '2019-06-03'),
            2020: ('2020-04-24', '2020-05-23'),
            2021: ('2021-04-13', '2021-05-12'),
            2022: ('2022-04-02', '2022-05-01'),
            2023: ('2023-03-23', '2023-04-20'),
            2024: ('2024-03-11', '2024-04-09'),
        }
        
        ng_hols = holidays.NG(years=range(2003, 2025))
        
        def assign_category(row):
            dt = row['date_dt']
            year = dt.year
            
            if year in ramadan_dates_dict:
                start_str, end_str = ramadan_dates_dict[year]
                start_dt = pd.to_datetime(start_str)
                end_dt = pd.to_datetime(end_str)
                if start_dt <= dt <= end_dt:
                    if dt < start_dt + timedelta(days=3):
                        return 'Ramadan Start (First 3 Days)'
                    elif dt > end_dt - timedelta(days=3):
                        return 'Ramadan End (Last 3 Days)'
                    else:
                        return 'Ramadan (Active Month)'
                        
            if dt in ng_hols:
                hname = ng_hols.get(dt)
                hname_lower = hname.lower()
                if 'fitr' in hname_lower:
                    return 'Eid al-Fitr (Id el Fitr)'
                elif 'kabir' in hname_lower or 'adha' in hname_lower:
                    return 'Eid al-Adha (Id el Kabir)'
                elif 'maulud' in hname_lower or 'prophet' in hname_lower:
                    return 'Mawlid (Id el Maulud)'
                elif 'christmas' in hname_lower or 'boxing' in hname_lower or 'new year' in hname_lower:
                    return 'Christmas & New Year Festivities'
                elif 'easter' in hname_lower or 'good friday' in hname_lower:
                    return 'Easter Holiday'
                else:
                    return 'Other Public Holidays'
                    
            if (dt.month == 12 and dt.day >= 24) or (dt.month == 1 and dt.day <= 2):
                return 'Christmas & New Year Festivities'
                
            return 'Regular Days'
            
        df_matched['category'] = df_matched.apply(assign_category, axis=1)
        total_matched_conflicts = len(df_matched)
        
        # Compute monthly distribution
        df_matched['month'] = df_matched['date_dt'].dt.month
        # Compute monthly distribution (top 6 months by count)
        df_matched['month'] = df_matched['date_dt'].dt.month
        monthly_counts = df_matched['month'].value_counts()
        months_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        
        max_monthly = monthly_counts.max() if not monthly_counts.empty else 1
        for m_num, val in list(monthly_counts.items())[:6]:
            pct = (val / total_matched_conflicts * 100) if total_matched_conflicts > 0 else 0.0
            spark_width = (val / max_monthly * 100) if max_monthly > 0 else 0.0
            
            monthly_rows += f"""                                <tr>
                                    <td>{months_names[m_num-1]}</td>
                                    <td style="text-align: right; font-weight: bold;">{val:,}</td>
                                    <td style="text-align: right; color: #64748b;">{pct:.1f}%</td>
                                    <td style="vertical-align: middle;">
                                        <div style="width: 100%; background-color: #e2e8f0; border-radius: 4px; height: 8px; overflow: hidden;">
                                            <div style="width: {spark_width:.1f}%; background-color: #f97316; height: 100%; border-radius: 4px;"></div>
                                        </div>
                                    </td>
                                </tr>\n"""
                                
        # Compute category distribution (top 4 categories by count, excluding Regular Days)
        cat_counts = df_matched['category'].value_counts()
        if 'Regular Days' in cat_counts:
            cat_counts = cat_counts.drop('Regular Days')
            
        max_cat = cat_counts.max() if not cat_counts.empty else 1
        for cat, val in list(cat_counts.items())[:4]:
            pct = (val / total_matched_conflicts * 100) if total_matched_conflicts > 0 else 0.0
            spark_width = (val / max_cat * 100) if max_cat > 0 else 0.0
            
            holiday_rows += f"""                                <tr>
                                    <td>{cat}</td>
                                    <td style="text-align: right; font-weight: bold;">{val:,}</td>
                                    <td style="text-align: right; color: #64748b;">{pct:.1f}%</td>
                                    <td style="vertical-align: middle;">
                                        <div style="width: 100%; background-color: #e2e8f0; border-radius: 4px; height: 8px; overflow: hidden;">
                                            <div style="width: {spark_width:.1f}%; background-color: #f97316; height: 100%; border-radius: 4px;"></div>
                                        </div>
                                    </td>
                                </tr>\n"""

        # Compute tactical timing (7-day window around holidays, top 5 by average conflict count per day)
        # Build specific dates list for each year 2011 to 2024
        tactical_dates_by_type = {
            'Mawlid (Id el Maulud)': [],
            'Ramadan End (Eve of Fitr)': [],
            'New Year Period': [],
            'Easter Holiday': [],
            'Eid al-Fitr (Id el Fitr)': [],
            'Ramadan Start': [],
            'Christmas & Boxing Day': [],
            'Workers Day': [],
            'Democracy Day': [],
            'National Day': [],
            'Eid al-Adha (Id el Kabir)': []
        }
        
        for yr in range(2011, 2025):
            tactical_dates_by_type['New Year Period'].append(pd.to_datetime(f'{yr}-01-01'))
            tactical_dates_by_type['Christmas & Boxing Day'].append(pd.to_datetime(f'{yr}-12-25'))
            tactical_dates_by_type['Workers Day'].append(pd.to_datetime(f'{yr}-05-01'))
            tactical_dates_by_type['Democracy Day'].append(pd.to_datetime(f'{yr}-06-12'))
            tactical_dates_by_type['National Day'].append(pd.to_datetime(f'{yr}-10-01'))
            
            # Easter (using Meeus/Jones/Butcher Computus algorithm)
            a = yr % 19
            b = yr // 100
            c = yr % 100
            d = b // 4
            e = b % 4
            f = (b + 8) // 25
            g = (b - f + 1) // 3
            h = (19 * a + b - d - g + 15) % 30
            i = c // 4
            k = c % 4
            L = (32 + 2 * e + 2 * i - h - k) % 7
            m = (a + 11 * h + 22 * L) // 451
            month = (h + L - 7 * m + 114) // 31
            day = ((h + L - 7 * m + 114) % 31) + 1
            tactical_dates_by_type['Easter Holiday'].append(pd.to_datetime(f'{yr}-{month:02d}-{day:02d}'))
            
            # Ramadan start/end
            if yr in ramadan_dates_dict:
                start_str, end_str = ramadan_dates_dict[yr]
                tactical_dates_by_type['Ramadan Start'].append(pd.to_datetime(start_str))
                tactical_dates_by_type['Ramadan End (Eve of Fitr)'].append(pd.to_datetime(end_str))
                
            # Islamic moveable holidays from ng_hols
            for dt_hol, hname in ng_hols.items():
                if dt_hol.year == yr:
                    hname_lower = hname.lower()
                    if 'fitr' in hname_lower and 'holiday' not in hname_lower and 'observed' not in hname_lower:
                        tactical_dates_by_type['Eid al-Fitr (Id el Fitr)'].append(pd.to_datetime(dt_hol))
                    elif 'kabir' in hname_lower and 'holiday' not in hname_lower and 'observed' not in hname_lower:
                        tactical_dates_by_type['Eid al-Adha (Id el Kabir)'].append(pd.to_datetime(dt_hol))
                    elif 'maulud' in hname_lower and 'observed' not in hname_lower:
                        tactical_dates_by_type['Mawlid (Id el Maulud)'].append(pd.to_datetime(dt_hol))
                        
        # Standardize unique date list per category per year
        for key in tactical_dates_by_type:
            dates_df = pd.DataFrame({'date': tactical_dates_by_type[key]})
            dates_df['year'] = dates_df['date'].dt.year
            tactical_dates_by_type[key] = dates_df.groupby('year')['date'].min().tolist()
            
        tactical_results = []
        for event_name, dates in tactical_dates_by_type.items():
            window_days = set()
            for date in dates:
                start_w = date - timedelta(days=3)
                end_w = date + timedelta(days=3)
                curr = start_w
                while curr <= end_w:
                    window_days.add(curr.date())
                    curr += timedelta(days=1)
            
            event_conflicts_df = df_matched[df_matched['date_dt'].dt.date.isin(window_days)]
            num_conflicts = len(event_conflicts_df)
            num_days = len(window_days)
            avg_per_day = num_conflicts / num_days if num_days > 0 else 0.0
            tactical_results.append({
                'name': event_name,
                'conflicts': num_conflicts,
                'avg_per_day': avg_per_day
            })
            
        tactical_results = sorted(tactical_results, key=lambda x: x['avg_per_day'], reverse=True)[:5]
        max_tactical = max([x['avg_per_day'] for x in tactical_results]) if tactical_results else 1.0
        
        tactical_rows = ""
        for res in tactical_results:
            pct = res['avg_per_day']
            spark_width = (pct / max_tactical * 100) if max_tactical > 0 else 0.0
            tactical_rows += f"""                                <tr>
                                    <td>{res['name']}</td>
                                    <td style="text-align: right; font-weight: bold;">{res['conflicts']:,}</td>
                                    <td style="text-align: right; color: #64748b;">{pct:.2f}</td>
                                    <td style="vertical-align: middle;">
                                        <div style="width: 100%; background-color: #e2e8f0; border-radius: 4px; height: 8px; overflow: hidden;">
                                            <div style="width: {spark_width:.1f}%; background-color: #f97316; height: 100%; border-radius: 4px;"></div>
                                        </div>
                                    </td>
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
    <title>Borno, Adamawa and Yobe (BAY) states, Nigeria – Education disruption dashboard</title>
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
            margin-bottom: 10px;
            font-weight: 800;
        }}
        .subtitle {{
            text-align: center;
            font-size: 20px;
            color: #64748b;
            margin-top: 0;
            margin-bottom: 50px;
            font-weight: 600;
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
            border-left: 6px solid #2563eb;
            border-top: 1px solid #dbeafe;
            border-right: 1px solid #dbeafe;
            border-bottom: 1px solid #dbeafe;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.08), 0 2px 4px -1px rgba(37, 99, 235, 0.04);
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
            font-size: 16px;
            font-weight: 700;
            color: #0f172a;
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

        /* Recommendation Styles */
        .recommendation-box {{
            padding: 24px;
            background-color: #f0fdf4;
            border-left: 6px solid #16a34a;
            border-top: 1px solid #dcfce7;
            border-right: 1px solid #dcfce7;
            border-bottom: 1px solid #dcfce7;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.05);
        }}
        .recommendation-title {{
            font-size: 14px;
            font-weight: 800;
            color: #166534;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.75px;
        }}
        .recommendation-text {{
            font-size: 15px;
            color: #14532d;
            line-height: 1.6;
            margin: 0;
            font-weight: bold;
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
            font-size: 12px;
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
        <h1>Borno, Adamawa and Yobe (BAY) states, Nigeria</h1>
        <p class="subtitle">Education disruption dashboard</p>

        <!-- 1. KPI Section -->
        <div class="section-wrapper">
            <div class="kpi-container">
                <div class="kpi-box">
                    <div class="kpi-value">{total_idps:,}</div>
                    <div class="kpi-label">Total IDP Population</div>
                </div>
                <div class="kpi-box" style="background-color: #fef2f2; border: 1px solid #fca5a5; box-shadow: 0 4px 6px -1px rgba(220, 38, 38, 0.05);">
                    <div class="kpi-value" style="color: #dc2626; font-size: 38px;">{pct_idps_top5:.2f}%</div>
                    <div class="kpi-label" style="color: #991b1b;">IDPs in Top 5 LGAs</div>
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
                    This indicates that education disruption is not evenly distributed. A small number of local government authorities (LGAs) — primarily in Borno State — account for the highest levels of risk due to overlapping conflict exposure, large displaced populations, and high school closure rates. EBI should prioritize these areas for immediate education interventions.
                </p>
            </div>
        </div>

        <!-- 3. Embedded Map -->
        <div style="margin: 40px auto; width: 100%; display: flex; flex-direction: column; align-items: center;">
            <div class="section-title" style="width: 100%; text-align: center;">Interactive Education disruption and Risk map</div>
            <p style="font-size: 15px; color: #475569; margin-top: -10px; margin-bottom: 20px; line-height: 1.5; text-align: center; max-width: 800px;">
                These areas require intervention where conflict, displacement, and school closures overlap.
            </p>
            <div class="map-container" style="width: 100%; margin: 0 auto;">
                <iframe src="outputs/maps/education_disruption_map.html?v={int(time.time())}" id="map-iframe" title="Education Disruption Map" style="width: 100%; height: 100%; border: none;"></iframe>
            </div>
        </div>

        <!-- Priority Table Section -->
        <div class="section-wrapper">
            <div class="section-title">Top 10 High-Risk LGAs for immediate intervention</div>
            <p style="font-size: 15px; color: #475569; margin-top: 0; margin-bottom: 15px; line-height: 1.5; text-align: left;">
                These areas require intervention where education disruption is most severe. EBI should prioritize resource allocation to these top 10 high-risk LGAs.
            </p>
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

            <!-- Data Insight -->
            <div style="margin: 20px auto 10px auto; text-align: center; font-size: 16px; color: #0f172a; padding: 12px; background-color: #f1f5f9; border-radius: 6px; border: 1px solid #e2e8f0;">
                <strong>Key finding: These top 10 LGAs account for {pct_risk_top10:.1f}% of total education disruption risk in the BAY states.</strong>
            </div>
        </div>

        <!-- 4. Risk Model Section -->
        <div class="section-wrapper" style="margin-top: 40px;">
            <div class="model-box">
                <div class="model-title">How Risk is calculated</div>
                <div class="formula-box">
                    <div class="formula-text">
                        Risk Score = 30% Conflict + 25% IDP Population + 25% School Closure Rate + 20% School-age Population
                    </div>
                </div>
                <p class="model-explanation">
                    This indicates that children in these LGAs are most at risk of losing access to education due to overlapping pressures.
                </p>
            </div>
        </div>

        <!-- 5. How to Use Section -->
        <div class="section-wrapper">
            <div class="usage-box">
                <div class="usage-title">How to Use This Dashboard</div>
                <ol class="usage-steps">
                    <li class="usage-step">Focus on red (high-risk) LGAs</li>
                    <li class="usage-step">Refer to Top 10 High-Risk LGAs table</li>
                    <li class="usage-step">Check IDP concentration and school closures</li>
                    <li class="usage-step">Use this to guide intervention planning</li>
                </ol>
            </div>
        </div>


        <!-- Recommended Action Section -->
        <div class="section-wrapper">
            <div class="recommendation-box">
                <div class="recommendation-title">Recommended Action</div>
                <p class="recommendation-text">
                    EBI should prioritize resource allocation and rapid education response interventions in the identified high-risk LGAs. Immediate actions should focus on reopening closed schools, supporting displaced children, and restoring access in conflict-affected areas.
                </p>
            </div>
        </div>

        <!-- Future planning Section -->
        <div class="section-wrapper" style="margin-top: 50px;">
            <div class="section-title">Future planning</div>
            <p style="font-size: 15px; color: #475569; margin-top: 0; margin-bottom: 25px; line-height: 1.6; text-align: left;">
                Conflict events in high-risk LGAs often show temporal patterns, suggesting opportunities to identify periods of elevated risk. This approach can be extended to support operational planning, enabling EBI teams to adjust field activities based on risk patterns and improve staff safety.
            </p>
            
            <div style="display: flex; gap: 30px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 300px;">
                    <div style="font-size: 16px; font-weight: bold; color: #0f172a; margin-bottom: 12px;">Conflict Events by Month (Top 6)</div>
                    <div class="table-container">
                        <table class="top-lgas-table">
                            <thead>
                                <tr>
                                    <th>Month</th>
                                    <th style="text-align: right; width: 60px;">Events</th>
                                    <th style="text-align: right; width: 80px;">Percentage</th>
                                    <th style="width: 35%;">Distribution</th>
                                </tr>
                            </thead>
                            <tbody>
{monthly_rows}                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div style="flex: 1; min-width: 300px;">
                    <div style="font-size: 16px; font-weight: bold; color: #0f172a; margin-bottom: 12px;">Holiday / Festival Active (Top 4)</div>
                    <div class="table-container">
                        <table class="top-lgas-table">
                            <thead>
                                <tr>
                                    <th>Period / Festival</th>
                                    <th style="text-align: right; width: 60px;">Events</th>
                                    <th style="text-align: right; width: 80px;">Percentage</th>
                                    <th style="width: 35%;">Distribution</th>
                                </tr>
                            </thead>
                            <tbody>
{holiday_rows}                            </tbody>
                        </table>
                    </div>
                </div>

                <div style="flex: 1; min-width: 300px;">
                    <div style="font-size: 16px; font-weight: bold; color: #0f172a; margin-bottom: 12px;">Tactical Timing: Proximity to Holidays (Top 5)</div>
                    <div class="table-container">
                        <table class="top-lgas-table">
                            <thead>
                                <tr>
                                    <th>Event (7-day window)</th>
                                    <th style="text-align: right; width: 60px;">Events</th>
                                    <th style="text-align: right; width: 80px;">Avg/Day</th>
                                    <th style="width: 35%;">Intensity</th>
                                </tr>
                            </thead>
                            <tbody>
{tactical_rows}                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Operational Recommendation / Highlights -->
            <div style="padding: 16px 20px; background-color: #fef3c7; border-left: 4px solid #d97706; border-radius: 6px; margin-top: 25px;">
                <div style="font-size: 14px; font-weight: 800; color: #92400e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">Operational Recommendation for Field Teams</div>
                <p style="font-size: 14px; color: #78350f; margin: 0; line-height: 1.5;">
                    EBI should restrict travel and enhance safety protocols during the 7-day windows centered around the high-risk events (<strong>Mawlid</strong>, <strong>Ramadan End</strong>, <strong>New Year</strong>, <strong>Easter</strong>, and <strong>Eid al-Fitr</strong>) as conflict intensity significantly increases during these periods.
                </p>
            </div>
        </div>

        <!-- 7. Limitations Section -->
        <div class="section-wrapper" style="margin-bottom: 0;">
            <div class="limitations-box">
                <div class="limitations-title">Limitations</div>
                <ul class="limitations-list">
                    <li class="limitations-item">School status data may be incomplete</li>
                    <li class="limitations-item">IDP data may not reflect recent displacement</li>
                    <li class="limitations-item">Some LGAs may have missing data</li>
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
