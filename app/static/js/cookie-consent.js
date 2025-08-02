document.addEventListener('DOMContentLoaded', function () {
  const banner = document.getElementById('cookie-consent-banner');
  const dismissBtn = document.getElementById('cookie-consent-dismiss');
  const COOKIE_KEY = 'owc_cookie_consent';
  const ONE_DAY_MS = 24 * 60 * 60 * 1000;

  try {
    const lastAccepted = localStorage.getItem(COOKIE_KEY);
    const lastAcceptedTime = parseInt(lastAccepted, 10);
    const now = Date.now();

    const shouldShowBanner =
      !lastAccepted || Number.isNaN(lastAcceptedTime) || now - lastAcceptedTime >= ONE_DAY_MS;

    if (shouldShowBanner) {
      banner.style.display = 'flex';
    }

    dismissBtn?.addEventListener('click', function () {
      try {
        localStorage.setItem(COOKIE_KEY, Date.now().toString());
      } catch (err) {
        console.warn('[CookieConsent] Failed to store consent time:', err);
      }
      banner.style.display = 'none';
    });
  } catch (e) {
    console.warn('[CookieConsent] Script failed:', e);
  }
});
