"""Generate the GitHub Pages portfolio using Python's standard library."""
from pathlib import Path
import html
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / 'content/projects.json').read_text())
EARLIER = json.loads((ROOT / 'content/earlier-research.json').read_text())
E = html.escape
SCHOLAR = 'https://scholar.google.com/citations?user=SlShE9EAAAAJ&hl=en'
EMAIL = 'amirxhassanzadeh@gmail.com'
SITE = 'https://amirhassanzadeh.com'

def anchor(url, label, css=''):
    external = ' target="_blank" rel="noopener noreferrer"' if url.startswith('https://') else ''
    return f'<a href="{E(url)}" class="{css}"{external}>{E(label)}</a>'

def tags(values):
    return '<ul class="tags">' + ''.join(f'<li>{E(v)}</li>' for v in values) + '</ul>'

def shell(title, description, body, path='index.html'):
    prefix = '../' if path.startswith('projects/') else ''
    home = prefix + 'index.html'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(description)}"><meta name="author" content="Amir Hassanzadeh">
<link rel="canonical" href="{SITE}/{path if path != 'index.html' else ''}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:type" content="website">
<link rel="stylesheet" href="{prefix}assets/site/style.css?v=7"><script src="{prefix}assets/site/main.js?v=3" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="site-header"><nav class="nav wrap" aria-label="Main navigation">
<a class="brand" href="{home}">Amir Hassanzadeh<span aria-hidden="true">.</span></a>
<button class="menu-toggle" type="button" aria-controls="navigation" aria-expanded="false">Menu</button>
<div class="nav-links" id="navigation"><a href="{home}#research">Projects</a><a href="{home}#publications">Publications</a><a href="{home}#about">About</a><a href="{home}#contact">Contact</a><a class="nav-resume" href="{prefix}assets/docs/Amir-Hassanzadeh-Resume.pdf">Résumé ↗</a></div>
</nav></header>
<main id="main">{body}</main>
<footer class="footer"><div class="wrap footer-inner"><span>© 2026 Amir Hassanzadeh</span><span>Remote sensing · Machine learning · Simulation</span><a href="#main">Back to top ↑</a></div></footer></body></html>'''

def card(p, index):
    image_class = 'photo' if p['slug'] == 'lidar' else 'logo' if p['slug'] == 'jostar' else ''
    url = f"projects/{p['slug']}.html"
    return f'''<article class="project-card">
