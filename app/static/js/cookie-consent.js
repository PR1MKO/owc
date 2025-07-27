document.addEventListener('DOMContentLoaded', function () {
  const banner = document.getElementById('cookie-consent-banner');
  const dismissBtn = document.getElementById('cookie-consent-dismiss');
  const COOKIE_KEY = 'owc_cookie_consent';
  const ONE_DAY_MS = 24 * 60 * 60 * 1000;

  try {
    const lastAccepted = localStorage.getItem(COOKIE_KEY);
    const lastAcceptedTime = parseInt(lastAccepted, 10);
    const now = Date.now();

    console.log('[CookieConsent] Last accepted:', lastAcceptedTime);
    console.log('[CookieConsent] Now:', now);

    if (!lastAccepted || now - lastAcceptedTime > ONE_DAY_MS) {
      banner.style.display = 'flex';
    } else {
      console.log('[CookieConsent] Consent is still valid. Banner stays hidden.');
    }

    dismissBtn?.addEventListener('click', function () {
      const acceptedAt = Date.now().toString();  // ✅ updated here, not earlier
      localStorage.setItem(COOKIE_KEY, acceptedAt);
      banner.style.display = 'none';
      console.log('[CookieConsent] Dismiss clicked. Stored:', acceptedAt);
    });
  } catch (e) {
    console.warn("[CookieConsent] Script failed:", e);
  }
});
