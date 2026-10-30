"""Generate the GitHub Pages portfolio using Python's standard library."""
from pathlib import Path
import html
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / 'content/projects.json').read_text())
# The homepage sequence is curated independently of the detail-page sequence.
HOME_PROJECTS = [
    next(p for p in PROJECTS if p['slug'] == slug)
    for slug in ('sst', 'scene-constructor', 'landsat', 'lidar', 'splash', 'phd', 'jostar')
]
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
    active = 'projects.html' if path.startswith('projects/') or path == 'research.html' else path
    navigation = ''.join(
        f'<a href="{prefix}{url}"' + (' aria-current="page"' if active == url else '') + f'>{label}</a>'
        for url, label in [('index.html', 'about'), ('publications.html', 'publications'),
                           ('projects.html', 'projects'), ('cv.html', 'cv'), ('teaching.html', 'teaching')]
    )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(description)}"><meta name="author" content="Amir Hassanzadeh">
<link rel="canonical" href="{SITE}/{path if path != 'index.html' else ''}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
<script>try{{const t=localStorage.getItem('portfolio-theme');if(t==='dark'||t==='light')document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
<link rel="stylesheet" href="{prefix}assets/site/style.css?v=11"><script src="{prefix}assets/site/main.js?v=4" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="site-header"><nav class="nav wrap" aria-label="Main navigation">
<a class="brand" href="{home}"><strong>Amir</strong> Hassanzadeh</a>
<div class="nav-actions"><button class="theme-toggle" type="button" aria-label="Switch to dark theme" hidden><svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 0 0 16Z" fill="currentColor" stroke="none"/></svg></button>
<button class="menu-toggle" type="button" aria-controls="navigation" aria-expanded="false">Menu</button>
</div><div class="nav-links" id="navigation">{navigation}</div>
</nav></header>
<main id="main">{body}</main>
<footer class="footer"><div class="wrap footer-inner"><span>© 2026 Amir Hassanzadeh. Inspired by <a href="https://alshedivat.github.io/al-folio/">al-folio</a>. Hosted on GitHub Pages.</span><a href="#main">Back to top ↑</a></div></footer></body></html>'''

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
    ('2026','Development of an Uncertainty Workflow to Support Landsat TIRS Split Window-Derived Surface Temperature Products','Remote Sensing of Environment','https://www.sciencedirect.com/science/article/abs/pii/S003442572600430X?via%3Dihub'),
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

def publications(selected=False):
    out = ''
    project_links = {0: 'lidar', 1: 'landsat', 7: 'phd', 9: 'phd', 10: 'phd', 11: 'phd'}
    for i, (year, title, venue, url) in enumerate(PUBLICATIONS[:3] if selected else PUBLICATIONS):
        heading = anchor(url, title) if url else E(title)
        actions = anchor(url, 'Paper', 'pub-button') if url else ''
        if i in project_links:
            actions += anchor(f'projects/{project_links[i]}.html', 'Project', 'pub-button')
        out += f'<li><span class="pub-year">{year}</span><div><h3 class="pub-title">{heading}</h3><p class="pub-venue">{E(venue)}</p><div class="pub-actions">{actions}</div></div></li>'
    return out

home_body = f'''
<div class="wrap academic-home">
<section id="about" class="profile" aria-labelledby="intro-title">
<header class="profile-heading"><h1 id="intro-title"><strong>Amir</strong> Hassanzadeh</h1>
<p class="affiliation">Research Assistant Professor · <a href="https://www.rit.edu/">Rochester Institute of Technology</a></p></header>
<aside class="profile-photo"><img src="assets/site/headshot.jpeg" alt="Amir Hassanzadeh" width="280" height="310" fetchpriority="high"><p>Remote sensing<br>Machine learning<br>Physics-based simulation</p></aside>
<div class="biography"><p>I am a Research Assistant Professor at Rochester Institute of Technology, working at the intersection of <strong>remote sensing, machine learning, and physics-based simulation</strong>. I develop methods and software for extracting meaningful information from satellite, UAV, hyperspectral, thermal, and LiDAR observations.</p>
<p>My current research spans <a href="projects/sst.html">self-supervised hyperspectral representation learning</a>, <a href="projects/landsat.html">Landsat surface-temperature retrieval and uncertainty</a>, and <a href="projects/scene-constructor.html">large-scale DIRSIG scene construction</a>.</p>
<p>I earned my Ph.D. in Imaging Science at RIT in 2022. My doctoral work connected greenhouse spectroscopy with field-scale UAV observations for <a href="projects/phd.html">crop-yield prediction and harvest-maturity assessment</a>.</p>
<p>I teach <a href="teaching.html">Applications of Machine Learning in Remote Sensing</a> and advise graduate and undergraduate researchers.</p></div>
</section>
<section id="contact" class="academic-contact" aria-label="Contact and professional profiles"><div class="social-links">{anchor('mailto:'+EMAIL,'Email')}{anchor(SCHOLAR,'Google Scholar')}{anchor('https://github.com/amirhszd','GitHub')}{anchor('https://www.linkedin.com/in/amirhassanzadeh/','LinkedIn')}{anchor('assets/docs/AmirHassanzadeh_CV.pdf','CV ↓')}</div><p>Research, collaboration, and opportunities: <a href="mailto:{EMAIL}">{EMAIL}</a></p></section>
<section id="research" class="academic-section"><div class="section-heading"><h2>selected projects</h2><a href="projects.html" class="text-link">all projects →</a></div><div class="project-grid featured-grid">{''.join(card(p,i+1) for i,p in enumerate(HOME_PROJECTS[:3]))}</div></section>
<section id="publications" class="academic-section"><div class="section-heading"><h2>selected publications</h2><a href="publications.html" class="text-link">all publications →</a></div><ol class="pub-list">{publications(selected=True)}</ol></section>
</div>'''
(ROOT / 'index.html').write_text(shell('Amir Hassanzadeh | Remote Sensing & Machine Learning', 'Research Assistant Professor at RIT. Remote sensing, foundation models, Landsat surface temperature, DIRSIG simulation, LiDAR, and open-source software.', home_body))

def academic_page(path, title, description, contents):
    body = f'<div class="wrap academic-page"><header class="page-heading"><h1>{title}</h1><p>{description}</p></header>{contents}</div>'
    (ROOT / path).write_text(shell(title.title() + ' | Amir Hassanzadeh', description, body, path))

academic_page('publications.html', 'publications', 'Papers, preprints, and doctoral research in remote sensing and machine learning.',
    f'<p class="page-link">{anchor(SCHOLAR, "View my Google Scholar profile →")}</p><ol class="pub-list full-publications">{publications()}</ol>')
academic_page('projects.html', 'projects', 'Research and software, from learning representations of Earth to simulating the sensors that observe it.',
    '<div class="project-grid">' + ''.join(card(p, i+1) for i,p in enumerate(HOME_PROJECTS)) + '</div><p class="archive-link"><a href="research.html">Earlier research & posters →</a></p>')
academic_page('cv.html', 'curriculum vitae', 'Research, software development, and teaching in imaging science.', '''
<p class="page-link"><a class="button" href="assets/docs/AmirHassanzadeh_CV.pdf">Download full CV (PDF) ↓</a></p>
<section class="cv-section"><h2>experience</h2><dl class="timeline"><div><dt>April 2026–Present</dt><dd><h3>Research Assistant Professor</h3><p>Rochester Institute of Technology</p></dd></div><div><dt>June 2022–April 2026</dt><dd><h3>Researcher / Engineer II</h3><p>Rochester Institute of Technology</p></dd></div></dl></section>
<section class="cv-section"><h2>education</h2><dl class="timeline"><div><dt>2022</dt><dd><h3>Ph.D. in Imaging Science</h3><p>Rochester Institute of Technology</p><p>On the Use of Imaging Spectroscopy from Unmanned Aerial Systems (UAS) to Model Yield and Assess Growth Stages of a Broadacre Crop</p></dd></div></dl></section>
<section class="cv-section"><h2>research interests</h2><p>Self-supervised representation learning · Hyperspectral imaging · Thermal remote sensing · LiDAR · Physics-based simulation · Agricultural monitoring</p></section>
<p class="page-link"><a href="publications.html">Publications →</a> &nbsp; <a href="teaching.html">Teaching →</a></p>''')
academic_page('teaching.html', 'teaching', 'Machine learning for Earth observation and research mentoring.', '''
<section class="teaching-section"><h2>Applications of Machine Learning in Remote Sensing</h2><p class="course-affiliation">Rochester Institute of Technology</p><p>I teach Applications of Machine Learning in Remote Sensing, connecting my work in imaging science and machine learning with the analysis of remotely sensed observations.</p></section>
<section class="teaching-section"><h2>research advising</h2><p>I advise graduate and undergraduate researchers. My research spans hyperspectral representation learning, thermal remote sensing, LiDAR, physics-based simulation, and agricultural monitoring.</p><p>For research and collaboration inquiries, <a href="mailto:amirxhassanzadeh@gmail.com">get in touch</a>.</p></section>''')

def figure(p, f, number):
    base = f"../assets/projects/{p['slug']}/"
    src = base + f['src']
    kind = f.get('kind', 'image')
    extra = ''
    if kind == 'video':
        visual = f'<video autoplay muted loop playsinline preload="metadata" aria-label="{E(f["title"])}"><source src="{src}" type="video/mp4">Video playback is not supported in this browser.</video>'
    elif kind == 'pdf':
        visual = f'<iframe class="pdf-figure" src="{src}#page=1&zoom=page-width" title="Jostar poster"></iframe>'
        extra = '<button class="button fullscreen-toggle" type="button" aria-label="Enter full screen">Full screen ↗</button>'
    elif kind == 'poster':
        visual = f'<img class="poster-figure" src="{src}" alt="Jostar poster" loading="lazy" decoding="async">'
        extra = '<button class="button fullscreen-toggle" type="button" aria-label="Enter full screen">Full screen ↗</button>'
    elif kind == 'animation':
        still = src.replace('.gif', '.webp')
        identifier = f"animation-{number}"
        visual = f'<img id="{identifier}" src="{still}" data-animation="{src}" data-still="{still}" alt="{E(f["title"])}" loading="lazy">'
        extra = f'<button hidden class="button animation-toggle" type="button" aria-controls="{identifier}" aria-pressed="false">Play animation</button>'
    else:
        visual = f'<img src="{src}" alt="{E(f["caption"])}" loading="lazy" decoding="async">'
    css = 'poster-card' if kind == 'poster' else 'pdf-card' if kind == 'pdf' else 'logo' if f['src'] == 'logo.webp' else 'narrow' if f['src'] == 'interface.webp' else ''
    caption = '' if kind == 'pdf' else f'''<figcaption class="sci-caption"><span class="figure-num sci-num">{number:02d}</span><div class="figure-copy"><h3>{E(f['title'])}</h3><p class="figure-description sci-desc">{E(f['caption'])}</p></div></figcaption>'''
    return f'''<figure class="figure sci-card {css}" tabindex="0" aria-expanded="false"><div class="figure-display sci-media">{visual}</div>{extra}{caption}</figure>'''

def project_heading(p):
    hero_image = p.get('header_image', p['image'])
    hero = next((f for f in p['figures'] if f['src'] == hero_image), {})
    css = ' logo' if p['slug'] == 'jostar' else ''
    fit = ' style="overflow:visible"' if p['slug'] == 'sst' else ''
    image_fit = ' style="width:100%;height:auto;max-height:none;object-fit:contain"' if p['slug'] == 'sst' else ''
    return f'''<div class="project-heading project-heading-{E(p['slug'])}"><h1>{E(p['full_title'])}</h1><div class="project-heading-image{css}"{fit}><img src="../assets/projects/{p['slug']}/{E(hero_image)}" alt="{E(hero.get('title', p['title']))}" fetchpriority="high" decoding="async"{image_fit}></div></div>'''

def gallery(p):
    if p['slug'] == 'landsat':
        return ''
    excluded = p.get('gallery_exclude', p['image'])
    figures = {f['src']: f for f in p['figures'] if f['src'] != excluded or f.get('show_in_gallery')}
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
        'landsat': (
            'Interactive Landsat Uncertainty Framework explorer',
            '../assets/projects/landsat/scene-explorer/index.html',
            'Interactive Landsat scene explorer comparing RGB imagery, surface temperature, uncertainty, and estimated total precipitable water across multiple scenes',
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

def news(p):
    item = p.get('news')
    if not item:
        return ''
    return f'''<section class="project-news" aria-labelledby="project-news-title">
<p class="eyebrow">{E(item.get('eyebrow', 'In the news'))}</p>
<div class="project-news-card"><h2 id="project-news-title">{E(item['title'])}</h2><p>{E(item['text'])}</p><a class="text-link" href="{E(item['url'])}" target="_blank" rel="noopener noreferrer">{E(item.get('link_label', 'Read the story'))} ↗</a></div>
</section>'''

for i,p in enumerate(PROJECTS):
    meta = ''.join(f'<span>{E(v)}</span>' for v in [p['dates'],p.get('status','')] if v)
    links = ''.join(anchor(x['url'],x['label']+' ↗','button') for x in p['links'])
    note = f'<p class="publication-note">{E(p["publication_note"])}</p>' if p.get('publication_note') else ''
    next_p = PROJECTS[(i+1)%len(PROJECTS)]
    body=f'''<div class="wrap"><header class="detail-header"><a class="back" href="../projects.html">← All projects</a><p class="eyebrow">{E(p['category'])}</p>{project_heading(p)}<div class="detail-meta">{meta}</div><div class="links">{links}</div>{note}</header>
<div class="detail-overview"><section><h2>Overview</h2><p class="overview-text">{E(p['overview'])}</p></section><aside class="role"><h2>Contribution</h2><ul>{''.join('<li>'+E(x)+'</li>' for x in p['role'])}</ul>{tags(p['tags'])}</aside></div>
{interactive_demo(p)}
{gallery(p)}
{news(p)}
<div class="next-project"><a class="text-link" href="../projects.html">← All projects</a><div><p class="eyebrow">Next project</p><h3><a href="{next_p['slug']}.html">{E(next_p['title'])} ↗</a></h3></div></div></div>'''
    path=f"projects/{p['slug']}.html"
    (ROOT/path).write_text(shell(p['full_title']+' | Amir Hassanzadeh',p['summary'],body,path))

entries=''
for p in EARLIER:
    entries+=f'''<article class="earlier-entry"><h2>{E(p['title'])}</h2><p class="authors">{E(p['authors'])}</p>{anchor(p['url'],'Read paper / poster ↗','button')}<div class="earlier-content"><a href="{p['image']}"><img src="{p['image']}" alt="{E(p['title'])}" loading="lazy"></a><p>{E(p['text'])}</p></div></article>'''
body=f'''<div class="wrap"><header class="detail-header"><a class="back" href="index.html#research">← All projects</a><p class="eyebrow">Research archive</p><h1>Earlier research & posters</h1><p class="summary">Greenhouse and field studies in imaging spectroscopy, crop phenotyping, and yield estimation.</p></header>{entries}</div>'''
(ROOT/'research.html').write_text(shell('Earlier Research | Amir Hassanzadeh','Earlier research, figures, and posters on crop yield, harvest scheduling, hyperspectral sensing, and LiDAR.',body,'research.html'))
print(f'Built homepage, 4 academic pages, {len(PROJECTS)} project pages, and earlier research page.')

# Optional static output for the private review deployment. GitHub Pages serves the root.
out = ROOT / 'out'
if out.exists():
    shutil.rmtree(out)
out.mkdir()
for name in ['index.html', 'publications.html', 'projects.html', 'cv.html', 'teaching.html', 'research.html', '.nojekyll']:
    shutil.copy2(ROOT/name, out/name)
for name in ['projects', 'assets', 'images']:
    shutil.copytree(ROOT/name, out/name)
