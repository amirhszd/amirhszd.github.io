# Amir Hassanzadeh — research portfolio

Static website for https://amirhszd.github.io. No JavaScript framework or package installation is required. The homepage and project pages work without JavaScript; JavaScript adds the mobile navigation and optional GIF playback controls.

## Update content

- Edit `content/projects.json` for project descriptions, dates, contributions, links, and figure captions.
- Add project media under `assets/projects/<project>/`.
- Replace `assets/docs/Amir-Hassanzadeh-Resume.pdf` to update the résumé download.
- Edit `scripts/build.py` to update the bio, publication list, and shared page structure.
- Edit `assets/site/style.css` to update styling.

Run `python3 scripts/build.py` and commit the generated HTML alongside the source changes. GitHub Pages can serve the repository root directly. Existing images and earlier research are preserved; the News section has been removed.

## Project image layouts

Each project's `image` appears to the right of its title, without a caption or number. Clicking it opens the original. That image is automatically omitted from the gallery; its entry in `figures` retains the original-file link and descriptive alternative text.

Choose the gallery layout in `content/projects.json` using `figure_rows`. Each inner list is one row: one filename makes a one-column row; two filenames make a two-column row. Two-column rows stack on phones. Include every figure except the heading image exactly once. Filenames must match the `src` fields in `figures`.

For example, SST can show the masking video on its own and the reconstructions side by side:

```json
"figure_rows": [
  ["masking-v2.mp4"],
  ["spatial-reconstruction.webp", "spectral-reconstruction.webp"]
]
```

To separate that pair, put each filename in its own inner list. Rebuild with `python3 scripts/build.py`, then commit the JSON and generated project pages to publish the choice. This is an author setting, not a visitor-facing switch; there is no on-page editor. Omitting `figure_rows` defaults to single-column rows.

## Publication status

The main Landsat manuscript is labeled **in review** based on the supplied résumé. Its Collection 3 integration remains tentative in the project description. Public code links appear only where supplied for the portfolio. Original PDFs and images remain available through figure links.

## Attribution

Project descriptions, figures, publication links, and résumé were supplied by Amir Hassanzadeh. Earlier research text and illustrations are preserved from the original website.
