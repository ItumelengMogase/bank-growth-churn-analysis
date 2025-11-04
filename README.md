# Bank Growth & Churn Analysis — Senior Data Analyst Case Study

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Visuals-brightgreen)
![SQL](https://img.shields.io/badge/SQL-Analytics%20Models-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Complete-success)

---

**Summary:**  
End-to-end analytics and storytelling project exploring **user acquisition, engagement, churn, and LTV:CAC performance** for a digital bank.  
Built using **Python**, **SQL**, and **dbt-style transformations**, this case study highlights data storytelling, pipeline design, and metric-driven insight generation.

---

## 🗂️ Repository Structure

```bash
bank-growth-churn-analysis/
│
├── data/                       # Raw CSVs (excluded from GitHub)
│   ├── user_acquisition.csv
│   ├── user_activity.csv
│   ├── transactions.csv
│   └── churn.csv
│
├── sql/                        # SQL models
│   ├── 01_context_setup.sql
│   ├── 02_choose_appropriate_visuals.sql
│   ├── 03_eliminate_clutter.sql
│   ├── 04_focus_attention.sql
│   ├── cac_conversion_by_channel.sql
│   ├── churn_composition_dormant_by_channel.sql
│   ├── executive_numbers.sql
│   ├── ltv_proxy.sql
│   ├── ltv_by_channel_user_level.sql
│   ├── monthly_churn.sql
│   └── staging__churn.sql
│
├── visuals/                    # Generated dashboards
│   ├── 01_churn_crisis.html
│   ├── 02_channel_performance.html
│   ├── 03_ltv_cac_ratio.html
│   ├── 04_growth_vs_engagement.html
│   └── executive summary.pptx
│
├── scripts/                    # Python scripts
│   ├── storytelling_visuals.pystorytelling_visuals.py
│   └── load_data.py
│
├── notebooks/                  # Optional exploratory analysis
│   └── analysis.ipynb
│
├── dbt_project.yml             # dbt configuration file
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE

---

## Setup Instructions

### Clone this repository
```bash
git clone https://github.com/<your-username>/bank-growth-churn-analysis.git
cd bank-growth-churn-analysis
````

### Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate         # macOS / Linux
# .venv\Scripts\activate          # Windows PowerShell
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Add your CSV data files

```
data/
├── user_acquisition.csv
├── user_activity.csv
├── transactions.csv
└── churn.csv
```

### Run the main analysis

```bash
python scripts/storytelling_visuals.pystorytelling_visuals.py
```

---

## What the Script Does

The analysis pipeline:

1. Loads all four datasets (**acquisition**, **activity**, **transactions**, **churn**).
2. Calculates:

   * **Customer Acquisition Cost (CAC)** by channel
   * **Monthly churn rate**
   * **Lifetime Value (LTV)** and **LTV:CAC ratio**
   * **Engagement and dormant user composition**
3. Generates:

   * Four **interactive Plotly HTML dashboards**
   * One **PowerPoint executive summary** with KPIs and insights

---

## Deliverables

| Output                         | Description                              |
| ------------------------------ | ---------------------------------------- |
| `01_churn_crisis.html`         | Churn trend & retention crisis overview  |
| `02_channel_performance.html`  | Channel CAC & conversion comparison      |
| `03_ltv_cac_ratio.html`        | LTV:CAC efficiency by channel            |
| `04_growth_vs_engagement.html` | Growth vs engagement correlation         |
| `executive summary.pptx`       | One-slide KPI and recommendation summary |

---

## Key Metrics

| Metric         | Description                                      |
| -------------- | ------------------------------------------------ |
| **CAC**        | Cost of acquiring one new customer per channel   |
| **Churn Rate** | Percentage of users lost within a period         |
| **LTV**        | Estimated revenue per customer lifetime          |
| **LTV:CAC**    | Value-to-cost ratio showing marketing efficiency |

---

## Assumptions

* Dataset covers **Jan–Dec 2024**.
* Some placeholders (e.g., ARPU, spend) are adjustable.
* SQL models follow **dbt-style modular transformations** for production adaptation.

---

## Recommended Workflow

1. Run the script to generate outputs.
2. Review the dashboards (`*.html`) in `/visuals`.
3. Review SQL models for reproducibility in dbt or PostgreSQL.
4. Present findings using `executive summary.pptx`.

---

## Example Insights

* Channels with **high CAC but low retention** are least efficient.
* **Organic and referral channels** have strongest LTV:CAC ratios.
* Engagement dips **precede churn spikes** by ~1 month, revealing lagging indicators.

---

## Author

**Itumeleng Mkhwanazi**
Data & Analytics Engineering Portfolio Project
Contact via GitHub Issues or LinkedIn

---

## License

MIT License © 2025 Itumeleng Mkhwanazi
This project is for educational and portfolio demonstration purposes.

---

## Tech Stack

* **Languages:** Python (Pandas, Plotly), SQL
* **Tools:** dbt, PostgreSQL, Excel, PowerPoint
* **Outputs:** Interactive dashboards, Executive presentation

---

## Badges Legend

| Badge                                                                            | Meaning                                              |
| -------------------------------------------------------------------------------- | ---------------------------------------------------- |
| ![Python](https://img.shields.io/badge/Python-3.9%2B-blue)                       | Project built using Python 3.9+                      |
| ![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Visuals-brightgreen) | Interactive dashboards using Plotly                  |
| ![SQL](https://img.shields.io/badge/SQL-Analytics%20Models-orange)               | Analytical SQL queries and dbt-style transformations |
| ![License](https://img.shields.io/badge/License-MIT-yellow)                      | Open MIT license                                     |
| ![Status](https://img.shields.io/badge/Status-Complete-success)                  | Project complete and reproducible                    |
