document.addEventListener('DOMContentLoaded', function () {
  const AGE_KEY = 'owc_age_verified';
  const modalEl = document.getElementById('age-verification-modal');
  const yesBtn = document.getElementById('age-yes');
  const noBtn = document.getElementById('age-no');

  if (!modalEl) {
    console.warn('[AgeVerify] Modal element missing');
    return;
  }

  const ageModal = new bootstrap.Modal(modalEl, {
    backdrop: 'static',
    keyboard: false
  });

  try {
    if (!sessionStorage.getItem(AGE_KEY)) {
      ageModal.show();
      console.log('[AgeVerify] Showing modal');
    } else {
      console.log('[AgeVerify] Already verified in this session');
    }

    yesBtn?.addEventListener('click', function () {
      sessionStorage.setItem(AGE_KEY, 'true');
      ageModal.hide();
    });

    noBtn?.addEventListener('click', function () {
      window.location.href = 'https://www.google.com';
    });
  } catch (e) {
    console.warn('[AgeVerify] Script failed:', e);
  }
});