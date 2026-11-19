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

  var year = document.querySelector("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());
})();
