# Education Disruption and Spatial Risk Vulnerability Index
### Adamawa, Borno, and Yobe (BAY) States, Northeast Nigeria

## Live Dashboard

This project presents an interactive dashboard identifying priority LGAs for education intervention in North-East Nigeria.

🔗 **[Explore the Live Interactive Dashboard](https://dubemgsm.github.io/NigeriaBAY/)**

---

## 1. Problem Statement
Northeast Nigeria—specifically the states of Borno, Adamawa, and Yobe (BAY)—has faced over a decade of humanitarian crisis due to conflict and instability. This situation has severely disrupted education access. Schools have been closed, populations displaced, and children left vulnerable. 

This project develops a spatial risk vulnerability map and index at the Local Government Area (LGA) level. It highlights where educational disruption is most severe, helping organizations and decision-makers target resources, prioritize school reopenings, and locate support services.

---

## 2. Data Sources
The analysis utilizes four key input datasets to evaluate risk across the 65 LGAs in the BAY states. Apart from the administrative boundary shapes, all working datasets are sourced from the processed data directory:

*   **Conflict Data (ACLED):** Point-level records of security events (e.g., battles, explosions, violence against civilians) filtered geographically and historically.
    *   *Source file:* `data/processed/conflict.csv` / `data/processed/conflict.geojson`
*   **Displaced Populations (IOM DTM):** Site-level assessment coordinates and internally displaced person (IDP) counts from the International Organization for Migration.
    *   *Source file:* `data/processed/IDP.csv` / `data/processed/IDP.geojson`
*   **School Datasets (GRID3 / iMMAP):** Spatial points containing names and operational status (Open, Closed) of educational facilities.
    *   *Source file:* `data/processed/schools.csv` / `data/processed/schools.geojson`
*   **School-Age Demographics (SADD):** Tabular data detailing school-age children population (boys and girls) per LGA.
    *   *Source file:* `data/processed/school_age_population.csv`
*   **Administrative Boundaries (OCHA):** LGA level polygon shapefiles for Adamawa, Borno, and Yobe states.
    *   *Source file:* `data/clean/nga_shp/nga_admin2.shp`

---

## 3. Methodology
The pipeline processes points, aggregates counts spatially, and calculates a normalized index:

1.  **Spatial Joins:**
    *   Point datasets (Conflict, IDPs, Schools) are projected to WGS 84 (`EPSG:4326`) and joined with LGA boundary polygons to aggregate event counts, total site populations, and school statuses per LGA.
2.  **Indicators & Normalization:**
    *   **School Closure Rate:** `closed_schools / (total_schools + 1)` (to prevent division by zero).
    *   **Conflict Intensity:** Normalized LGA-level conflict count (0 to 1 scale).
    *   **IDP Density:** Normalized LGA-level IDP site population (0 to 1 scale).
    *   **School-Age Density:** Normalized LGA-level school-age children population (0 to 1 scale).
3.  **Risk Score Formulation:**
    *   A composite index is calculated using weighted indicators:
        $$\text{Risk Score} = (\text{Conflict Intensity} \times 0.30) + (\text{IDP Density} \times 0.25) + (\text{School Closure Rate} \times 0.25) + (\text{School-Age Density} \times 0.20)$$
    *   The final risk score is normalized between 0 (lowest disruption risk) and 1 (highest disruption risk).

---

## 4. Key Insight
> [!IMPORTANT]
> **Education disruption is highest where large displaced populations and school closures overlap.**
> LGAs like **Gwoza**, **Bama**, and **Jere** in Borno State exhibit the highest risk scores because they host both massive IDP camps and have high school closure rates combined with high conflict density. Conversely, high-population urban centers like Maiduguri remain vulnerable due to demographic density, even with fewer school closures.

---

## 5. Limitations & Assumptions
*   **Data Gaps:** Point coordinates for schools and conflict events are subject to database collection coverage limits and security challenges in reporting. Some remote areas might have underreported events.
*   **Normalization Assumptions:** Min-Max normalization assumes a linear increase in risk with density. In reality, risk levels might follow non-linear patterns (e.g., threshold effects where risk increases sharply after a certain capacity is reached).
*   **Coordinate Precision:** IDP coordinates were filtered to remove a site recorded outside the BAY states bounding box (located in Taraba State but mislabeled as Yobe).

---

## 6. Outputs and Deliverables

All outputs are saved in the project repository:

1.  **Interactive Choropleth Web Map:**
    *   **Path:** [outputs/maps/education_risk_map.html](file:///workspaces/NigeriaBAY/outputs/maps/education_risk_map.html)
    *   **Features:** Displays LGA vulnerability using a Green (low) $\rightarrow$ Orange $\rightarrow$ Red (high) color scale, overlaying conflict events, IDP sites, and school markers. Zooming and panning is constrained strictly to the BAY states, and LGA boundaries are bordered in black for permanent visibility.
2.  **Consolidated Summary Dataset:**
    *   **Path:** [outputs/maps/final_dataset.csv](file:///workspaces/NigeriaBAY/outputs/maps/final_dataset.csv)
    *   *Columns:* `LGA`, `state`, `risk_score`, `school_age_population`, `idp_population`, `conflict_count`, `closed_schools`
3.  **Top 10 Most Vulnerable LGAs:**
    *   **Path:** [outputs/maps/top_10_lgas.csv](file:///workspaces/NigeriaBAY/outputs/maps/top_10_lgas.csv)
4.  **Local Landing Page Portal:**
    *   **Path:** [index.html](file:///workspaces/NigeriaBAY/index.html) (Serves as the main dashboard containing the embedded map and direct links to the CSV downloads).

---

## Strategy Section

### 1. Context
Over a decade of instability and conflict has severely impacted the education sector in Northeast Nigeria’s Adamawa, Borno, and Yobe (BAY) states. The crisis has resulted in widespread school closures, mass population displacement, and compromised safety, leaving hundreds of thousands of children without access to quality education. To address these challenges systematically, the Education Disruption and Spatial Risk Vulnerability Index has been developed. By consolidating geographic, demographic, and operational data, the platform provides a rigorous, empirical base to guide strategic interventions.

### 2. Objectives
*   **Quantify Spatial Vulnerability:** Establish a localized, LGA-level spatial index mapping educational disruption and security risk.
*   **Target Critical Areas:** Guide the mobilization and allocation of resources to the most affected communities to maximize intervention efficacy.
*   **Coordinate Multi-Sectoral Response:** Support humanitarian actors in planning school rehabilitation, launching temporary learning centers, and integrating displaced children.

### 3. Approach
Our approach centers on a weighted multi-criteria risk model that identifies where education infrastructure, demographics, displacement, and safety pressures overlap. The index evaluates all 65 LGAs in the BAY states based on four indicators:
*   **Conflict Intensity (30% weight):** Assesses the density and frequency of active security incidents (ACLED data) affecting community safety.
*   **IDP Density (25% weight):** Integrates internally displaced person counts (IOM DTM data) to capture high-demand areas.
*   **School Closure Rate (25% weight):** Measures direct impacts on the educational system by tracking non-operational schools.
*   **School-Age Density (20% weight):** Adjusts for the underlying child demographics (SADD data) to ensure interventions match population scale.

**Prioritization Framework:** Resource allocation is optimized by targeting high-risk LGAs. The top 10 highest-risk LGAs (including Gwoza, Maiduguri, Bama, Jere, and Konduga, all located in Borno State) account for **47.6%** of the region's total education disruption risk. Directing interventions to these high-risk areas ensures the most vulnerable populations are reached first.

### 4. Proposed Activities
*   **Prioritized Resource Deployment:** Channel supplies, funding, and teaching staff to the top 10 priority LGAs, starting with highest-vulnerability areas like Gwoza and Bama.
*   **Rehabilitation of Closed Schools:** Coordinate safe school reopening plans with security agencies and community leaders in LGAs where school closure rates are high but security conditions are stabilizing.
*   **IDP Education Support:** Set up temporary learning spaces (TLS) and psychosocial support services in dense displacement hubs such as Maiduguri, Jere, and Monguno.
*   **Risk-Informed Scheduling:** Plan field travel, supply distribution, and community engagement according to temporal conflict trends, minimizing operations during months with historically elevated conflict patterns (e.g., January, February, and November).

### 5. Deliverables
*   **Interactive Spatial Map & Dashboard:** A web-based GIS visualization tool showcasing real-time LGA vulnerability levels, conflict density, and school operational status.
*   **LGA Risk Dataset & Rankings:** A clean, downloadable database containing normalized risk scores and raw parameters for all 65 LGAs.
*   **Targeted Intervention Strategy:** A detailed deployment plan prescribing LGA-specific activities, timeline schedules, and resource distribution budgets.

### 6. Future Planning & Tactical Scheduling
To enhance operational safety and resource efficiency, field deployments and travel should be coordinated around temporal risk patterns identified in the conflict data analysis:
*   **Seasonal Insecurity Windows:** Restrict non-essential field travel and enhance safety measures during months with historically high conflict activity, specifically **January** (10.9% of events), **February** (8.9% of events), and **November** (8.6% of events).
*   **Holiday Proximity Restrictions:** Enhance security protocols and restrict travel during 7-day windows centered around major public and religious events which exhibit elevated daily conflict intensity:
    *   **Mawlid (Id el Maulud)** (Avg: 0.93 events/day)
    *   **Ramadan End (Eve of Fitr)** (Avg: 0.85 events/day)
    *   **New Year Period** (Avg: 0.84 events/day)
    *   **Easter Holiday** (Avg: 0.83 events/day)
    *   **Eid al-Fitr (Id el Fitr)** (Avg: 0.80 events/day)
*   **Dynamic Adaptation:** Integrate monthly security feeds to keep the index dynamically updated, adjusting field deployments as local conflict corridors shift.
