# TabbedAIOPlus - Government Jobs Portal

A simple, automated government jobs aggregator that scrapes multiple sources and displays them in an interactive web dashboard.

## Features

- 🤖 **Automated Scraping** - Runs every 6 hours via GitHub Actions
- 📊 **Multiple Sources** - Aggregates jobs from 4 different websites
- 🎨 **Beautiful UI** - Clean, responsive Bootstrap interface
- 🔍 **Advanced Filtering** - Filter by source, qualification, or search
- 📱 **Mobile Friendly** - Works on all devices
- 🚀 **Zero Backend** - Pure static site hosted on GitHub Pages

## Data Sources

1. **CareerPower** - careerpower.in
2. **AllGovtJobs** - allgovernmentjobs.in (all jobs)
3. **AllGovtJobs-Filtered** - allgovernmentjobs.in (filtered by education)
4. **SarkariResult** - sarkariresult.app

## Setup

### 1. Fork this repository

### 2. Enable GitHub Actions
- Go to **Settings** → **Actions** → **General**
- Enable "Read and write permissions"

### 3. Enable GitHub Pages
- Go to **Settings** → **Pages**
- Source: **Deploy from a branch**
- Branch: **main** / **root**
- Save

### 4. Manual Trigger (Optional)
- Go to **Actions** tab
- Select **Scrape Government Jobs**
- Click **Run workflow**

## How It Works

1. **GitHub Actions** runs `scraper.py` every 6 hours
2. Script scrapes 4 job websites
3. Data is saved to `jobs.json`
4. Changes are committed automatically
5. **GitHub Pages** serves the static HTML
6. Users see live data in their browser

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run scraper
python scraper.py

# Open index.html in browser
```

## File Structure
```
├── scraper.py              # Python scraper script
├── jobs.json              # Scraped data (auto-generated)
├── index.html             # Main web page
├── app.js                 # Frontend JavaScript
├── requirements.txt       # Python dependencies
├── .github/
│   └── workflows/
│       └── scrape.yml     # GitHub Actions workflow
└── README.md              # This file
```

## License

GNU General Public License v2.0
