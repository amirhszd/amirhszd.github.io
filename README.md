# Amir Hassanzadeh — research portfolio

Static website for https://amirhassanzadeh.com. No JavaScript framework or package installation is required. The homepage and project pages work without JavaScript; JavaScript adds the mobile navigation and optional GIF playback controls.

## Update content

- Edit `content/projects.json` for project descriptions, dates, contributions, links, and figure captions.
- Add project media under `assets/projects/<project>/`.
- Replace `assets/docs/Amir-Hassanzadeh-Resume.pdf` to update the résumé download.
- Edit `scripts/build.py` to update the bio, publication list, and shared page structure.
- Edit `assets/site/style.css` to update styling.

Run `python3 scripts/build.py` and commit the generated HTML alongside the source changes. GitHub Pages can serve the repository root directly. Existing images and earlier research are preserved; the News section has been removed.

## Project image layouts

Each project's `image` appears to the right of its title, without a caption, number, or link. That image is automatically omitted from the gallery; its entry in `figures` supplies descriptive alternative text.

Project galleries place all figures in one bounded showcase. Clicking a card—or pressing Enter or Space while it is focused—expands it into a large split view with the complete caption; clicking it again or pressing Escape returns to the grid. Gallery images are intentionally not links, and animation and video controls remain interactive.

## Publication status

The main Landsat manuscript is labeled **in review** based on the supplied résumé. Its Collection 3 integration remains tentative in the project description. Public code links appear only where supplied for the portfolio.

## Attribution

Project descriptions, figures, publication links, and résumé were supplied by Amir Hassanzadeh. Earlier research text and illustrations are preserved from the original website.
