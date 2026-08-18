#!/usr/bin/env python3
"""
D Consulting — blog build.

Reads  blog/posts/*.md   (front-matter + markdown)
Writes blog/index.html, blog/<slug>.html, blog/feed.xml,
       and — at the SITE ROOT, outside blog/ — sitemap.xml and llms.txt

Also VALIDATES three files it does not write: ../index.html, ../privacy.html and
../sitemap.xml. A ?lang= hreflang cluster in any of them exits 1 before anything
is written, so an exit 1 here can be caused by a file outside blog/.

Front-matter keys:
  title, date (YYYY-MM-DD), lang (en|he), tags (comma separated),
  excerpt, image (optional, path relative to site root), slug (optional)

This is the target the content agent will write into: drop a .md file in
posts/, run this, publish. No CMS, no database.

Requires: pip install markdown
"""
import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from html.parser import HTMLParser

try:
    import markdown as md_lib
except ImportError:
    sys.exit("Missing dependency. Run:  pip3 install markdown")

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(HERE, "posts")
SITE = "https://dconsult.me"
# Local, not UTC, so it lines up with git's `%as` (which is the author's local
# date). A UTC "today" can name the day before the commit that carries it.
TODAY = datetime.now().strftime("%Y-%m-%d")

# blog/index.html has ONE URL. Its language is switched client-side with ?lang=,
# so /blog/?lang=en and /blog/?lang=he return byte-identical HTML and both
# canonicalise to /blog/. An hreflang cluster whose members are not canonical
# URLs in their own right is invalid, so Google discards it. Removing it
# withdraws a false declaration — it does not remove a URL, because the ?lang=
# links are still in the markup and the canonical is what consolidates them.
# The accepted cost is that /blog/ now carries no Hebrew targeting signal at all,
# which is the right trade for a page whose Hebrew has no address of its own.
# The per-language ARTICLES do have real URLs (-he.html) and keep their
# hreflang, which is valid there.
INDEX_HREFLANG_NOTE = (
    "<!-- No hreflang: the index switches language client-side via ?lang=, so those\n"
    "     URLs are not canonical and the cluster was invalid. See ../index.html\n"
    "     (site root) for the full reasoning. -->"
)

UI = {
    "en": {
        "back": "← All articles", "home": "← Back to site", "blog": "Insights",
        "kicker": "Insights", "title": "Notes from the front line of hospitality distribution.",
        "sub": "What we're seeing in the market, in the channels, and in the data — written for people who run properties.",
        "empty": "First articles coming shortly.", "read": "Read article",
        "min": "min read", "by": "By",
        "n_about": "About", "n_services": "Services", "n_platform": "Platform",
        "n_approach": "Approach", "n_insights": "Insights", "n_contact": "Contact",
        "n_cta": "Let's talk", "other": "עברית",
    },
    "he": {
        "back": "→ כל המאמרים", "home": "→ חזרה לאתר", "blog": "תובנות",
        "kicker": "תובנות", "title": "מהשטח של עולם ההפצה והאירוח.",
        "sub": "מה אנחנו רואים בשוק, בערוצים ובנתונים — נכתב עבור מי שמנהל נכסים בפועל.",
        "empty": "המאמרים הראשונים יעלו בקרוב.", "read": "לקריאת המאמר",
        "min": "דק' קריאה", "by": "מאת",
        "n_about": "אודות", "n_services": "שירותים", "n_platform": "הפלטפורמה",
        "n_approach": "הגישה", "n_insights": "תובנות", "n_contact": "צור קשר",
        "n_cta": "דברו איתנו", "other": "English",
    },
}


def parse_front_matter(raw):
    """Minimal front-matter parser: --- key: value --- then body."""
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    if end == -1:
        return {}, raw
    head, body = raw[3:end], raw[end + 4:]
    meta = {}
    for line in head.strip().splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body.lstrip("\n")


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE).strip().lower()
    return re.sub(r"[\s_-]+", "-", s) or "post"


