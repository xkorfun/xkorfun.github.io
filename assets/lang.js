// Loaded in <head> by every page (tools/i18n.py adds it). English URLs serve the
// bilingual source; Korean readers go to the /ko/ page before anything is drawn,
// unless they chose English (?lang=en or the EN button).
(function () {
  if (document.documentElement.lang !== 'en') return;
  var asked = (/[?&]lang=(en|ko)\b/.exec(location.search) || [])[1];
  var saved = null;
  try {
    if (asked) localStorage.setItem('lang', asked);
    saved = localStorage.getItem('lang');
  } catch (e) {}
  var want = asked || saved || (/^ko\b/i.test(navigator.language || '') ? 'ko' : 'en');
  var ko = document.querySelector('link[rel="alternate"][hreflang="ko"]');
  if (want === 'ko' && ko) location.replace(new URL(ko.href).pathname + location.hash.replace(/^#en-/, '#ko-'));
})();
