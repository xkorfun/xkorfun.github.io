(function () {
  var root = document.documentElement;
  var lang = root.lang === 'ko' ? 'ko' : 'en';
  // The EN / 한국어 buttons go to the other language's URL (its hreflang alternate)
  // and remember the choice for assets/lang.js.
  document.querySelectorAll('.lang button').forEach(function (b) {
    b.setAttribute('aria-pressed', String(b.dataset.lang === lang));
    b.addEventListener('click', function () {
      try { localStorage.setItem('lang', b.dataset.lang); } catch (e) {}
      var alt = document.querySelector('link[rel="alternate"][hreflang="' + b.dataset.lang + '"]');
      if (b.dataset.lang !== lang && alt) {
        location.href = new URL(alt.href).pathname +
          location.hash.replace(/^#(en|ko)-/, '#' + b.dataset.lang + '-');
      }
    });
  });
  document.querySelectorAll('.copy').forEach(function (b) {
    b.addEventListener('click', function () {
      var text = b.parentElement.querySelector('code').textContent;
      navigator.clipboard.writeText(text).then(function () {
        var old = b.innerHTML;
        b.textContent = lang === 'ko' ? '복사됨' : 'Copied';
        setTimeout(function () { b.innerHTML = old; }, 1500);
      });
    });
  });
})();
