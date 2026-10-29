// Progressive enhancements. Links and content remain usable without JavaScript.
const toggle = document.querySelector('.nav-toggle');
const links = document.querySelector('.nav-links');
if(toggle && links) {
  toggle.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  });
  links.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      links.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Open navigation');
    });
  });
}
const year = document.getElementById('year');
if(year) year.textContent = new Date().getFullYear();
if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const elements = document.querySelectorAll('.reveal');
  elements.forEach(el => el.classList.add('will-reveal'));
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if(entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, {threshold: 0.08});
  elements.forEach(el => observer.observe(el));
}
