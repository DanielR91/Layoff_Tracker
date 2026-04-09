# Layoff Tracker Dashboard 📉

A high-performance, real-time dashboard tracking tech industry redundancies, restructuring events, and rumors. Designed with a clean, Bloomberg Terminal-style layout, this application cleanly separates confirmed data from industry noise.

## Features

- **Split-View Architecture**: 
  - **Confirmed Redundancies**: A data-driven table highlighting companies with officially confirmed layoff numbers.
  - **News & Rumors Feed**: A dedicated vertical feed for zero-count reports, rumors, and aggregate industry news, preventing data pollution.
- **Interactive Visualizations**: Powered by Chart.js, the trend line provides an at-a-glance view of industry shifts, reacting dynamically to the selected time horizon (1M, 3M, 6M, 1Y, 2Y).
- **Automated Data Pipeline**: A custom Python scraper automatically fetches the latest news twice daily via GitHub Actions.
- **Intelligent Deduplication**: The backend script parses news headlines via Regex, correctly attributing layoff counts and actively blacklisting "aggregate" reports (e.g., "70,000 jobs lost in Q1") to avoid double-counting.
- **Glassmorphism UI**: Uses a modern dark-mode aesthetic with CSS glassmorphism, glowing accents, and responsive flexbox grids.

## Technical Stack

- **Frontend**: Vanilla HTML, CSS, JavaScript, [Chart.js](https://www.chartjs.org/), [Lucide Icons](https://lucide.dev/)
- **Backend Pipeline**: Python 3 (`xml.etree.ElementTree`, `re`, `urllib`)
- **Automation & Hosting**: GitHub Actions (Cron Jobs) and GitHub Pages

## Project Structure

- `index.html` - The main dashboard view.
- `src/styles/` - CSS configuration, tokens, and component styling.
- `src/scripts/main.js` - Client-side logic for filtering, sorting, rendering, and graph updates.
- `src/scripts/update_data.py` - The automated data scraper that pulls RSS news and intelligently updates the dataset.
- `src/data/layoffs.js` - The source-of-truth dataset exported as a global variable.

*Note: The project leverages a Javascript-based data file (`layoffs.js`) instead of standard JSON to effortlessly bypass local CORS policy restrictions when testing locally.*
