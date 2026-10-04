# EduPro Learner Analytics

A Streamlit dashboard for **Learner Demographics and Course Enrollment Behavior Analysis on EduPro**.

## Features
- Learner demographic overview
- Age-group and gender analysis
- Course category, type, and level enrollment
- Demographics × course preference heatmaps
- Enrollment behavior KPIs
- Interactive filters

## Data
The `data/` folder contains datasets extracted from the provided EduPro project source PDF:
- users.csv
- courses.csv
- transactions.csv
- teachers.csv

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
