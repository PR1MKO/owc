# AGENTS.md – Frontend Compliance & Script Tracking

## 🍪 Cookie Consent
- Stored in `localStorage`
- Shown once per 24h
- Script: `/static/js/cookie-consent.js`
- Injected via `base.html`

## 🛂 Age Verification
- Stored in `sessionStorage`
- Shown once per session
- Blocks site interaction
- Script: `/static/js/age-verification.js`
- Injected via `base.html`

## 📊 Analytics / Tracking
- None included yet
- Add section here if future scripts are added