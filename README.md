# ☁️ TechNova GmbH — AWS FinOps Analysis

> **Simulated Cortex Reply FinOps Engagement** | Python · Pandas · Matplotlib · Streamlit

A real-world FinOps data analysis project simulating a consultant engagement at **Cortex Reply**.
The client (TechNova GmbH) saw their AWS bill jump **69% in a single month** with no explanation.
This project identifies the root causes and quantifies **€7,737 in savings opportunities (32% reduction)**.

---

## 📋 Project Overview

| | |
|---|---|
| **Client** | TechNova GmbH (simulated) |
| **Analyst** | Cortex Reply FinOps Team |
| **Period** | January – March 2024 |
| **Cloud** | AWS (eu-central-1) |
| **Tools** | Python, Pandas, Matplotlib, Streamlit |

### The Problem

> *"Our AWS bill jumped from €42,000/month to €71,000/month over the last 3 months and nobody on our side can explain why."*
> — Marcus Weber, CTO TechNova GmbH

### The Objective

1. Clean and merge 3 raw AWS datasets
2. Identify top cost drivers by service and team
3. Find waste — untagged spend, idle resources, uncontrolled storage
4. Quantify savings potential in EUR
5. Deliver a Streamlit dashboard and recommendations report

---

## 📊 Key Findings

### Monthly Cost Trend

![Monthly Cost](charts/chart1_monthly_cost.png)

AWS spend jumped **+69%** from January (€5,744) to February (€9,682) and remained elevated in March (€8,718).
Total 3-month spend: **€24,145**.

---

### Cost by Service

![Cost by Service](charts/chart2_cost_by_service.png)

**EC2 and S3** are the two biggest cost drivers, accounting for **70% of total spend**.
Both spiked in February and showed different patterns — EC2 partially recovered while S3 kept growing.

---

### Cost by Team

![Cost by Team](charts/chart3_cost_by_team.png)

**31% of spend (€7,542) has no team owner** — labeled `untagged`.
The untagged spike in February (€4,753) was the primary driver of the cost increase.
Finance cannot do chargeback on untagged resources.

---

### Savings Opportunities

![Savings Summary](charts/chart4_savings.png)

| # | Finding | Saving | Action |
|---|---------|--------|--------|
| 1 | 31% of spend untagged — no owner | €7,542 | Enforce tagging policy via AWS Config Rules |
| 2 | S3 raw-logs bucket growing 77% | €3,956 | Add S3 lifecycle policy (Glacier after 30 days) |
| 3 | 4 EC2 instances idle on weekends (<10% CPU) | €1,958/yr | AWS Instance Scheduler — auto-shutdown |
| 4 | 100% On-Demand, zero Reserved Instances | €1,822 | Purchase 1-year RIs for EC2 + RDS |
| | **Total** | **€7,737** | **32% cost reduction** |

---

## 🗂️ Project Structure

```
finops-project/
│
├── aws_billing.csv            # AWS Cost & Usage data (126 rows)
├── ec2_usage_metrics.csv      # EC2 CPU & memory utilization (54 rows)
├── resource_inventory.csv     # Resource metadata — owner, team, cost center (42 rows)
│
├── Finops_Data_Analysis.ipynb # Full analysis notebook
├── dashboard.py               # Streamlit dashboard
│
├── charts/                    # Exported chart images
│   ├── chart1_monthly_cost.png
│   ├── chart2_cost_by_service.png
│   ├── chart3_cost_by_team.png
│   └── chart4_savings.png
│
└── README.md
```

---

## 🚀 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/finops-technova.git
cd finops-technova
```

### 2. Install dependencies
```bash
pip install pandas numpy matplotlib streamlit
```

### 3. Run the Jupyter notebook
```bash
jupyter notebook Finops_Data_Analysis.ipynb
```

### 4. Launch the Streamlit dashboard
```bash
streamlit run dashboard.py
```

Dashboard opens at `http://localhost:8501`

---

## 📁 Datasets

| File | Description | Rows | Columns |
|------|-------------|------|---------|
| `aws_billing.csv` | AWS Cost & Usage Report — service, cost, tags, region, pricing term | 126 | 16 |
| `ec2_usage_metrics.csv` | CPU & memory utilization per EC2 instance per month | 54 | 10 |
| `resource_inventory.csv` | Master resource list — owner email, team, cost center, environment | 42 | 10 |

---

## 🔍 Analysis Steps

| Step | Description |
|------|-------------|
| 1. Explore | Understand structure, dtypes, and missing values across all 3 datasets |
| 2. Clean | Fix date types, normalize environment values, fill missing tags, convert USD → EUR |
| 3. Merge | LEFT JOIN billing ← inventory ← usage metrics into one enriched dataframe |
| 4. Analyse | 9 analyses covering cost trends, team allocation, idle resources, RI gap, S3 growth |
| 5. Visualize | 9 matplotlib charts — one per analysis |
| 6. Dashboard | Streamlit app with 5 tabs — Overview, Teams, EC2, S3, Savings |
| 7. Report | Findings, conclusions, and FinOps recommendations |

---

## 💡 FinOps Concepts Covered

- **FinOps Lifecycle** — Inform → Optimize → Operate
- **Showback & Chargeback** — cost allocation by team and cost center
- **Tagging strategy** — identifying and fixing untagged resource spend
- **Rightsizing** — detecting idle and overprovisioned EC2 instances
- **Reserved Instances** — quantifying savings from commitment-based pricing
- **S3 Lifecycle Policies** — identifying uncontrolled storage growth
- **Cost allocation** — splitting shared cloud costs across engineering teams

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.x-green)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.x-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)

---

*This project was built as part of interview preparation for a FinOps Data Analyst & Consultant role at Cortex Reply.*
