"""Regression checks for project headings and configurable figure rows."""
import copy
from html.parser import HTMLParser
from pathlib import Path
import runpy
import unittest
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
BUILD = runpy.run_path(str(ROOT / 'scripts/build.py'))


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('src', 'href', 'data-animation', 'data-still') and value:
                self.urls.append(value)


class LayoutTests(unittest.TestCase):
    def test_all_project_headings(self):
        for project in BUILD['PROJECTS']:
            heading = BUILD['project_heading'](project)
            gallery = BUILD['gallery'](project)
            self.assertIn('<h1>', heading)
            self.assertIn(project['image'], heading)
            self.assertNotIn('figcaption', heading)
            self.assertNotIn('figure-num', heading)
            self.assertNotIn('/' + project['image'] + '"', gallery)
            self.assertEqual(gallery.count('<figure '), len(project['figures']) - 1)

    def test_two_columns_and_playback(self):
        project = copy.deepcopy(BUILD['PROJECTS'][0])
        project['figure_rows'] = [
            ['masking-v2.mp4'],
            ['spatial-reconstruction.webp', 'spectral-reconstruction.webp'],
        ]
        rendered = BUILD['gallery'](project)
        self.assertEqual(rendered.count('figure-row columns-2'), 1)
        self.assertEqual(rendered.count('figure-row columns-1'), 1)
        self.assertIn('controls autoplay muted loop playsinline', rendered)
        for invalid in ([[]], [['missing.webp']], [['masking-v2.mp4']]*3):
            project['figure_rows'] = invalid
            with self.assertRaises(ValueError):
                BUILD['gallery'](project)

    def test_animation_controls_and_empty_gallery(self):
        projects = {p['slug']: p for p in BUILD['PROJECTS']}
        self.assertEqual(BUILD['gallery'](projects['phd']), '')
        rendered = BUILD['gallery'](projects['scene-constructor'])
        self.assertEqual(rendered.count('animation-toggle'), 2)
        pair = rendered.split('<div class="figure-row columns-2">')[1].split('</figure></div>')[0]
        self.assertIn('time-of-day', pair)
        self.assertIn('hexagonal-tiles', pair)
        self.assertIn('figure-num">03</span>', pair)
        self.assertIn('figure-num">05</span>', pair)
        self.assertIn('data-animation="../assets/projects/scene-constructor/output-v2.gif"', rendered)

    def test_local_references(self):
        for page in [ROOT/'index.html', ROOT/'research.html', *sorted((ROOT/'projects').glob('*.html'))]:
            parser = References()
            parser.feed(page.read_text())
            for url in parser.urls:
                parsed = urlsplit(url)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                self.assertTrue((page.parent/unquote(parsed.path)).exists(), f'{page.name}: {url}')


if __name__ == '__main__':
    unittest.main()
