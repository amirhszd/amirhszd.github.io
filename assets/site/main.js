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
