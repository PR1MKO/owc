document.addEventListener('DOMContentLoaded', function () {
  const banner = document.getElementById('cookie-consent-banner');
  const dismissBtn = document.getElementById('cookie-consent-dismiss');
  const COOKIE_KEY = 'owc_cookie_consent';
  const ONE_DAY_MS = 24 * 60 * 60 * 1000;

  try {
    const lastAccepted = localStorage.getItem(COOKIE_KEY);
    const now = Date.now();

    if (!lastAccepted || now - parseInt(lastAccepted, 10) > ONE_DAY_MS) {
      banner?.classList.remove('d-none');
    }

    dismissBtn?.addEventListener('click', function () {
      localStorage.setItem(COOKIE_KEY, Date.now().toString());
      banner?.classList.add('d-none');
    });
  } catch (e) {
    console.warn("Cookie consent failed:", e);
  }
});
