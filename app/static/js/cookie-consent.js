document.addEventListener('DOMContentLoaded', function () {
  const banner = document.getElementById('cookie-consent-banner');
  const dismissBtn = document.getElementById('cookie-consent-dismiss');
  const COOKIE_KEY = 'owc_cookie_consent';
  const ONE_DAY_MS = 24 * 60 * 60 * 1000;

  try {
    const lastAccepted = localStorage.getItem(COOKIE_KEY);
    const now = Date.now();

    console.log('[CookieConsent] Last accepted:', lastAccepted);
    console.log('[CookieConsent] Now:', now);

    if (!lastAccepted || now - parseInt(lastAccepted, 10) > ONE_DAY_MS) {
      console.log('[CookieConsent] Showing banner...');
      banner?.classList.remove('d-none');
    } else {
      console.log('[CookieConsent] Consent is still valid. Banner stays hidden.');
    }

    dismissBtn?.addEventListener('click', function () {
      const newTimestamp = Date.now().toString();
      localStorage.setItem(COOKIE_KEY, newTimestamp);
      banner?.classList.add('d-none');
      console.log('[CookieConsent] Dismiss clicked, banner hidden. Stored:', newTimestamp);
    });
  } catch (e) {
    console.warn("[CookieConsent] Script failed:", e);
  }
});
