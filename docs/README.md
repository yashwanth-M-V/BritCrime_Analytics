# BritCrime_Analytics — UK Crime Data Intelligence Dashboard**
A data analytics project that transforms large-scale UK crime data from data.police.uk  into actionable insights using Python, SQL, and Power BI. Built an automated ETL pipeline to process last 3 months records, visualize crime hotspots and trends, and deliver real-time intelligence through interactive dashboards.


The **UK Crime Data Intelligence Dashboard** is a data analytics project designed to transform large-scale open UK crime datasets into actionable insights through a fully automated ETL and visualization pipeline.

Using **Python, SQL, and Power BI**, this project demonstrates end-to-end data engineering and analytics skills — from real-world data ingestion to dashboard automation. The system pulls authentic monthly crime data directly from the [UK Police Data API (data.police.uk)](https://data.police.uk/data/), processes over **1 million+ records**, and delivers real-time visual analytics on crime hotspots, category trends, and severity across police forces.

### 🔧 **Key Features**

* **Automated ETL Pipeline:**
  Extracts and ingests raw CSV/ZIP datasets from data.police.uk using Python (`requests`, `zipfile`, `pandas`), performs data cleaning and normalization, and loads the transformed data into a **SQL database** via `SQLAlchemy`.

* **Data Modeling & Storage:**
  Structured schema designed for analytical querying — supports spatial and temporal analysis of crimes by type, region, and month.

* **Interactive Power BI Dashboard:**
  Connects directly to the SQL database to visualize:

  * Crime **hotspots** (geospatial maps)
  * **Monthly and yearly trends** across categories
  * **Force-wise comparisons** and severity patterns

* **Automation & Scheduling:**
  The ETL pipeline runs automatically using Python’s `schedule` library, while Power BI dashboards auto-refresh to keep insights up to date without manual intervention.

### **Technical Stack**

| Component        | Tools / Libraries                              | Purpose                             |
| ---------------- | ---------------------------------------------- | ----------------------------------- |
| Data Source      | [data.police.uk](https://data.police.uk/data/) | Real UK open crime data             |
| ETL & Processing | Python (Pandas, Requests, SQLAlchemy)          | Extract, clean, and load data       |
| Database         | MySQL / PostgreSQL                             | Centralized structured storage      |
| Visualization    | Power BI                                       | Interactive dashboards and insights |
| Automation       | schedule, Power BI refresh                     | Monthly auto-update pipeline        |

### 🚀 **Impact**

* Processed **1M+ rows** of real UK crime data into structured, query-ready format.
* Reduced manual reporting time by **~80%** through full pipeline automation.
* Delivered **real-time, data-driven insights** for policy evaluation and local policing decisions.

### 🧩 **Key Learning Outcomes**

* Practical understanding of **data engineering workflows (ETL → SQL → BI)**.
* Experience integrating **open data APIs** into scalable analytics systems.
* Hands-on with **Power BI dashboards** connected to live SQL databases.
* Built a **production-style automated data refresh pipeline** using Python.

---

Would you like me to now write the **README.md layout** (with sections like *Architecture Diagram*, *How to Run Locally*, *Power BI Preview*, etc.) for your GitHub repo using this description?
That’s what makes your project stand out to recruiters and hiring managers.

