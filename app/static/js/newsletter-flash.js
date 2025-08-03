// Auto-dismiss newsletter flash messages
// Ensures alerts collapse without leaving residual space

document.addEventListener('DOMContentLoaded', function () {
  const container = document.getElementById('newsletter-flash-container');
  if (!container) {
    return;
  }

  setTimeout(function () {
    const alerts = container.querySelectorAll('.alert');
    alerts.forEach(function (alertEl) {
      const alert = bootstrap.Alert.getOrCreateInstance(alertEl);
      alert.close();
    });
  }, 2000);

  container.addEventListener('closed.bs.alert', function () {
    if (!container.querySelector('.alert')) {
      container.remove();
    }
  });
});