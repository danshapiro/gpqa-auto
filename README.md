# GPQA Frontier Autoupdate

- Scrapes a few public benchmark posts for GPQA Diamond scores of current frontier models.
- Regenerates a horizontal bar chart.
- Publishes a lightweight public page via GitHub Pages.
- Runs on a twice-daily GitHub Actions schedule (and on manual dispatch).

## Layout
- `scripts/fetch_gpqa.py` — pulls scores and saves `data/gpqa_scores.json`.
- `scripts/make_chart.py` — renders `img/gpqa_frontier.png`.
- `index.html` — simple landing page that embeds the refreshed chart.
- `.github/workflows/refresh-gpqa.yml` — fetch, chart, commit, and deploy to Pages.

## Adding/adjusting models
Update `SOURCES` and `PROVIDER_BY_MODEL` inside `scripts/fetch_gpqa.py` with new model names or better data sources.

## Local run
```bash
pip install -r requirements.txt
python scripts/fetch_gpqa.py
python scripts/make_chart.py
```

Artifacts land in `data/` and `img/`. The site deploy step copies `index.html` and the chart into the Pages artifact automatically.
