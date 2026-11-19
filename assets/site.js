// Progressive enhancement only: the page works without it. Theme picker, remembered language, current year.
(function () {
  var root = document.documentElement;
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) {} },
  };

  // Theme: system (default), light or dark. The choice is applied before first paint by the script in <head>.
  var group = document.querySelector(".theme-switch");
  if (group) {
    var buttons = group.querySelectorAll("button[data-theme-value]");
    var sync = function () {
      var pref = store.get("klip-theme") || "system";
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.themeValue === pref)); });
    };
    buttons.forEach(function (b) {
      b.addEventListener("click", function () {
        var v = b.dataset.themeValue;
        if (v === "system") { store.set("klip-theme", null); delete root.dataset.theme; }
        else { store.set("klip-theme", v); root.dataset.theme = v; }
        sync();
      });
    });
    group.hidden = false;
    sync();
  }

  // Language: remember an explicit choice so "/" stops redirecting by browser language.
  document.querySelectorAll("a[data-lang]").forEach(function (a) {
    a.addEventListener("click", function () { store.set("klip-lang", a.dataset.lang); });
  });

  // Early access: build the email (subject and body in the page's language, with the pasted link if any).
  document.querySelectorAll("form[data-capture]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var link = (form.querySelector('input[name="body"]').value || "").trim();
      var body = link ? form.dataset.body.replace("{link}", link) : form.dataset.bodyEmpty;
      window.location.href = "mailto:" + form.dataset.to + "?subject=" + encodeURIComponent(form.dataset.subject) +
        "&body=" + encodeURIComponent(body);
    });
  });

  // Bottom bar: visible while neither the hero form nor the closing section is on screen.
  var dock = document.querySelector("[data-dock]");
  var watched = [document.querySelector(".capture-hero"), document.querySelector(".cta"), document.querySelector(".site-footer")]
    .filter(Boolean);
  if (dock && watched.length && "IntersectionObserver" in window) {
    var visible = new Map();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible.set(en.target, en.isIntersecting); });
      var anyVisible = watched.some(function (el) { return visible.get(el); });
      var past = watched[0].getBoundingClientRect().bottom < 0; // only after scrolling past the hero form
      dock.hidden = anyVisible || !past;
    });
    watched.forEach(function (el) { io.observe(el); });
    window.addEventListener("scroll", function () {
      var anyVisible = watched.some(function (el) { return visible.get(el); });
      dock.hidden = anyVisible || watched[0].getBoundingClientRect().bottom >= 0;
    }, { passive: true });
  }

  var year = document.querySelector("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());
})();