<a class="card-image {image_class}" href="{url}" aria-label="Explore {E(p['title'])}"><img src="assets/projects/{p['slug']}/{p['image']}" alt="{E(p['full_title'])}" width="900" height="500" loading="lazy" decoding="async"></a>
<div class="card-meta"><span>{index:02d} / {E(p['category'])}</span><span>{E(p['dates'])}</span></div>
<h3><a href="{url}">{E(p['title'])}</a></h3><p>{E(p['summary'])}</p>
<div class="card-bottom">{tags(p['tags'][:3])}<a class="text-link" href="{url}">Explore project ↗</a></div></article>'''

PUBLICATIONS = [
    ('2026','Deep Imbalanced Multi-Target Regression: 3D Point Cloud Voxel Content Estimation in Simulated Forests','IEEE Transactions on Geoscience and Remote Sensing','https://arxiv.org/pdf/2511.12740'),
    ('2026','Development of an Uncertainty Workflow to Support Landsat TIRS Split Window-Derived Surface Temperature Products','Remote Sensing of Environment · In review · Preprint','https://arxiv.org/pdf/2511.12729'),
    ('2025','Through the Perspective of LiDAR: A Feature-Enriched and Uncertainty-Aware Annotation Pipeline for Terrestrial Point Cloud Segmentation','Preprint','https://arxiv.org/abs/2510.06582'),
    ('2025','Enhancing snap bean yield prediction through synergistic integration of UAS-Based LiDAR and multispectral imagery','Computers and Electronics in Agriculture · 230, 109923',''),
    ('2023','Forecasting Table Beet Root Yield Using Spectral and Textural Features from Hyperspectral UAS Imagery','Remote Sensing · 15(3), 794',''),
    ('2022','Evaluation of Leaf Area Index (LAI) of Broadacre Crops Using UAS-Based LiDAR Point Clouds and Multispectral Imagery','IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing · 15, 4027–4044',''),
    ('2022','On the Use of Imaging Spectroscopy from Unmanned Aerial Systems (UAS) to Model Yield and Assess Growth Stages of a Broadacre Crop','Ph.D. dissertation · Rochester Institute of Technology',''),
    ('2021','Toward Crop Maturity Assessment via UAS-Based Imaging Spectroscopy—A Snap Bean Pod Size Classification Field Study','IEEE Transactions on Geoscience and Remote Sensing · 60, 1–17','https://ieeexplore.ieee.org/abstract/document/9645759'),
    ('2021','Comparison of UAS-Based Structure-from-Motion and LiDAR for Structural Characterization of Short Broadacre Crops','Remote Sensing · 13(19), 3975','https://doi.org/10.3390/rs13193975'),
    ('2021','Broadacre Crop Yield Estimation Using Imaging Spectroscopy from Unmanned Aerial Systems (UAS): A Field-Based Case Study with Snap Bean','Remote Sensing · 13(16), 3241','https://www.mdpi.com/2072-4292/13/16/3241'),
    ('2020','Growth Stage Classification and Harvest Scheduling of Snap Bean Using Hyperspectral Sensing: A Greenhouse Study','Remote Sensing · 12(22), 3809','https://www.mdpi.com/2072-4292/12/22/3809'),
    ('2020','Yield modeling of snap bean based on hyperspectral sensing: a greenhouse study','Journal of Applied Remote Sensing · 14(2), 024519','https://doi.org/10.1117/1.JRS.14.024519'),
]

def publications():
    out = ''
    for year, title, venue, url in PUBLICATIONS:
        heading = anchor(url, title + ' ↗') if url else E(title)
        out += f'<li><span class="pub-year">{year}</span><div><h3 class="pub-title">{heading}</h3><p class="pub-venue">{E(venue)}</p></div></li>'
    return out

home_body = f'''
<section class="wrap hero" aria-labelledby="intro-title">
<div><p class="eyebrow">Earth observation & applied AI</p><h1 id="intro-title">Amir<br>Hassanzadeh<span style="color:var(--accent)">.</span></h1>
<p class="lead">Understanding our world through remote sensing, machine learning, and physical simulation.</p>
<p class="affiliation">Research Assistant Professor<br>Rochester Institute of Technology</p>
<div class="links"><a class="button primary" href="#research">Explore research ↓</a>{anchor(SCHOLAR,'Google Scholar ↗','button')}</div></div>
<figure class="hero-visual"><img src="assets/projects/lidar/harvard-forest.webp" width="1536" height="1024" alt="Aerial view of the simulated Harvard Forest landscape" fetchpriority="high"><figcaption><span>Harvard Forest · DIRSIG simulation</span><a href="projects/lidar.html">View project ↗</a></figcaption></figure>
</section>
<section id="research" class="section"><div class="wrap">
<div class="section-heading"><div><p class="eyebrow">Research & software</p><h2>Selected projects</h2></div><p>From learning representations of Earth to simulating the sensors that observe it.</p></div>
<div class="project-grid">{''.join(card(p,i+1) for i,p in enumerate(PROJECTS))}</div>
<div class="links"><a class="button" href="research.html">Earlier research & posters ↗</a></div>
</div></section>
<section id="publications" class="section pub-section"><div class="wrap">
<div class="section-heading"><div><p class="eyebrow">Papers & collaboration</p><h2>Publications</h2></div>{anchor(SCHOLAR,'Google Scholar ↗','text-link')}</div>
<ol class="pub-list">{publications()}</ol></div></section>
<section id="about" class="section"><div class="wrap about-grid">
<div><p class="eyebrow">About</p><h2 style="margin-top:.8rem">Research meets<br>implementation.</h2><img class="portrait" src="assets/site/headshot.jpeg" alt="Amir Hassanzadeh" width="180" height="180" loading="lazy"><a class="text-link" href="assets/docs/Amir-Hassanzadeh-Resume.pdf">Download résumé ↗</a></div>
<div class="about-copy"><p>Amir Hassanzadeh is a Research Assistant Professor at Rochester Institute of Technology, working at the intersection of remote sensing, machine learning, and physics-based simulation. His work develops methods and software for extracting meaningful information from satellite, drone, hyperspectral, thermal, and LiDAR observations.</p>
<p>Research spans self-supervised geospatial foundation models, Landsat surface-temperature retrieval and uncertainty, large-scale DIRSIG scene construction, and agricultural monitoring. A Ph.D. in Imaging Science from RIT, earned in 2022, connected greenhouse spectroscopy with drone-based crop-yield and harvest-maturity assessment.</p>
<p>Teaching includes <em>Applications of Machine Learning in Remote Sensing</em>, along with graduate and undergraduate research advising. Earlier industry experience at AgerPoint and PrecisionHawk informs a focus on practical, usable research software.</p>
<ul class="background-list"><li><strong>Research Assistant Professor · RIT</strong><span>April 2026 – Present</span></li><li><strong>Researcher / Engineer II · RIT</strong><span>June 2022 – April 2026</span></li><li><strong>Ph.D. in Imaging Science · RIT</strong><span>2022</span></li><li><strong>B.Sc. in Engineering · University of Guilan</strong><span>2016</span></li></ul>
</div></div></section>
<section id="contact" class="contact"><div class="wrap contact-inner"><div><h2>Get in touch</h2><p>Research, collaboration, and opportunities.</p></div><div><a href="mailto:{EMAIL}">{EMAIL}</a><div class="links">{anchor('https://github.com/amirhszd','GitHub ↗','text-link')}{anchor('https://www.linkedin.com/in/amirhassanzadeh/','LinkedIn ↗','text-link')}{anchor(SCHOLAR,'Scholar ↗','text-link')}</div></div></div></section>'''
(ROOT / 'index.html').write_text(shell('Amir Hassanzadeh | Remote Sensing & Machine Learning', 'Research Assistant Professor at RIT. Remote sensing, foundation models, Landsat surface temperature, DIRSIG simulation, LiDAR, and open-source software.', home_body))

def figure(p, f, number):
    base = f"../assets/projects/{p['slug']}/"
    src = base + f['src']
    kind = f.get('kind', 'image')
    extra = ''
    if kind == 'video':
        visual = f'<video autoplay muted loop playsinline preload="metadata" aria-label="{E(f["title"])}"><source src="{src}" type="video/mp4">Video playback is not supported in this browser.</video>'
    elif kind == 'animation':
        still = src.replace('.gif', '.webp')
        identifier = f"animation-{number}"
        visual = f'<img id="{identifier}" src="{still}" data-animation="{src}" data-still="{still}" alt="{E(f["title"])}" loading="lazy">'
        extra = f'<button hidden class="button animation-toggle" type="button" aria-controls="{identifier}" aria-pressed="false">Play animation</button>'
    else:
        visual = f'<img src="{src}" alt="{E(f["caption"])}" loading="lazy" decoding="async">'
    css = 'logo' if f['src'] == 'logo.webp' else 'narrow' if f['src'] == 'interface.webp' else ''
    return f'''<figure class="figure sci-card {css}" tabindex="0" aria-expanded="false"><div class="figure-display sci-media">{visual}</div>{extra}<figcaption class="sci-caption"><span class="figure-num sci-num">{number:02d}</span><div class="figure-copy"><h3>{E(f['title'])}</h3><p class="figure-description sci-desc">{E(f['caption'])}</p></div></figcaption></figure>'''

def project_heading(p):
    hero = next((f for f in p['figures'] if f['src'] == p['image']), {})
    css = ' logo' if p['slug'] == 'jostar' else ''
    fit = ' style="overflow:visible"' if p['slug'] == 'sst' else ''
    image_fit = ' style="width:100%;height:auto;max-height:none;object-fit:contain"' if p['slug'] == 'sst' else ''
    return f'''<div class="project-heading project-heading-{E(p['slug'])}"><h1>{E(p['full_title'])}</h1><div class="project-heading-image{css}"{fit}><img src="../assets/projects/{p['slug']}/{E(p['image'])}" alt="{E(hero.get('title', p['title']))}" fetchpriority="high" decoding="async"{image_fit}></div></div>'''

def gallery(p):
    figures = {f['src']: f for f in p['figures'] if f['src'] != p['image'] or f.get('show_in_gallery')}
    ordered = list(figures)
    if not ordered:
        return ''
    numbers = {src: j + 1 for j, src in enumerate(figures)}
    contents = ''.join(figure(p, figures[src], numbers[src]) for src in ordered)
    return f'<section class="gallery" aria-label="Project figures and demonstrations"><p class="eyebrow">A closer look</p><div class="gallery-window scientific-showcase-box items-{len(ordered)}">{contents}</div></section>'

def interactive_demo(p):
    demos = {
        'scene-constructor': (
            'Landsat Pushbroom Simulation',
            '../assets/projects/scene-constructor/viewer/index.html',
            'Interactive Landsat pushbroom simulation showing a DIRSIG Scene Constructor acquisition over the eastern United States',
        ),
        'lidar': (
            'Interactive 3D Voxelized Forest',
            '../assets/projects/lidar/viewer/index.html',
            'Interactive 3D voxelized point cloud of the simulated Harvard Forest',
        ),
    }
    if p['slug'] not in demos:
        return ''
    title, url, description = demos[p['slug']]
    return f'''<section class="interactive-demo" aria-labelledby="interactive-demo-title">
