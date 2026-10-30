# Amir Hassanzadeh — research portfolio

Static website for https://amirhassanzadeh.com, with an academic design inspired by [al-folio](https://alshedivat.github.io/al-folio/). This is a custom static implementation of the visual style, rather than the Jekyll theme. No JavaScript framework or package installation is required. Content and navigation work without JavaScript; JavaScript adds the mobile menu, a persistent light/dark theme toggle, and project gallery controls.

## Update content

- Edit `content/projects.json` for project descriptions, dates, contributions, links, and figure captions.
- Add project media under `assets/projects/<project>/`.
- Replace `assets/docs/Amir-Hassanzadeh-Resume.pdf` to update the résumé download.
- Edit `scripts/build.py` to update the bio, publication list, and shared page structure.
- Edit `assets/site/style.css` to update styling.

Run `python3 scripts/build.py` and commit the generated HTML alongside the source changes. GitHub Pages serves the repository root directly. The homepage presents the biography and portrait, selected publications, and featured projects. Dedicated pages contain the full publication list, all seven projects, a CV overview and PDF download, and teaching. Existing project URLs, figures, demonstrations, and earlier research are preserved.

## Project image layouts

Each project's `image` appears to the right of its title, without a caption, number, or link. That image is automatically omitted from the gallery; its entry in `figures` supplies descriptive alternative text.

Project galleries place all figures in one bounded showcase. Clicking a card—or pressing Enter or Space while it is focused—expands it into a large split view with the complete caption; clicking it again or pressing Escape returns to the grid. Gallery images are intentionally not links, and animation and video controls remain interactive.

## Publication status

Publication metadata is maintained in `PUBLICATIONS` in `scripts/build.py`. Its Collection 3 integration remains tentative in the project description. Public code links appear only where supplied for the portfolio.

## Attribution

Project descriptions, figures, publication links, and résumé were supplied by Amir Hassanzadeh. Earlier research text and illustrations are preserved from the original website.
