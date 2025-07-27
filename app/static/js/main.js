console.log('[OWC] Main JS loaded');
(function() {
  const themeToggle = document.getElementById('theme-toggle');
  if (!themeToggle) return;

  const root = document.documentElement;
  const stored = localStorage.getItem('owc-theme');
  if (stored) {
    root.setAttribute('data-bs-theme', stored);
  }

  themeToggle.addEventListener('click', () => {
    const current = root.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-bs-theme', next);
    localStorage.setItem('owc-theme', next);
  });
})();