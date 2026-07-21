/* =========================================================
   D Consulting — interactions + EN/HE i18n
   English lives inline in index.html (captured on load);
   Hebrew strings live here. Toggle swaps innerHTML + dir.
   ========================================================= */
(function () {
  "use strict";

  /* ---------- Hebrew dictionary (keys match data-i18n) ---------- */
  var HE = {
    "nav.about": "אודות",
    "nav.services": "שירותים",
    "nav.platform": "הפלטפורמה",
    "nav.blog": "תובנות",
    "nav.approach": "הגישה",
    "nav.results": "תוצאות",
    "nav.contact": "צור קשר",
    "nav.cta": "דברו איתנו",

    "hero.eyebrow": "מפתחים אסטרטגיות חדשניות — משיגים תוצאות",
    "hero.title": "יותר הכנסות מכל ערוץ.",
    "hero.lead": "D Consulting היא חברת ייעוץ לניהול הכנסות, הפצה וטכנולוגיית תיירות עבור תעשיית האירוח. אנחנו משלבים הבנה מעמיקה של השוק עם טכנולוגיה ייחודית, כדי לעזור למלונות ולנכסי אירוח להוביל בעולם הדיגיטלי.",
    "hero.cta1": "לתיאום שיחת ייעוץ",
    "hero.cta2": "לשירותים שלנו",
    "hero.stat1": "גידול ממוצע בהכנסות",
    "hero.stat2": "פתרון דיגיטלי",
    "hero.stat3num": "ישראל ואירופה",
    "hero.stat3": "נכסים שאנו מלווים",
    "hero.card.label": "הכנסות · הרבעון הנוכחי",
    "hero.card.direct": "ישיר",

    "about.kicker": "מי אנחנו",
    "about.h2": "שותפים לצמיחה ולחדשנות בתעשיית האירוח.",
    "about.p1": "מאז 2016, D Consulting היא חברה מובילה בפיתוח עסקי וחדשנות עבור תעשיית האירוח — ומסייעת למקומות אירוח להפוך את ערוצי המכירה המקוונים למנוע צמיחה אמיתי ומדיד.",
    "about.p2": "הגישה שלנו משלבת יצירת פתרונות ייחודיים המותאמים אישית לכל לקוח, יחד עם הידע והניסיון להבטיח את התוצאות הטובות ביותר. אנחנו חלק אינטגרלי מצוות השיווק שלכם — מרמת האסטרטגיה ועד רמת הביצוע — עם מענה מהיר ומיידי לכל שאלה ובקשה.",
    "about.p3": "מה שמניע אותנו הוא הרצון לשנות את הסטטוס קוו: חשיבה יצירתית ולמידה מתמדת. לאורך השנים פיתחנו מגוון שיטות וכלים ייחודיים, המבוססים על הבנה מעמיקה של עולם ההפצה המקוונת וההתנהגות הצרכנית, יחד עם היכרות קרובה עם השוק המקומי.",
    "about.p4": "אנחנו החברה היחידה שמציעה פתרון 360° אמיתי לשיווק הדיגיטלי בתיירות — והתוצאות מדברות בעד עצמן.",
    "about.founderRole": "מייסד ומנכ\"ל",
    "about.tick1": "מאסטרטגיה ועד ביצוע מעשי",
    "about.tick2": "טכנולוגיית הכנסות ייחודית בעלת למידה עצמית",
    "about.tick3": "היכרות עמוקה עם השוק המקומי",
    "about.tick4": "פתרון דיגיטלי 360° אמיתי",

    "services.kicker": "מה אנחנו עושים",
    "services.h2": "השירותים שלנו",
    "services.sub": "פתרון 360° — בחרו את המודולים שאתם צריכים, או תנו לנו לנהל מקצה לקצה.",
    "svc.1.t": "הפצה מקוונת והקמת ערוצים",
    "svc.1.d": "הקמה ואופטימיזציה של הנוכחות שלכם ב-Booking.com, Airbnb, Expedia ועוד — הקמת פרופיל, תכנים, תכניות תעריף וסנכרון מלא ל-PMS / מנהל הערוצים.",
    "svc.2.t": "ניהול הכנסות ותמחור",
    "svc.2.d": "ניהול תשואה ואסטרטגיית תמחור מלאה לכל ערוץ וקהל יעד — בהתחשב במחירים, תפוסות, מוניטין ותקציב, למקסום הרווח.",
    "svc.3.t": "הזמנות ישירות ואתר הבית",
    "svc.3.d": "הגדלת הכנסות ללא עמלות: אופטימיזציה של מנוע ההזמנות, שיפור המרות, קמפיינים ממוקדים ותוכניות נאמנות לאתר שלכם.",
    "svc.4.t": "Meta Search",
    "svc.4.d": "שתופיעו ותוזמנו ישירות דרך Google Hotel Ads, Trivago, TripAdvisor ומנועי מטא נוספים.",
    "svc.5.t": "טכנולוגיה ואנליטיקה",
    "svc.5.d": "כלים ייחודיים בעלי למידה עצמית שחוזים ביקוש, קוראים את נתוני ההזמנות שלכם והופכים אותם להחלטות תמחור והפצה.",
    "svc.6.t": "הדרכות וליווי שוטף",
    "svc.6.d": "הדרכות צוות, דוחות ביצועים שבועיים, דוח חודשי מפורט ופגישות אסטרטגיות שוטפות.",

    "logos.clients": "מלווים מלונות וקבוצות אירוח",
    "logos.platforms": "הערוצים והפלטפורמות שאנחנו מנהלים",

    "platform.kicker": "טכנולוגיה שפיתחנו",
    "platform.h2": "לא מצאנו את הכלים שחיפשנו. אז בנינו אותם.",
    "platform.sub": "רוב חברות הייעוץ עובדות עם מה שהשוק נותן להן. אנחנו נתקלנו שוב ושוב באותן מגבלות — ולכן בנינו מערכות משלנו. הן לומדות מכל נכס, בכל שבוע, ומשתפרות ככל שהן פועלות לאורך זמן.",

    "tool.1.t": "ניהול הכנסות שלומד.",
    "tool.1.d": "מערכת ניהול הכנסות בעלת למידה עצמית, שחוזה ביקוש וממליצה על תמחור לכל נכס בכל שבוע — ואז מבקרת את ההמלצות של עצמה כדי לאתר היכן טעתה.",
    "tool.1.p1": "<b>חיזוי מהנתונים שלכם</b> — עקומות איסוף הזמנות (pickup) שנבנות לכל נכס בנפרד מנתוני OTB רב-שנתיים, ולא מממוצעי שוק גנריים.",
    "tool.1.p2": "<b>מודעוּת לשינויי שוק</b> — המערכת משקללת מחדש את משקל העונות כשהשוק משתנה, כך ששנה חריגה אחת לא מרעילה את המודל.",
    "tool.1.p3": "<b>היא מבקרת את עצמה</b> — שכבת ביקורת ייעודית מנקדת המלצות עבר ומכיילת את המודל אוטומטית.",
    "tool.1.p4": "<b>פועלת לפי לוח זמנים</b> — התהליך השבועי רץ בענן ומגיע כדשבורד מוכן להחלטה.",

    "tool.2.t": "היסטוריית ההזמנות שלכם כבר מכילה את התשובות.",
    "tool.2.d": "אנליטיקת הזמנות שקוראת קובץ ייצוא כמעט מכל מערכת ניהול או ערוץ מכירה, והופכת אותו לתמונה שרוב בעלי הנכסים לא זוכים לראות.",
    "tool.2.p1": "<b>אגנוסטית למקור</b> — מזהה את הפורמט ומנרמלת אותו, כך שנתונים ממערכות שונות הופכים סוף-סוף להשוואתיים.",
    "tool.2.p2": "<b>השאלות שבאמת חשובות</b> — תמהיל ערוצים, מרחק ההזמנה מראש, אורך שהייה, ביצועי סוגי חדרים ועונתיות.",
    "tool.2.p3": "<b>ביטולים, בכימות</b> — היכן באמת נאבדות ההכנסות, לפי ערוץ ולפי חלון ההזמנה.",
    "tool.2.p4": "<b>רצה בדפדפן שלכם</b> — הניתוח מתבצע במחשב שלכם; הנתונים לא עוזבים אותו.",

    "tool.3.tag": "דיווח אוטומטי",
    "tool.3.t": "כל לקוח, אותה משמעת — בכל שבוע.",
    "tool.3.d": "דוחות קצב שבועיים וניתוחי עומק חודשיים נבנים אוטומטית מנתונים חיים, ואז עוברים בדיקה אנושית לפני שהם מגיעים אליכם. העקביות היא המוצר.",
    "tool.3.p1": "<b>קצב שבועי</b> — היכן עומד החודש מול היעד, ומה בדיוק השתנה מאז השבוע שעבר.",
    "tool.3.p2": "<b>ניתוח עומק חודשי</b> — ביצועי ערוצים, תמהיל סוגי חדרים ועמלות, מוצלבים מול נתוני המקור.",
    "tool.3.p3": "<b>כתוב כדי להיקרא</b> — המספרים מגיעים עם הפרשנות, לא כגיליון נתונים גולמי.",
    "tool.3.p4": "<b>נבדק, לא נשלח בעיוורון</b> — האוטומציה מרכיבה; שיקול הדעת נשאר אנושי.",

    "quote.text": "העבודה עם איתי הגדילה את ההכנסות שלנו בלפחות 25%. תשומת הלב שלו לפרטים והידע שלו בשוק האירוח הופכים אותו למיוחד כמנהל הכנסות ושיווק דיגיטלי. איתי, עם העבודה הקשה והשירות האישי המצוין שלך, אתה נכס לכל צוות — ותענוג אמיתי לעבוד איתך.",
    "quote.role": "מנהל מלון · YMCA Three Arches",

    "approach.kicker": "איך אנחנו עובדים",
    "approach.h2": "מהאסטרטגיה ועד הביצוע.",
    "step.1.t": "להבין",
    "step.1.d": "לומדים את הנכס, השוק, תמהיל האורחים והיעדים שלכם — ובונים תכנית שיווק והכנסות מפורטת עם תקציב.",
    "step.2.t": "להקים",
    "step.2.d": "מקימים ומחברים את הערוצים, התכנים, התמחור והטכנולוגיה — נוכחות מקצועית ומסונכרנת מהיום הראשון.",
    "step.3.t": "לייעל",
    "step.3.d": "מנהלים ומשפרים לאורך הערוצים והעונות — להגדלת החשיפה, הנראות והביקוש הישיר.",
    "step.4.t": "לדווח ולצמוח",
    "step.4.d": "דיווח שבועי, ניתוח עומק חודשי ועבודה משותפת עם כל הגורמים הרלוונטיים — תמיד בהתאם לאסטרטגיה.",

    "results.kicker": "במספרים",
    "results.h2": "תוצאות שמדברות בעד עצמן.",
    "results.s1": "גידול ממוצע בהכנסות",
    "results.s2": "כיסוי דיגיטלי",
    "results.s3": "שווקים שאנו פועלים בהם",
    "results.s4": "פועלים מאז",

    "contact.kicker": "צור קשר",
    "contact.h2": "בואו נגדיל את ההכנסות שלכם.",
    "contact.sub": "ספרו לנו על הנכס והיעדים שלכם — נחזור אליכם תוך יום עסקים אחד.",
    "contact.addr": "תל אביב-יפו, ישראל",
    "contact.wa": "שיחה בוואטסאפ",
    "form.name": "שם",
    "form.email": "אימייל",
    "form.phone": "טלפון",
    "form.msg": "איך נוכל לעזור?",
    "form.send": "שליחת הודעה",

    "footer.tag": "מפתחים אסטרטגיות חדשניות · משיגים תוצאות",
    "footer.rights": "כל הזכויות שמורות.",
    "footer.privacy": "מדיניות פרטיות",

    "consent.text": "אנחנו משתמשים בעוגיות אנליטיקס כדי להבין איך משתמשים באתר. בלי פרסום ובלי מכירת מידע. ראו את <a href=\"privacy.html\">מדיניות הפרטיות</a>.",
    "consent.accept": "אישור",
    "consent.decline": "דחייה"
  };

  var STATUS = {
    en: { sending: "Sending…", ok: "Thanks! Your message is on its way — we'll be in touch shortly.",
          mail: "Opening your email app…", err: "Please fill in your name, a valid email and a message." },
    he: { sending: "שולח…", ok: "תודה! ההודעה נשלחה — נחזור אליכם בהקדם.",
          mail: "פותח את אפליקציית המייל…", err: "נא למלא שם, אימייל תקין והודעה." }
  };

  var EN = {};          // captured from DOM
  var nodes = [];       // [{el, key}]
  var lang = "en";

  function captureEN() {
    nodes = [].slice.call(document.querySelectorAll("[data-i18n]"));
    nodes.forEach(function (el) {
      EN[el.getAttribute("data-i18n")] = el.innerHTML;
    });
  }

  function apply(l) {
    lang = (l === "he") ? "he" : "en";
    var dict = (lang === "he") ? HE : EN;
    nodes.forEach(function (el) {
      var k = el.getAttribute("data-i18n");
      var v = (lang === "he") ? (HE[k] != null ? HE[k] : EN[k]) : EN[k];
      if (v != null) el.innerHTML = v;
    });
    var html = document.documentElement;
    html.setAttribute("lang", lang);
    html.setAttribute("dir", lang === "he" ? "rtl" : "ltr");
    [].slice.call(document.querySelectorAll(".langtoggle__opt")).forEach(function (o) {
      o.classList.toggle("is-active", o.getAttribute("data-lang") === lang);
    });
    try { localStorage.setItem("dc_lang", lang); } catch (e) {}
  }

  /* ---------- boot ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    captureEN();
    var saved = "en";
    try { saved = localStorage.getItem("dc_lang") || "en"; } catch (e) {}
    var qp = new URLSearchParams(location.search).get("lang");
    if (qp === "he" || qp === "en") saved = qp;
    apply(saved);

    var yr = document.getElementById("year");
    if (yr) yr.textContent = new Date().getFullYear();

    /* language toggle */
    document.getElementById("langToggle").addEventListener("click", function () {
      apply(lang === "en" ? "he" : "en");
    });

    /* nav: solid on scroll */
    var nav = document.getElementById("nav");
    function onScroll() { nav.classList.toggle("scrolled", window.scrollY > 30); }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    /* mobile menu */
    var burger = document.getElementById("hamburger");
    var links = document.getElementById("navLinks");
    function closeMenu() { links.classList.remove("open"); burger.classList.remove("active"); burger.setAttribute("aria-expanded", "false"); }
    burger.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      burger.classList.toggle("active", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    [].slice.call(links.querySelectorAll("a")).forEach(function (a) {
      a.addEventListener("click", closeMenu);
    });

    /* scrollspy */
    var secs = [].slice.call(document.querySelectorAll("main section[id]"));
    var map = {};
    [].slice.call(document.querySelectorAll(".nav__links a")).forEach(function (a) {
      map[a.getAttribute("href").slice(1)] = a;
    });
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var a = map[e.target.id];
          if (a && e.isIntersecting) {
            for (var id in map) map[id].classList.remove("active");
            a.classList.add("active");
          }
        });
      }, { rootMargin: "-45% 0px -50% 0px" });
      secs.forEach(function (s) { io.observe(s); });
    }

    /* cookie consent — GA4 loads only after an explicit "accept" */
    (function () {
      var box = document.getElementById("consent");
      if (!box) return;
      var KEY = "dc_consent", choice = null;
      try { choice = localStorage.getItem(KEY); } catch (e) {}

      function loadGA() {
        if (!window.DC_GA_ID || window.__dcGaLoaded) return;
        window.__dcGaLoaded = true;
        var s = document.createElement("script");
        s.async = true;
        s.src = "https://www.googletagmanager.com/gtag/js?id=" + window.DC_GA_ID;
        document.head.appendChild(s);
        gtag("js", new Date());
        gtag("config", window.DC_GA_ID, { anonymize_ip: true });
      }
      function decide(v) {
        try { localStorage.setItem(KEY, v); } catch (e) {}
        box.hidden = true;
        if (v === "yes") loadGA();
      }

      if (choice === "yes") loadGA();
      else if (choice !== "no") box.hidden = false;

      document.getElementById("consentYes").addEventListener("click", function () { decide("yes"); });
      document.getElementById("consentNo").addEventListener("click", function () { decide("no"); });
    })();

    /* contact form: Formspree if configured, else mailto fallback */
    var form = document.getElementById("contactForm");
    var statusEl = document.getElementById("formStatus");
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var t = STATUS[lang];
      var name = form.name.value.trim();
      var email = form.email.value.trim();
      var phone = form.phone.value.trim();
      var msg = form.message.value.trim();
      var emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
      statusEl.className = "form__status";
      if (!name || !emailOk || !msg) { statusEl.textContent = t.err; statusEl.classList.add("err"); return; }

      var endpoint = (form.getAttribute("data-formspree") || "").trim();
      if (endpoint) {
        statusEl.textContent = t.sending;
        fetch("https://formspree.io/f/" + endpoint, {
          method: "POST", headers: { "Accept": "application/json" },
          body: new FormData(form)
        }).then(function (r) {
          if (r.ok) { statusEl.textContent = t.ok; statusEl.classList.add("ok"); form.reset(); }
          else { throw new Error("bad"); }
        }).catch(function () {
          statusEl.textContent = t.err; statusEl.classList.add("err");
        });
      } else {
        /* no backend yet → open email client pre-filled */
        var subj = "Website enquiry — " + name;
        var body = "Name: " + name + "\nEmail: " + email + "\nPhone: " + phone + "\n\n" + msg;
        statusEl.textContent = t.mail; statusEl.classList.add("ok");
        window.location.href = "mailto:itai@dconsult.me?subject=" + encodeURIComponent(subj) + "&body=" + encodeURIComponent(body);
      }
    });
  });
})();
