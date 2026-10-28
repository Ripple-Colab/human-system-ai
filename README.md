# The Human System of AI

An animated map of who worked where, who paid whom and who fell out in AI, 2012 to today. Every tie, event, release and value links to its source.

Live at https://lab.ripplecolab.com/ai/. Made by Ripple CoLab.

- `public/` is the site Vercel serves. Nothing in it needs a build step.
- `src/ai-map/` holds the map's source:
    - `data.json`: people, organisations, ties and moments, each with a source
    - `releases.json`: model and product releases, each with a source
    - `values.json`: company values over time, each figure with a source
    - `template.html`: the page
    - `build.py`: puts the data into the page
    - `fetch_faces.py`: fetches portrait photos from Wikipedia, with credits

## Updating the map

1. Edit the JSON files in `src/ai-map/`.
2. Run `python3 src/ai-map/build.py --site public`.
3. Commit and push. Vercel publishes the new version.

## Corrections

Open an issue with a source; see `CONTRIBUTING.md`. Or email mark@ripplecolab.com.

## Licences

- Code: MIT (`LICENSE`).
- Data: CC BY 4.0 (`LICENSE-DATA.md`).
- Photos, fonts, logos and D3: see `CREDITS.md`.
