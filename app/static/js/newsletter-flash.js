document.addEventListener('DOMContentLoaded', function () {
  var nodes = document.querySelectorAll('.newsletter-flash');
  if (!nodes || !nodes.length) return;
  setTimeout(function () {
    nodes.forEach(function (el) {
      try {
        el.style.transition = 'opacity 300ms';
        el.style.opacity = '0';
        setTimeout(function () {
          if (el && el.parentNode) el.parentNode.removeChild(el);
        }, 320);
      } catch (e) {
        if (el && el.parentNode) el.parentNode.removeChild(el);
      }
    });
  }, 3000);
});