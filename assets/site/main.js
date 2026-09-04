document.documentElement.classList.add('js');
const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('.nav-links');
menu?.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  nav.classList.toggle('open', open);
});
nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
  menu?.setAttribute('aria-expanded', 'false');
  nav.classList.remove('open');
}));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') {
    menu.setAttribute('aria-expanded', 'false'); nav.classList.remove('open'); menu.focus();
  }
});
document.querySelectorAll('.animation-toggle').forEach(button => {
  button.hidden = false;
  const img = document.getElementById(button.getAttribute('aria-controls'));
  const setPlaying = playing => {
    img.src = playing ? img.dataset.animation : img.dataset.still;
    button.setAttribute('aria-pressed', String(playing));
    button.textContent = playing ? 'Stop animation' : 'Play animation';
  };
  setPlaying(!window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  button.addEventListener('click', () => setPlaying(button.getAttribute('aria-pressed') !== 'true'));
});
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.querySelectorAll('video[autoplay]').forEach(video => {
    video.autoplay = false;
    video.pause();
  });
}

document.querySelectorAll('.scientific-showcase-box').forEach(showcase => {
  const cards = [...showcase.querySelectorAll('.sci-card')];

  const collapse = card => {
    card.classList.remove('focused-view');
    card.setAttribute('aria-expanded', 'false');
    card.removeAttribute('style');
    showcase.classList.remove('active-mode');
  };

  const expand = card => {
    const rect = card.getBoundingClientRect();
    const parentRect = showcase.getBoundingClientRect();
    card.style.position = 'absolute';
    card.style.top = `${rect.top - parentRect.top}px`;
    card.style.left = `${rect.left - parentRect.left}px`;
    card.style.width = `${rect.width}px`;
    card.style.height = `${rect.height}px`;
    card.offsetHeight;
    showcase.classList.add('active-mode');
    card.classList.add('focused-view');
    card.setAttribute('aria-expanded', 'true');
  };

  const toggle = card => card.classList.contains('focused-view') ? collapse(card) : expand(card);

  cards.forEach(card => {
    card.addEventListener('click', event => {
      if (event.target.closest('button, video, input, select, a')) return;
      toggle(card);
    });
    card.addEventListener('keydown', event => {
      if ((event.key === 'Enter' || event.key === ' ') && event.target === card) {
        event.preventDefault();
        toggle(card);
      }
    });
  });

  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    const focused = showcase.querySelector('.focused-view');
    if (focused) {
      collapse(focused);
      focused.focus();
    }
  });
});
