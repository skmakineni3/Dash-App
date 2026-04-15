S&P 500 Dash App
Interactive Dash dashboard for exploring historical S&P 500 data, company metadata, and visual analyses.

Status

Development complete for the app itself.
Still working on finding a permanent server to host the live app.
In the meantime, screenshots and detailed descriptions of the app functionality are included in the repository.
Features

Interactive time-series charts for S&P 500 index and individual companies
Company-level filters and selection controls
Aggregations and summary statistics
Download / export options (if enabled in UI)
Responsive layout using Dash + dash-bootstrap-components
Getting started (local)

Clone the repo:
git clone https://github.com/skmakineni3/Dash-App.git
cd "S&P 500 Dash App"

Create a virtual environment and install dependencies:
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
.venv\Scripts\activate       # Windows
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

Provide data

The full dataset (data/sp500_data.csv) is large and tracked with Git LFS. If you don't have the full file, a smaller sample (data/sp500_sample.csv) may be included for demo/testing.
If using the full dataset and Git LFS: ensure git-lfs is installed and run git lfs pull after cloning.
Alternatively, upload the full CSV to an external storage (S3 / Google Drive / GitHub Release) and update the download URL in dash_app.py to fetch at runtime.
Run the app: python dash_app.py Open http://localhost:8050 in your browser.
Deployment notes

I am evaluating hosting options (Render, Heroku, Railway, AWS). The repo uses Git LFS for large data files; some hosts may need extra steps to fetch LFS objects during build. For a reliable deployment I plan to use a CI workflow (GitHub Actions) that checks out with lfs: true and triggers the host deploy.
If you want to host yourself, use:
Render: include runtime.txt (python-3.11.5) and a Procfile: web: gunicorn dash_app:server
Ensure the build installs dependencies and that LFS objects are available to the build (or host the CSV externally and download at runtime).
Included files

dash_app.py — main Dash application
assets/ — CSS / static assets
data/
sp500_data.csv (large; tracked with Git LFS)
sp500_companies.csv (company metadata)
sp500_sample.csv (optional, small sample for demos)
requirements.txt — Python dependencies
Procfile — for Heroku/Render: web: gunicorn dash_app:server
runtime.txt — recommended Python runtime (e.g., python-3.11.5)
screenshots/ — screenshots of the app UI (included)
README.md — this file
Notes for reviewers

If you want to run the app quickly without the full dataset, use the sample CSV or let me know and I can provide a temporary download link.
I welcome feedback on hosting preferences; I will update the README with a live URL once hosting is finalized.
Contact

GitHub: https://github.com/skmakineni3
Email: (use the email on my GitHub profile)
