(function () {
  var root = document.documentElement;
  function setLang(lang) {
    root.lang = lang;
    document.querySelectorAll('.lang button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.lang === lang));
    });
    try { localStorage.setItem('lang', lang); } catch (e) {}
  }
  // ?lang=ko|en in the URL wins, so a link can open a page in a given language.
  var saved = (/[?&]lang=(en|ko)\b/.exec(location.search) || [])[1] || null;
  try { saved = saved || localStorage.getItem('lang'); } catch (e) {}
  setLang(saved || (/^ko\b/i.test(navigator.language || '') ? 'ko' : 'en'));
  document.querySelectorAll('.lang button').forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.dataset.lang); });
  });
  document.querySelectorAll('.copy').forEach(function (b) {
    b.addEventListener('click', function () {
      var text = b.parentElement.querySelector('code').textContent;
      navigator.clipboard.writeText(text).then(function () {
        var old = b.innerHTML;
        b.textContent = root.lang === 'ko' ? '복사됨' : 'Copied';
        setTimeout(function () { b.innerHTML = old; }, 1500);
      });
    });
  });
})();