<div class="interactive-demo-heading"><div><p class="eyebrow">Interactive demonstration</p><h2 id="interactive-demo-title">{E(title)}</h2></div><a class="text-link" href="{E(url)}" target="_blank" rel="noopener noreferrer">Open full screen ↗</a></div>
<iframe src="{E(url)}" title="{E(description)}" loading="eager" allowfullscreen></iframe>
</section>'''

for i,p in enumerate(PROJECTS):
    meta = ''.join(f'<span>{E(v)}</span>' for v in [p['dates'],p.get('status','')] if v)
    links = ''.join(anchor(x['url'],x['label']+' ↗','button') for x in p['links'])
    note = f'<p class="publication-note">{E(p["publication_note"])}</p>' if p.get('publication_note') else ''
    next_p = PROJECTS[(i+1)%len(PROJECTS)]
    body=f'''<div class="wrap"><header class="detail-header"><a class="back" href="../index.html#research">← All projects</a><p class="eyebrow">{E(p['category'])}</p>{project_heading(p)}<div class="detail-meta">{meta}</div><div class="links">{links}</div>{note}</header>
<div class="detail-overview"><section><h2>Overview</h2><p class="overview-text">{E(p['overview'])}</p></section><aside class="role"><h2>Contribution</h2><ul>{''.join('<li>'+E(x)+'</li>' for x in p['role'])}</ul>{tags(p['tags'])}</aside></div>
{interactive_demo(p)}
{gallery(p)}
<div class="next-project"><a class="text-link" href="../index.html#research">← All projects</a><div><p class="eyebrow">Next project</p><h3><a href="{next_p['slug']}.html">{E(next_p['title'])} ↗</a></h3></div></div></div>'''
    path=f"projects/{p['slug']}.html"
    (ROOT/path).write_text(shell(p['full_title']+' | Amir Hassanzadeh',p['summary'],body,path))

entries=''
for p in EARLIER:
    entries+=f'''<article class="earlier-entry"><h2>{E(p['title'])}</h2><p class="authors">{E(p['authors'])}</p>{anchor(p['url'],'Read paper / poster ↗','button')}<div class="earlier-content"><a href="{p['image']}"><img src="{p['image']}" alt="{E(p['title'])}" loading="lazy"></a><p>{E(p['text'])}</p></div></article>'''
body=f'''<div class="wrap"><header class="detail-header"><a class="back" href="index.html#research">← All projects</a><p class="eyebrow">Research archive</p><h1>Earlier research & posters</h1><p class="summary">Greenhouse and field studies in imaging spectroscopy, crop phenotyping, and yield estimation.</p></header>{entries}</div>'''
(ROOT/'research.html').write_text(shell('Earlier Research | Amir Hassanzadeh','Earlier research, figures, and posters on crop yield, harvest scheduling, hyperspectral sensing, and LiDAR.',body,'research.html'))
print(f'Built homepage, {len(PROJECTS)} project pages, and earlier research page.')

# Optional static output for the private review deployment. GitHub Pages serves the root.
out = ROOT / 'out'
if out.exists():
    shutil.rmtree(out)
out.mkdir()
for name in ['index.html', 'research.html', '.nojekyll']:
    shutil.copy2(ROOT/name, out/name)
for name in ['projects', 'assets', 'images']:
    shutil.copytree(ROOT/name, out/name)
