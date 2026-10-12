/* =========================================================
   D Consulting: blog, author pages and subscription forms.
   - initConsent(): the analytics consent banner for pages that do not load
     script.js (blog articles, blog index, author pages). Same logic and the
     same stored choice ("dc_consent") as the homepage, so a visitor who
     answered once is never asked again. GA4 loads only after "accept".
   - every form[data-subscribe]: posts to the endpoint with fetch (no-cors). The
     response is opaque, so the page cannot tell success from failure; the
     message after sending is worded for that ("if the address is valid").
     without JS the form posts itself (redirect=1) and the endpoint redirects
     to /subscribe/check(-he).html.
   - GA events, sent only when GA is loaded (consent given):
       cta_whatsapp, cta_email, cta_linkedin  {post_slug, lang}
       subscribe_submit                       {post_slug, lang}
   ========================================================= */
(function () {
  "use strict";

  var MSG = {
    en: {
      bad: "Please enter a valid email address.",
      sending: "Sending...",
      ok: "Thanks. If the address is valid, a confirmation link is on its way: check your inbox, and the spam folder too.",
      err: "That did not go through. Please try again, or write to itai@dconsult.me."
    },
    he: {
      bad: "נא להזין כתובת מייל תקינה.",
      sending: "שולח...",
      ok: "תודה. אם הכתובת תקינה, קישור לאישור ההרשמה כבר בדרך: בדקו את תיבת המייל, וגם את תיקיית הספאם.",
      err: "ההרשמה לא נקלטה. נסו שוב, או כתבו לי ל-itai@dconsult.me."
    }
  };

  function pageLang() {
    return document.documentElement.getAttribute("lang") === "he" ? "he" : "en";
  }
  function pageSlug() {
    return (document.body && document.body.getAttribute("data-post")) || "";
  }
  function gaReady() {
    return !!window.__dcGaLoaded && typeof window.gtag === "function";
  }
  function track(name, params) {
    if (!gaReady()) return;              // no consent, no event
    params = params || {};
    params.transport_type = "beacon";
    window.gtag("event", name, params);
  }

  function loadGA() {
    if (!window.DC_GA_ID || window.__dcGaLoaded) return;
    window.__dcGaLoaded = true;
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + window.DC_GA_ID;
    document.head.appendChild(s);
    window.gtag("js", new Date());
    window.gtag("config", window.DC_GA_ID, { anonymize_ip: true });
    /* remember the last post read in this tab, so a contact-form submit on the
       homepage can be credited to it (script.js, contact_submit). Only after
       consent, and only in this tab's session storage. */
    var slug = pageSlug();
    if (slug && slug.charAt(0) !== "(") {
      try { sessionStorage.setItem("dc_from_post", slug); } catch (e) {}
    }
  }

  function initConsent() {
    var box = document.getElementById("consent");
    if (!box) return;
    var KEY = "dc_consent", choice = null;
    try { choice = localStorage.getItem(KEY); } catch (e) {}
    function decide(v) {
      try { localStorage.setItem(KEY, v); } catch (e) {}
      box.hidden = true;
      if (v === "yes") loadGA();
    }
    if (choice === "yes") loadGA();
    else if (choice !== "no") box.hidden = false;
    var yes = document.getElementById("consentYes"), no = document.getElementById("consentNo");
    if (yes) yes.addEventListener("click", function () { decide("yes"); });
    if (no) no.addEventListener("click", function () { decide("no"); });
  }

  /* the three asks: one event name per ask, so GA reports them without setup */
  document.addEventListener("click", function (ev) {
    var t = ev.target;
    var a = t && t.closest ? t.closest("a[data-cta]") : null;
    if (!a) return;
    var kind = a.getAttribute("data-cta");
    if (kind === "whatsapp" || kind === "email" || kind === "linkedin") {
      track("cta_" + kind, { post_slug: pageSlug(), lang: pageLang() });
    }
  });

  function formLang(f) {
    var el = f.elements.namedItem("lang");
    return el && el.value === "he" ? "he" : "en";
  }

  [].forEach.call(document.querySelectorAll("form[data-subscribe]"), function (f) {
    f.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var lang = formLang(f), m = MSG[lang];
      var st = f.querySelector(".subform__status");
      var email = (f.elements.namedItem("email").value || "").trim();
      function say(text, cls) {
        if (!st) return;
        st.textContent = text;
        st.className = "subform__status" + (cls ? " " + cls : "");
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) { say(m.bad, "err"); return; }
      var data = new URLSearchParams(new FormData(f));
      data.delete("redirect");             /* JS path: no redirect page */
      data.set("email", email);
      say(m.sending, "");
      track("subscribe_submit", { post_slug: f.getAttribute("data-slug") || pageSlug(), lang: lang });
      fetch(f.getAttribute("action"), { method: "POST", mode: "no-cors", body: data })
        .then(function () { say(m.ok, "ok"); f.elements.namedItem("email").value = ""; })
        .catch(function () { say(m.err, "err"); });
    });
  });

  window.DC = { track: track, initConsent: initConsent, loadGA: loadGA };
})();
