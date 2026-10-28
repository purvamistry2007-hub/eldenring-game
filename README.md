# Elden Ring Arsenal Analytics

Interactive Streamlit dashboard for the supplied 50,000-row, 20-column Elden Ring Excel dataset.

## Files
- `app.py` — Streamlit dashboard application
- `Elden_Ring_PowerBI_Dataset_20_Columns.xlsx` — source dataset
- `requirements.txt` — Python dependencies

## Run locally
Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:
```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy with Streamlit Community Cloud
1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, and the Excel dataset to the repository root.
3. Open Streamlit Community Cloud and connect your GitHub account.
4. Choose the repository, branch, and `app.py` as the main file.
5. Deploy.

Keep the Excel file in the same folder as `app.py`. Do not commit passwords, API keys, or other secrets.

## Dashboard features
- Sidebar filters for weapon type, region, affinity, rarity, damage type, boss loot, base damage, and upgrade level
- KPI cards for record count, average damage, average weight, and boss-loot count
- Charts for weapon types, regions, rarity, affinity, damage distribution, and weight vs damage
- Item search and filtered CSV download
