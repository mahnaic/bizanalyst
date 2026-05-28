# BizAnalyst

An AI-powered data analyst built for Bengaluru startups.

BizAnalyst lets founders and operators upload their business data (sales, customers, revenue) and ask questions in plain English. It generates SQL, runs the analysis, and returns clear answers — no analytics team required.

## Who it's for

Early- and growth-stage startups in Bengaluru (and across India) that need quick, accurate answers from their data without hiring a dedicated analyst.

## What it does

- Upload a CSV (sales, transactions, customer data) and start asking questions
- Natural-language to SQL via Claude, executed against your data with DuckDB
- Pandas-powered transformations and summaries
- Tailored to the Indian startup context — INR revenue, city-level breakdowns, common SaaS/D2C patterns

## Stack

- **LLM:** Claude (Anthropic)
- **Query engine:** DuckDB
- **Data manipulation:** Pandas
- **UI:** Streamlit

## Getting started

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your Anthropic API key to a `.env` file
3. Run the Streamlit app:
   ```bash
   streamlit run ai_data_analyst.py
   ```
4. Upload a CSV and start asking questions

## Sample data

`sample_sales.csv` contains 20 rows of synthetic Indian SaaS revenue data across Bengaluru, Mumbai, Chennai, and Hyderabad — useful for trying out the app.
