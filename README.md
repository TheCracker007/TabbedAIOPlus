# TabbedAIOPlus

A simple, automated government jobs aggregator that scrapes multiple sources and displays them in an interactive web dashboard.

## Features

- 🤖 **Automated Scraping** - Runs every 6 hours via GitHub Actions
- 📊 **Multiple Sources** - Aggregates jobs from 4 different websites
- 🎨 **Beautiful UI** - Clean, responsive Bootstrap interface
- 🔍 **Advanced Filtering** - Filter by source, qualification, or search
- 📱 **Mobile Friendly** - Works on all devices
- 🚀 **Zero Backend** - Pure static site hosted on GitHub Pages

## How It Works

1. **GitHub Actions** runs `scraper.py` every 6 hours
2. Script scrapes 4 job websites
3. Data is saved to `jobs.json`
4. Changes are committed automatically
5. **GitHub Pages** serves the static HTML
6. Users see live data in their browser


## File Structure
```
├── scraper.py             # Python scraper script
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