def valid_date(raw, fn):
    """A front-matter date, or None with a printed reason.

    Checked, not trusted, because this one hand-typed string reaches four
    machine-read fields: <lastmod>, <pubDate>, datePublished and dateModified.
    `2026-7-21` looks fine and strptime("%m") even accepts it, but it is not a
    valid W3C datetime AND it sorts ABOVE every real 2026-1x date, so the
    lastmod floor below would pin that article's date forever — silently, at
    exit 0. A missing date used to default to 1970-01-01 and print nothing,
    which put "1970-01-01" on a page a client can read.
    """
    if not raw:
        print(f"  ! skipping {fn}: no date (add `date: YYYY-MM-DD`)")
        return None
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        print(f"  ! skipping {fn}: date {raw!r} is not YYYY-MM-DD")
        return None
    try:
        datetime.strptime(raw, "%Y-%m-%d")           # rejects 2026-13-45
    except ValueError:
        print(f"  ! skipping {fn}: date {raw!r} is not a real date")
        return None
    return raw


def read_posts():
    """Returns (posts, skipped). A skipped post is a FAILURE, not a warning.

    A .md that cannot be built silently disappears from the blog index, the
    feed, llms.txt and the sitemap — an article withdrawn from the site and from
    Google, at exit 0, reported only by a line that scrolls past. main() refuses
    to write anything while `skipped` is non-empty. To take a post out on
    purpose, rename it so it no longer ends in .md.
    """
    posts, skipped = [], []
    if not os.path.isdir(POSTS_DIR):
        return posts, skipped
    for fn in sorted(os.listdir(POSTS_DIR)):
        if not fn.endswith(".md"):
            continue
        raw = open(os.path.join(POSTS_DIR, fn), encoding="utf-8").read()
        meta, body = parse_front_matter(raw)
        if not meta.get("title"):
            print(f"  ! skipping {fn}: no title")
            skipped.append(fn)
            continue
        date = valid_date(meta.get("date"), fn)
        if not date:
            skipped.append(fn)
            continue
        if date > TODAY:
            print(f"  ! {fn}: date {date} is in the future; lastmod floored at {TODAY}")
        lang = (meta.get("lang") or "en").lower()
        slug = meta.get("slug") or slugify(meta["title"])
        words = len(re.findall(r"\w+", body, flags=re.UNICODE))
        posts.append({
            "file": fn,
            "title": meta["title"],
            "date": date,
            "lang": lang if lang in ("en", "he") else "en",
            "tags": [t.strip() for t in (meta.get("tags") or "").split(",") if t.strip()],
            "excerpt": meta.get("excerpt", ""),
            "image": meta.get("image", ""),
            "author": meta.get("author", "Itai Gal"),
            "base": slug,
            "slug": f"{slug}-{lang}" if lang == "he" else slug,
            # Modification date of the SOURCE, not of the rendered file. Google
            # asks lastmod to track the main content; a nav or template change
            # rewrites every article without changing a word any reader reads,
            # and claiming otherwise is how a site teaches Google to ignore the
            # field. Floored at the publish date so it can never run backwards —
            # and the floor itself is capped at today, so a future-dated post
            # cannot pin its own lastmod ahead of every subsequent edit. When git
            # cannot answer, the publish date is the honest fallback, not today.
            "lastmod": max(min(date, TODAY),
                           lastmod(os.path.join("posts", fn)) or date),
            "body_html": md_lib.markdown(body, extensions=["extra", "sane_lists"]),
            "words": words,
            "minutes": max(1, round(words / 200)),
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts, skipped


def head(title, desc, lang, canonical, image="", alts=None, switch=None,
         hreflang_note=None):
    rtl = ' dir="rtl"' if lang == "he" else ' dir="ltr"'
    og_img = f"{SITE}/{image}" if image else f"{SITE}/assets/og.jpg"
    u = UI[lang]
    switch_html = (
        f'\n      <a class="langtoggle" href="{switch}" '
        f'aria-label="Switch language">{html.escape(u["other"])}</a>'
        if switch else ""
    )
    # keep the visitor's language when they head back to the main site
    home = "../?lang=he" if lang == "he" else "../"

    def _nl(href, key, cls=""):
        c = f' class="{cls}"' if cls else ""
        return (f'<a href="{href}"{c} data-en="{html.escape(UI["en"][key])}"'
                f' data-he="{html.escape(UI["he"][key])}">{html.escape(u[key])}</a>')

    nav_links = "\n      ".join([
        _nl(f"{home}#about", "n_about"),
        _nl(f"{home}#services", "n_services"),
        _nl(f"{home}#platform", "n_platform"),
        _nl(f"{home}#approach", "n_approach"),
        _nl("./", "n_insights", "active"),
        _nl(f"{home}#contact", "n_contact"),
    ])
    cta = _nl(f"{home}#contact", "n_cta", "btn btn--sm btn--primary")

    if alts and hreflang_note:
        raise ValueError("head(): pass alts OR hreflang_note, not both — "
                         "the note would be dropped silently.")
    hreflang = "".join(
        f'\n<link rel="alternate" hreflang="{l}" href="{u}">' for l, u in (alts or [])
    )
    if alts:
        hreflang += f'\n<link rel="alternate" hreflang="x-default" href="{alts[0][1]}">'
    elif hreflang_note:
        # A page with no real per-language URL still deserves an explanation in the
        # markup, so nobody "restores" the hreflang block that was removed on purpose.
        hreflang = f"\n{hreflang_note}"
    return f"""<!DOCTYPE html>
<html lang="{lang}"{rtl}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">{hreflang}
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="D Consulting — Insights" href="{SITE}/blog/feed.xml">
<link rel="icon" type="image/png" href="../assets/icon-512.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,500&family=Inter:wght@400;500;600;700&family=Heebo:wght@400;500;700&family=Frank+Ruhl+Libre:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../styles.css">
</head>
<body class="subpage">

<!-- full site nav, so the reader never feels they have left the site -->
<header class="nav scrolled" id="nav">
  <div class="container nav__inner">
    <a href="{home}" class="brand" aria-label="D Consulting home">
      <img class="brand__logo brand__logo--light" src="../assets/logo-light.png" alt="D Consulting" width="465" height="140">
    </a>
    <nav class="nav__links" id="navLinks" aria-label="Primary">
      {nav_links}
    </nav>
    <div class="nav__actions">{switch_html}
      {cta}
      <button class="hamburger" id="hamburger" type="button" aria-label="Menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>

<p class="crumbs"><a href="{home}">D Consulting</a> <span>/</span> <a href="./" data-en="{html.escape(UI['en']['n_insights'])}" data-he="{html.escape(UI['he']['n_insights'])}">{html.escape(u['n_insights'])}</a></p>
"""


def foot(lang):
    u = UI[lang]
    return f"""<footer class="footer">
  <div class="container footer__inner">
    <div class="footer__brand">
      <img class="footer__logo" src="../assets/logo-dark.png" alt="D Consulting" width="465" height="140" loading="lazy">
      <p class="footer__tag">Developing innovative strategies &middot; Achieving success</p>
    </div>
    <nav class="footer__links" aria-label="Footer">
      <a href="../#about">{html.escape(u['n_about'])}</a>
      <a href="../#services">{html.escape(u['n_services'])}</a>
      <a href="../#platform">{html.escape(u['n_platform'])}</a>
      <a href="./">{html.escape(u['n_insights'])}</a>
      <a href="../#contact">{html.escape(u['n_contact'])}</a>
    </nav>
  </div>
  <div class="container footer__bottom">
    <span>&copy; <span id="year">2026</span> D Consulting.</span>
    <a class="footer__privacy" href="../privacy.html">Privacy</a>
  </div>
</footer>
<script>
document.getElementById('year').textContent = new Date().getFullYear();
(function () {{
  var b = document.getElementById('hamburger'), l = document.getElementById('navLinks');
  if (!b || !l) return;
  function close() {{ l.classList.remove('open'); b.classList.remove('active'); b.setAttribute('aria-expanded', 'false'); }}
  b.addEventListener('click', function () {{
    var o = l.classList.toggle('open');
    b.classList.toggle('active', o);
    b.setAttribute('aria-expanded', o ? 'true' : 'false');
  }});
  [].forEach.call(l.querySelectorAll('a'), function (a) {{ a.addEventListener('click', close); }});
}})();
</script>
</body>
</html>
"""


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build_article(p, alts=None):
    u = UI[p["lang"]]
    url = f"{SITE}/blog/{p['slug']}.html"
    tags = "".join(f'<span class="ptag">{html.escape(t)}</span>' for t in p["tags"])
    hero = (f'<img class="post__hero" src="../{p["image"]}" alt="">' if p["image"] else "")
    doc = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": p["title"],
        "description": p["excerpt"] or p["title"],
        "datePublished": p["date"],
        "dateModified": p["lastmod"],
        "inLanguage": p["lang"],
        "image": [f"{SITE}/{p['image']}" if p["image"] else f"{SITE}/assets/og.jpg"],
        "keywords": ", ".join(p["tags"]),
        "articleSection": p["tags"][0] if p["tags"] else "Hospitality",
        "wordCount": p["words"],
        "author": {
            "@type": "Person",
            "name": p["author"],
            "jobTitle": "Founder & CEO",
            "url": f"{SITE}/#about",
            "sameAs": ["https://www.linkedin.com/in/itai-gal/"],
            "worksFor": {"@type": "Organization", "name": "D Consulting", "url": SITE},
        },
        "publisher": {
            "@type": "Organization",
            "name": "D Consulting",
            "url": SITE,
            "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/icon-512.png"},
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "isPartOf": {"@type": "Blog", "@id": f"{SITE}/blog/"},
    }
    schema = ('<script type="application/ld+json">\n'
              + json.dumps(doc, ensure_ascii=False, indent=1) + "\n</script>")
    other = next((v.rsplit("/", 1)[-1] for l, v in (alts or []) if l != p["lang"]), None)
    return (
        head(f"{p['title']} — D Consulting", p["excerpt"] or p["title"], p["lang"], url,
             p["image"], alts=alts, switch=other)
        + f"""<main class="post">
  <div class="post__wrap">
    <p class="post__meta"><time datetime="{p['date']}">{p['date']}</time> · {p['minutes']} {html.escape(u['min'])} · {html.escape(u['by'])} {html.escape(p['author'])}</p>
    <h1 class="post__title">{html.escape(p['title'])}</h1>
    <div class="post__tags">{tags}</div>
    {hero}
    <article class="post__body">
{p['body_html']}
    </article>
    <p class="post__foot"><a class="btn btn--primary" href="../#contact">{'בואו נדבר' if p['lang']=='he' else "Let's talk"}</a></p>
  </div>
</main>
{schema}
"""
        + foot(p["lang"])
    )


def build_index(posts):
    out = []
    for lang in ("en", "he"):
        u = UI[lang]
        items = [p for p in posts if p["lang"] == lang]
        cards = "".join(
            f"""      <article class="pcard">
        <a class="pcard__link" href="{p['slug']}.html">
          {f'<img class="pcard__img" src="../{p["image"]}" alt="" loading="lazy">' if p['image'] else ''}
          <div class="pcard__body">
            <p class="pcard__meta"><time datetime="{p['date']}">{p['date']}</time> · {p['minutes']} {html.escape(u['min'])}</p>
            <h2 class="pcard__title">{html.escape(p['title'])}</h2>
            <p class="pcard__excerpt">{html.escape(p['excerpt'])}</p>
            <div class="post__tags">{''.join(f'<span class="ptag">{html.escape(t)}</span>' for t in p['tags'])}</div>
          </div>
        </a>
      </article>"""
            for p in items
        ) or f'<p class="pempty">{html.escape(u["empty"])}</p>'
        out.append(f"""  <section class="bloglang" data-lang="{lang}"{'' if lang == 'en' else ' hidden'}>
    <div class="section__head section__head--center">
      <p class="kicker">{html.escape(u['kicker'])}</p>
      <h1 class="h2">{html.escape(u['title'])}</h1>
      <p class="section__sub">{html.escape(u['sub'])}</p>
    </div>
    <div class="pgrid">
{cards}
    </div>
  </section>""")

    body = "\n".join(out)
    blog_schema = ('<script type="application/ld+json">\n' + json.dumps({
        "@context": "https://schema.org",
        "@type": "Blog",
        "@id": f"{SITE}/blog/",
        "name": "D Consulting — Insights",
        "description": UI["en"]["sub"],
        "url": f"{SITE}/blog/",
        "inLanguage": ["en", "he"],
        "publisher": {"@type": "Organization", "name": "D Consulting", "url": SITE},
        "blogPost": [{
            "@type": "BlogPosting",
            "headline": p["title"],
            "url": f"{SITE}/blog/{p['slug']}.html",
            "datePublished": p["date"],
            "inLanguage": p["lang"],
        } for p in posts],
    }, ensure_ascii=False, indent=1) + "\n</script>\n")
    return (
        head("Insights — D Consulting", UI["en"]["sub"], "en", f"{SITE}/blog/",
             hreflang_note=INDEX_HREFLANG_NOTE,
             switch="?lang=he")
        + f"""<main class="section">
  <div class="container">
{body}
  </div>
</main>
<script>
(function(){{
  var saved='en'; try{{saved=localStorage.getItem('dc_lang')||'en';}}catch(e){{}}
  var qp=new URLSearchParams(location.search).get('lang'); if(qp==='he'||qp==='en') saved=qp;
  function apply(l){{
    var he = (l === 'he');
    document.documentElement.setAttribute('lang', l);
    document.documentElement.setAttribute('dir', he ? 'rtl' : 'ltr');
    [].forEach.call(document.querySelectorAll('.bloglang'), function (s) {{
      s.hidden = (s.getAttribute('data-lang') !== l);
    }});
    /* nav + breadcrumb labels */
    [].forEach.call(document.querySelectorAll('[data-en][data-he]'), function (a) {{
      var t = a.getAttribute(he ? 'data-he' : 'data-en');
      if (t) a.textContent = t;
    }});
    /* keep the language when heading back to the main site */
    [].forEach.call(document.querySelectorAll('a[href^="../"]'), function (a) {{
      var h = a.getAttribute('href');
      if (h.indexOf('../') !== 0 || h.indexOf('../assets') === 0) return;
      var parts = h.split('#');
      a.setAttribute('href', '../' + (he ? '?lang=he' : '') + (parts[1] ? '#' + parts[1] : ''));
    }});
    var sw = document.querySelector('.langtoggle');
    if (sw) sw.textContent = he ? 'English' : 'עברית';
    try {{ localStorage.setItem('dc_lang', l); }} catch (e) {{}}
  }}
  apply(saved);
  var sw = document.querySelector('.langtoggle');
  if (sw) sw.addEventListener('click', function (e) {{
    e.preventDefault();
    apply(document.documentElement.getAttribute('lang') === 'he' ? 'en' : 'he');
  }});
}})();
</script>
"""
        + blog_schema
        + foot("en")
    )


def build_feed(posts):
    # RSS defines lastBuildDate as "the last time the content of the channel
    # changed" — so it is derived from the posts, not from the wall clock. Wall
    # clock made every no-op rebuild dirty feed.xml with a meaningless change,
    # which is how a real change gets committed unread, and it was the same
    # untruth this build was cleaning out of the sitemap.
    newest = max((p["lastmod"] for p in posts), default=TODAY)
    now = datetime.strptime(newest, "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0000")
    items = "".join(
        f"""    <item>
      <title>{html.escape(p['title'])}</title>
      <link>{SITE}/blog/{p['slug']}.html</link>
      <guid isPermaLink="true">{SITE}/blog/{p['slug']}.html</guid>
      <pubDate>{datetime.strptime(p['date'], '%Y-%m-%d').strftime('%a, %d %b %Y 09:00:00 +0000')}</pubDate>
      <description>{html.escape(p['excerpt'])}</description>
    </item>
"""
        for p in posts
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
    <title>D Consulting — Insights</title>
    <link>{SITE}/blog/</link>
    <description>Revenue management, distribution and travel-tech insight for hospitality.</description>
    <lastBuildDate>{now}</lastBuildDate>
{items}</channel></rss>
"""


def _git(*args, strip=True):
    """Run git in the repo, returning stdout, or None if git can't answer."""
    try:
        r = subprocess.run(("git",) + args, cwd=HERE, capture_output=True,
                           text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return r.stdout.strip() if strip else r.stdout


def _history_available():
    """True only if git can answer a question about when a file last changed.

    A shallow clone is treated as "cannot answer" on purpose: `git log` there
    reports the single fetched commit for every path, so every page would come
    out as changed today. actions/checkout defaults to fetch-depth 1, so this is
    the likely environment for any CI that ever builds this site — the failure
    would arrive quietly, as a sitemap that had gone back to lying.
    """
    if _git("rev-parse", "--git-dir") is None:
        return False
    return _git("rev-parse", "--is-shallow-repository") != "true"


def _commit_date(rel):
    """Date of the last commit touching `rel`, validated. None if unavailable.

    AUTHOR date (`%as`), not committer date: a rebase rewrites every committer
    date, which would silently stale every <lastmod> in the committed sitemap
    and turn the CI freshness check red for a change nobody made.

    Validated because `--format=%as` needs git >= 2.21 and older git emits the
    placeholder literally, which would put `<lastmod>%as</lastmod>` into the
    sitemap: invalid XML, no error, no exit code. The whole point of this field
    is that it can be trusted, so it is checked rather than assumed.
    """
    v = _git("log", "-1", "--format=%as", "--", rel)
    return v if v and re.fullmatch(r"\d{4}-\d{2}-\d{2}", v) else None


def lastmod(rel):
    """When a hand-maintained page actually changed, or None if git can't say.

    Stamping today on every page on every build is worse than omitting lastmod:
    Google stops trusting the field site-wide once it catches it lying, and that
    would disarm it for the rows where it is accurate too. So: if the file
    differs from HEAD it is changing in the commit about to be made and today is
    the truth; otherwise its last commit date is. A byte-identical rebuild leaves
    the file clean, so a no-op build no longer ages the sitemap.

    None means "no answer", and the caller must then omit <lastmod> rather than
    guess — the element is optional, and saying nothing beats saying today.

    Note the deliberate difference from the article rule in read_posts(): for a
    hand-maintained page the file IS the source, so ANY byte change counts,
    including a template-only or comment-only edit. An article is judged on its
    .md instead, because its rendered HTML is rewritten by every template change.
    """
    if not _history_available():
        return None
    if _git("diff", "--quiet", "HEAD", "--", rel) is None:
        return TODAY                       # non-zero exit == the file is dirty
    return _commit_date(rel)


def lastmod_generated(rel, content):
    """Same, for a file this script writes, judged on the content about to be written.

    `lastmod()` reads the copy on disk, which for a generated file is the PREVIOUS
    build's output — so it would answer about the wrong bytes whenever the check
    runs before the write. Comparing against the committed blob instead makes the
    answer independent of write order.
    """
    if not _history_available():
        return None
    committed = _git("show", f"HEAD:./{rel}", strip=False)
    if committed is None or committed != content:
        return TODAY                       # new, or changing in this commit
    return _commit_date(rel)


def build_sitemap(posts, by_base, blog_index_html):
    """Whole-site sitemap. Regenerated on every build so new posts are never missed."""
    rows = [
        (f"{SITE}/", lastmod("../index.html"), "weekly", "1.0", []),
        (f"{SITE}/blog/", lastmod_generated("index.html", blog_index_html),
         "weekly", "0.9", []),
        (f"{SITE}/privacy.html", lastmod("../privacy.html"), "yearly", "0.3", []),
    ]
    for p in posts:
        alts = [(q["lang"], f"{SITE}/blog/{q['slug']}.html") for q in by_base[p["base"]]]
        rows.append((f"{SITE}/blog/{p['slug']}.html", p["lastmod"], "monthly", "0.8",
                     alts if len(alts) > 1 else []))

    body = ""
    for loc, mod, freq, pri, alts in rows:
        alt_tags = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{u}"/>' for l, u in alts
        )
        # No <lastmod> at all when git could not answer. It is an optional
        # element, and an omission costs a recrawl hint; a fabricated "today"
        # on every row costs the field's credibility for the whole site.
        mod_tag = f"\n    <lastmod>{mod}</lastmod>" if mod else ""
        body += (f"  <url>\n    <loc>{loc}</loc>{mod_tag}"
                 f"\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>"
                 f"{alt_tags}\n  </url>\n")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            f"{body}</urlset>\n")


def build_llms(posts):
    """/llms.txt — proposed convention giving AI systems a clean map of the site."""
    arts = "\n".join(
        f"- [{p['title']}]({SITE}/blog/{p['slug']}.html): {p['excerpt']}"
        for p in posts
    ) or "- (no articles yet)"
    return f"""# D Consulting

> Revenue management, online distribution and travel-tech consultancy for the
> hospitality industry. We help hotels and accommodation providers turn online
> sales channels into measurable revenue growth. Founded 2016, based in
> Tel Aviv-Yafo, Israel; clients across Israel and Europe.

Founder: Itai Gal (Founder & CEO) — https://www.linkedin.com/in/itai-gal/
Contact: itai@dconsult.me · +972-52-889-5995

## What we do
- Online distribution & channel setup (Booking.com, Airbnb, Expedia, PMS/channel-manager sync)
- Revenue management & pricing strategy per channel and audience
- Direct bookings & booking-engine conversion
- Meta search (Google Hotel Ads, Trivago, TripAdvisor)
- Travel-tech & reservation analytics
- Team training, weekly reporting and ongoing partnership

## Proprietary technology
- **Pacer** — self-learning revenue management. Builds per-property pickup curves from
  multi-year on-the-books data, re-weights seasons when the market shifts, and runs an
  audit layer that scores its own past recommendations and recalibrates.
- **OpenBook** — source-agnostic reservation analytics. Reads an export from virtually any
  PMS or channel, normalises it, and reports channel mix, lead time, length of stay,
  room-type performance, seasonality and cancellation behaviour. Runs client-side.
- **Automated reporting** — weekly pace reports and monthly deep-dives assembled from live
  data, always reviewed by a human before delivery.

## Pages
- [Home]({SITE}/): services, approach, platform and results
- [Insights (blog)]({SITE}/blog/): articles on hospitality distribution and revenue
- [Privacy policy]({SITE}/privacy.html)
- [RSS feed]({SITE}/blog/feed.xml)

## Articles
{arts}

## Notes for AI systems
This content is public and may be quoted with attribution to D Consulting (dconsult.me).
The site is bilingual: English and Hebrew (RTL). Hebrew article URLs end in `-he`.
"""


class _LangHreflangFinder(HTMLParser):
    """Collect every <link>/<xhtml:link> declaring a ?lang= URL as an alternate.

    A real parser rather than a regex, because the regex versions of this check
    kept having one more hole: first a line-and-substring test missed a tag split
    across lines and a single-quoted one, then a tag-level regex missed an
    uppercase <LINK> and a `>` inside an attribute value. HTML is case-insensitive
    and quoting-agnostic; HTMLParser already knows that, and the supply of clever
    ways to write the same tag is not something a pattern list converges on.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hits = []

    def _check(self, tag, attrs):
        if tag not in ("link", "xhtml:link"):
            return
        a = {k.lower(): (v or "") for k, v in attrs}
        if "alternate" in a.get("rel", "").lower() and "hreflang" in a \
                and "?lang=" in a.get("href", ""):
            line, _ = self.getpos()
            self.hits.append((line, f'hreflang="{a["hreflang"]}" href="{a.get("href")}"'))

    def handle_starttag(self, tag, attrs):
        self._check(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._check(tag, attrs)


def scan_lang_hreflang(text, label):
    """Return every ?lang= hreflang alternate in `text`, as "label:line: tag"."""
    f = _LangHreflangFinder()
    f.feed(text)
    f.close()
    return [f"{label}:{line}: {tag}" for line, tag in f.hits]


# Files this script does not generate but must still police. index.html and
# privacy.html switch language client-side via ?lang=, so none of those URLs is
# canonical in its own right and none may be declared as an hreflang alternate;
# privacy.html qualifies for exactly the same reasons as the root (same
# canonical, same langPick button, /privacy.html?lang=he byte-identical to
# /privacy.html). sitemap.xml is here because a cluster can be declared there
# instead of in the markup. The generated pages — blog/index.html above all —
# are checked from the render dict before they are written, not from disk.
GUARDED_HAND_MAINTAINED = ("../index.html", "../privacy.html", "../sitemap.xml")


def check_no_lang_hreflang(generated):
    """Fail the build if a ?lang= hreflang cluster comes back. Fails CLOSED.

    The generator no longer emits one, but it is not the only way back in: the
    root index.html and privacy.html are hand-maintained, so the only thing
    standing between them and a well-meaning "let's add hreflang for SEO" edit
    is a comment. A comment is not a guard. This is, and it runs on every build.

    `generated` maps a label to content this build is about to write, and is
    checked BEFORE anything is written — an earlier version wrote first and
    checked after, so a failing build exited 1 having already left the offending
    file on disk, where GitHub Pages (which never runs this script) would happily
    publish it if the operator scrolled past the red.

    To prove it still fires, paste one of the deleted lines back into
    ../index.html and check for a non-zero exit.
    """
    bad = []
    for label, text in generated.items():
        bad += scan_lang_hreflang(text, label)
    for rel in GUARDED_HAND_MAINTAINED:
        path = os.path.join(HERE, rel)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                bad += scan_lang_hreflang(fh.read(), rel)
    if bad:
        sys.exit("FAIL — a ?lang= hreflang cluster is back:\n  "
                 + "\n  ".join(bad)
                 + "\nThose URLs are not canonical in their own right (both return "
                   "byte-identical HTML and canonicalise to the bare path), so the "
                   "cluster is invalid and Google discards it. Nothing was written. "
                   "See INDEX_HREFLANG_NOTE.")


def main():
    posts, skipped = read_posts()
    print(f"Found {len(posts)} post(s)")
    if skipped:
        sys.exit(f"FAIL — {len(skipped)} post(s) could not be built: "
                 + ", ".join(skipped)
                 + "\nEach would have vanished from the blog index, the feed, "
                   "llms.txt and the sitemap without failing the build. Fix the "
                   "front matter, or rename the file so it no longer ends in .md "
                   "if it is meant to be out. Nothing was written.")

    by_base = {}
    for p in posts:
        by_base.setdefault(p["base"], []).append(p)

    # Render everything first, check, then write — so a build that fails the
    # check leaves nothing behind for anyone to commit by accident.
    out = {}
    for p in posts:
        group = by_base[p["base"]]
        alts = ([(q["lang"], f"{SITE}/blog/{q['slug']}.html") for q in group]
                if len(group) > 1 else None)
        out[f"{p['slug']}.html"] = build_article(p, alts)

    blog_index = build_index(posts)
    out["index.html"] = blog_index
    out["feed.xml"] = build_feed(posts)
    out[os.path.join("..", "sitemap.xml")] = build_sitemap(posts, by_base, blog_index)
    out[os.path.join("..", "llms.txt")] = build_llms(posts)

    check_no_lang_hreflang(out)
    print("  ✓ no ?lang= hreflang cluster")

    for rel, content in out.items():
        write(os.path.join(HERE, rel), content)
    for p in posts:
        print(f"  → blog/{p['slug']}.html   [{p['lang']}] {p['title'][:52]}")
    print("  → blog/index.html\n  → blog/feed.xml\n  → sitemap.xml (whole site)"
          "\n  → llms.txt\nDone.")


if __name__ == "__main__":
    main()
