"""Regression checks for project headings, galleries, and interactive viewers."""
import json
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
            self.assertNotIn('<a ', heading)
            self.assertNotIn('/' + project['image'] + '"', gallery)
            self.assertEqual(gallery.count('<figure '), len(project['figures']) - 1)

    def test_gallery_window_and_playback(self):
        project = BUILD['PROJECTS'][0]
        rendered = BUILD['gallery'](project)
        self.assertIn('gallery-window items-3', rendered)
        self.assertEqual(rendered.count('<figure '), 3)
        self.assertIn('figure-description', rendered)
        self.assertIn('controls autoplay muted loop playsinline', rendered)
        self.assertNotIn('figure-link', rendered)
        self.assertNotIn('Open original', rendered)

    def test_animation_controls_and_empty_gallery(self):
        projects = {p['slug']: p for p in BUILD['PROJECTS']}
        self.assertEqual(BUILD['gallery'](projects['phd']), '')
        rendered = BUILD['gallery'](projects['scene-constructor'])
        self.assertEqual(rendered.count('animation-toggle'), 2)
        self.assertIn('gallery-window items-6', rendered)
        self.assertIn('figure-num">03</span>', rendered)
        self.assertIn('figure-num">05</span>', rendered)
        self.assertIn('data-animation="../assets/projects/scene-constructor/output-v2.gif"', rendered)

    def test_scene_constructor_interactive_demo(self):
        projects = {p['slug']: p for p in BUILD['PROJECTS']}
        rendered = BUILD['interactive_demo'](projects['scene-constructor'])
        self.assertIn('<iframe ', rendered)
        self.assertIn('viewer/index.html', rendered)
        lidar = BUILD['interactive_demo'](projects['lidar'])
        self.assertIn('Interactive 3D Voxelized Forest', lidar)
        self.assertIn('../assets/projects/lidar/viewer/index.html', lidar)
        self.assertEqual(BUILD['interactive_demo'](projects['sst']), '')

    def test_scene_constructor_viewer_bundle(self):
        viewer = ROOT / 'assets/projects/scene-constructor/viewer'
        metadata = json.loads((viewer / 'acquisition.json').read_text())
        index = json.loads((viewer / 'imagery-index.json').read_text())
        bundle_size = (viewer / 'imagery.bin').stat().st_size
        self.assertEqual(len(index), len(metadata['segments']))
        self.assertEqual(index[0]['offset'], 0)
        self.assertEqual(index[-1]['offset'] + index[-1]['length'], bundle_size)

    def test_lidar_viewer_sample(self):
        viewer = ROOT / 'assets/projects/lidar/viewer'
        metadata = json.loads((viewer / 'metadata.json').read_text())
        self.assertEqual((viewer / 'points.bin').stat().st_size, metadata['sample_points'] * metadata['record_bytes'])
        self.assertEqual(metadata['fields'], ['x', 'y', 'z', 'intensity', 'bark', 'leaf', 'soil', 'other'])
        self.assertLess(metadata['sample_points'], metadata['source_points'])

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
