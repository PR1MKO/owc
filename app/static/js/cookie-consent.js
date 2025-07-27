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
      banner.style.display = 'flex';  // ← force visible
    } else {
      console.log('[CookieConsent] Consent is still valid. Banner stays hidden.');
    }

    dismissBtn?.addEventListener('click', function () {
      const timestamp = Date.now().toString();
      localStorage.setItem(COOKIE_KEY, timestamp);
      banner.style.display = 'none';  // ← now hides correctly
      console.log('[CookieConsent] Dismiss clicked. Stored:', timestamp);
    });
  } catch (e) {
    console.warn("[CookieConsent] Script failed:", e);
  }
});
