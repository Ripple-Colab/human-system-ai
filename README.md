# Ripple CoLab Lab

Public maps and sketches from Ripple CoLab, served at https://lab.ripplecolab.com.

## The Human System of AI

An animated map of who worked where, who paid whom and who fell out in AI, 2012 to today. It lives at `/ai/`.

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

Email mark@ripplecolab.com. Every item on the map links to its source, so please say which item and which source.

## Credits

- Fonts: Josefin Sans and Karla, SIL Open Font License.
- Charts: D3, ISC licence (`public/vendor/d3-LICENSE.txt`).
- Logos: Simple Icons. Trademarks belong to their owners.
