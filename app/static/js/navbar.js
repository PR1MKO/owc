document.addEventListener('DOMContentLoaded', function () {
  const navbarMain = document.getElementById('navbarMain');
  if (!navbarMain) return;

  navbarMain.addEventListener('hide.bs.collapse', function () {
    this.classList.add('collapsing-out');
  });

  navbarMain.addEventListener('hidden.bs.collapse', function () {
    this.classList.remove('collapsing-out');
  });
});
