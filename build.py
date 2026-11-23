#!/usr/bin/env python3
"""Build the portfolio from content/stories.json.

Writes index.html and one page per story at stories/<slug>/index.html.
Counts, word totals, story numbers and dates all come from the data file.
Run from anywhere: python3 build.py
"""

import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE_URL = "https://mrodhansen.github.io/jack-mcelwee-portfolio/"
AUTHOR_PAGE = "https://www.arbiteronline.com/author/jackmcelwee/"
AUTHOR = "Jack McElwee"
SECTIONS = ("News", "Culture")
FIELDS = {
    "section",
    "date",
    "title",
    "dek",
    "url",
    "image",
    "image_alt",
    "credit",
    "authors",
    "paragraphs",
}
AP_MONTHS = (
    "Jan.",
    "Feb.",
    "March",
    "April",
    "May",
    "June",
    "July",
    "Aug.",
    "Sept.",
    "Oct.",
    "Nov.",
    "Dec.",
)
FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' fill='%23111'/%3E%3Ctext x='16' y='21' font-family='monospace' "
    "font-size='13' font-weight='700' fill='%23fff' text-anchor='middle'%3EJM%3C/text%3E%3C/svg%3E"
)
FONTS = (
    "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600"
    "&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400&display=swap"
)


def e(text):
    return html.escape(text, quote=True)


def ap_date(iso):
    day = date.fromisoformat(iso)
    return f"{AP_MONTHS[day.month - 1]} {day.day}, {day.year}"


def count_words(paragraphs):
    return sum(len(re.sub(r"<[^>]+>", "", p).split()) for p in paragraphs)


def image_url(path, width):
    return f"https://i0.wp.com/www.arbiteronline.com/wp-content/uploads/{path}?w={width}&ssl=1"


def join_names(names):
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def load_stories():
    stories = json.loads((ROOT / "content" / "stories.json").read_text())
    if not stories:
        raise SystemExit("content/stories.json has no stories")
    slugs = set()
    for i, story in enumerate(stories):
        where = f"story {i + 1} ({story.get('title', 'no title')})"
        if set(story) != FIELDS:
            raise SystemExit(
                f"{where}: fields must be exactly {sorted(FIELDS)}, got {sorted(story)}"
            )
        if story["section"] not in SECTIONS:
            raise SystemExit(f"{where}: section must be one of {SECTIONS}")
        if i and story["date"] > stories[i - 1]["date"]:
            raise SystemExit(f"{where}: stories must be listed newest first")
        if AUTHOR not in story["authors"]:
            raise SystemExit(f"{where}: authors must include {AUTHOR}")
        if not story["paragraphs"]:
            raise SystemExit(f"{where}: no paragraphs")
        match = re.fullmatch(
            r"https://www\.arbiteronline\.com/.+/([a-z0-9-]+)/", story["url"]
        )
        if not match:
            raise SystemExit(
                f"{where}: url must be an arbiteronline.com story link ending in /"
            )
        slug = match.group(1)
        if slug in slugs:
            raise SystemExit(f"{where}: two stories share the address {slug}")
        slugs.add(slug)
        story["slug"] = slug
        story["number"] = len(stories) - i
        story["nn"] = f"{story['number']:02d}"
        story["words"] = count_words(story["paragraphs"])
        story["when"] = ap_date(story["date"])
    return stories


def head(title, description, prefix, extra):
    return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>{e(title)}</title>
    <meta name="description" content="{e(description)}" />
    <meta name="theme-color" content="#f6f6f4" />
{extra}
    <link rel="icon" href="{FAVICON}" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="preconnect" href="https://i0.wp.com" />
    <link href="{e(FONTS)}" rel="stylesheet" />
    <link href="{prefix}assets/site.css" rel="stylesheet" />
  </head>'''


def rail(prefix, total, on_story_page):
    work_current = ' aria-current="true"' if on_story_page else ""
    return f'''      <aside class="rail">
        <a class="mark" href="{prefix}#top">{AUTHOR}</a>
        <nav class="nav" aria-label="Sections">
          <a href="{prefix}#top">Overview</a>
          <a href="{prefix}#work"{work_current}>Work <span class="n">{total}</span></a>
          <a href="{prefix}#about">About</a>
          <a class="out" href="{AUTHOR_PAGE}" target="_blank" rel="noopener"
            >Arbiter <span class="n" aria-hidden="true">↗</span></a
          >
        </nav>
        <p class="rail-foot">
          <strong>News Reporter</strong>
          The Arbiter · Boise State
        </p>
      </aside>'''


def co_reporters(story):
    others = [name for name in story["authors"] if name != AUTHOR]
    if not others:
        return ""
    return f'\n                <p class="with">Co-reported with {e(join_names(others))}</p>'


def story_row(story, is_lead):
    lead = " lead" if is_lead else ""
    loading = "" if is_lead else '\n                    loading="lazy"'
    width = 1400 if is_lead else 900
    return f'''            <li class="story{lead}" id="s{story["nn"]}" data-section="{story["section"].lower()}">
              <span class="story-no" aria-hidden="true">{story["nn"]}</span>
              <figure class="story-media">
                <div class="story-img">
                  <img
                    src="{e(image_url(story["image"], width))}"
                    alt="{e(story["image_alt"])}"{loading}
                    onerror="this.parentNode.classList.add('broken')"
                  />
                </div>
                <figcaption class="credit">{e(story["credit"])}</figcaption>
              </figure>
              <div class="story-body">
                <p class="meta">
                  <span class="sec">{story["section"]}</span>
                  <time datetime="{story["date"]}">{story["when"]}</time>
                  <span class="words">{story["words"]} words</span>
                </p>
                <h3><a href="stories/{story["slug"]}/">{e(story["title"])}</a></h3>
                <p class="dek">{e(story["dek"])}</p>{co_reporters(story)}
              </div>
            </li>'''


def index_page(stories):
    total = len(stories)
    per_section = {
        name: sum(1 for s in stories if s["section"] == name) for name in SECTIONS
    }
    total_words = sum(s["words"] for s in stories)
    words_label = f"{total_words / 1000:.1f}k"
    rows = "\n\n".join(story_row(story, i == 0) for i, story in enumerate(stories))
    filters = "\n".join(
        f'''              <button type="button" data-filter="{name.lower()}" aria-pressed="false">
                {name} <span class="n">{per_section[name]}</span>
              </button>'''
        for name in SECTIONS
    )
    meta = f'''    <meta property="og:type" content="profile" />
    <meta property="og:title" content="{AUTHOR} · News Reporter" />
    <meta property="og:description" content="Reporting on Boise State, the city of Boise and Idaho for The Arbiter." />
    <meta property="og:image" content="{SITE_URL}assets/jack-mcelwee.jpg" />
    <meta name="twitter:card" content="summary" />'''
    description = (
        f"Portfolio of {AUTHOR}, news reporter for The Arbiter, "
        "Boise State University's independent student newspaper."
    )
    return f'''{head(f"{AUTHOR} · News Reporter", description, "", meta)}
  <body>
    <a class="skip" href="#work">Skip to stories</a>
    <div class="frame">
{rail("", total, False)}

      <main class="main">
        <header class="hero section" id="top">
          <p class="label muted">Portfolio · News Reporter</p>
          <h1>{AUTHOR}</h1>
          <p class="lede">
            News reporter for The Arbiter, Boise State University's independent student
            newspaper, covering campus, the city of Boise and Idaho.
          </p>
          <div class="actions">
            <a class="btn btn-solid" href="#work">Read the work</a>
            <a class="btn" href="{AUTHOR_PAGE}" target="_blank" rel="noopener"
              >Author page on The Arbiter <span aria-hidden="true">↗</span></a
            >
          </div>
          <dl class="stats">
            <div class="stat"><dt>Published stories</dt><dd>{total}</dd></div>
            <div class="stat"><dt>News</dt><dd>{per_section["News"]}</dd></div>
            <div class="stat"><dt>Culture</dt><dd>{per_section["Culture"]}</dd></div>
            <div class="stat"><dt>Words published</dt><dd>{words_label}</dd></div>
          </dl>
        </header>

        <section class="section" id="work" aria-labelledby="work-title">
          <div class="section-head">
            <h2 id="work-title">
              <span class="label">Published work</span>
              <span class="label muted">The Arbiter, 2026</span>
            </h2>
            <div class="filters" role="group" aria-label="Filter stories by section">
              <button type="button" data-filter="all" aria-pressed="true">
                All <span class="n">{total}</span>
              </button>
{filters}
            </div>
          </div>
          <p class="sr-only" aria-live="polite" id="filter-status"></p>

          <ol class="stories" reversed>
{rows}
          </ol>
        </section>

        <section class="section" id="about" aria-labelledby="about-title">
          <div class="section-head">
            <h2 id="about-title"><span class="label">About</span></h2>
          </div>
          <div class="about">
            <figure class="portrait">
              <img src="assets/jack-mcelwee.jpg" alt="Portrait of {AUTHOR}" width="768" height="768" />
              <figcaption class="label muted">{AUTHOR}</figcaption>
            </figure>
            <div>
              <div class="bio">
                <p>
                  Jack McElwee is a news reporter for The Arbiter, Boise State University's
                  independent student newspaper.
                </p>
                <p>
                  Jack's reporting follows how federal programs, university decisions and the
                  weather play out on campus and across Boise: an $8 million federal grant to keep
                  new teachers in Idaho classrooms, opportunity zones that could open campus to new
                  development, a Labor Day flood that pushed students and classes out of the
                  engineering building, and a record-low snow year at Idaho's ski resorts.
                </p>
                <p>
                  Alongside breaking news, Jack writes about the people and places behind campus
                  life, from the student-run hall councils in the residence halls to the history
                  inside the Communication Building, built in 1942.
                </p>
              </div>
              <dl class="facts">
                <div><dt>Role</dt><dd>News Reporter</dd></div>
                <div>
                  <dt>Publication</dt>
                  <dd>
                    <a href="https://www.arbiteronline.com/" target="_blank" rel="noopener"
                      >The Arbiter</a
                    >, Boise State University
                  </dd>
                </div>
                <div><dt>Coverage</dt><dd>Boise State, Boise, Idaho</dd></div>
                <div>
                  <dt>Topics</dt>
                  <dd>Campus development, education, public safety, student life, campus history</dd>
                </div>
                <div><dt>First byline</dt><dd>{stories[-1]["when"]}</dd></div>
                <div><dt>Latest byline</dt><dd>{stories[0]["when"]}</dd></div>
              </dl>
            </div>
          </div>
        </section>

        <footer class="foot">
          <p>© 2026 {AUTHOR}</p>
          <p>Stories first published by The Arbiter. Photos belong to the photographers credited.</p>
        </footer>
      </main>
    </div>
    <script src="assets/site.js"></script>
  </body>
</html>
'''


def pager_link(story, direction):
    if story is None:
        return "        <span></span>"
    arrow_before = '<span aria-hidden="true">←</span> ' if direction == "Newer" else ""
    arrow_after = ' <span aria-hidden="true">→</span>' if direction == "Older" else ""
    return f'''        <a class="{direction.lower()}" href="../{story["slug"]}/">
          <span class="label muted">{arrow_before}{direction} · No. {story["nn"]}{arrow_after}</span>
          <span class="t">{e(story["title"])}</span>
        </a>'''


def story_page(story, newer, older, total):
    paragraphs = "\n".join(f"            <p>{p}</p>" for p in story["paragraphs"])
    meta = f'''    <meta property="og:type" content="article" />
    <meta property="og:title" content="{e(story["title"])}" />
    <meta property="og:description" content="{e(story["dek"])}" />
    <meta property="og:image" content="{e(image_url(story["image"], 1200))}" />
    <meta name="twitter:card" content="summary_large_image" />
    <link rel="canonical" href="{e(story["url"])}" />'''
    return f'''{head(f"{story['title']} · {AUTHOR}", story["dek"], "../../", meta)}
  <body>
    <a class="skip" href="#story">Skip to the story</a>
    <div class="frame">
{rail("../../", total, True)}

      <main class="main main-story" id="story">
        <div class="topbar">
          <a class="back" href="../../#work"><span aria-hidden="true">←</span> All stories</a>
          <a class="source-bar" href="{e(story["url"])}" target="_blank" rel="noopener">
            <span class="src-label">First published in The Arbiter · {story["when"]}</span>
            <span class="src-go">Read on The Arbiter <span aria-hidden="true">↗</span></span>
          </a>
        </div>

        <article>
          <header class="story-head">
            <p class="meta">
              <span class="no">No. {story["nn"]}</span>
              <span class="sec">{story["section"]}</span>
              <time datetime="{story["date"]}">{story["when"]}</time>
              <span class="words">{story["words"]} words</span>
            </p>
            <h1>{e(story["title"])}</h1>
            <p class="dek">{e(story["dek"])}</p>
            <p class="byline">By <strong>{e(join_names(story["authors"]))}</strong> · The Arbiter</p>
          </header>

          <figure class="photo-figure">
            <div class="photo">
              <img
                src="{e(image_url(story["image"], 1600))}"
                alt="{e(story["image_alt"])}"
                onerror="this.parentNode.classList.add('broken')"
              />
            </div>
            <figcaption class="credit">{e(story["credit"])}</figcaption>
          </figure>

          <div class="story-text">
{paragraphs}
          </div>
        </article>

        <nav class="pager" aria-label="More stories">
{pager_link(newer, "Newer")}
{pager_link(older, "Older")}
        </nav>

        <footer class="foot">
          <p>© 2026 {AUTHOR}</p>
          <p>First published by The Arbiter. {e(story["credit"])}.</p>
        </footer>
      </main>
    </div>
  </body>
</html>
'''


def main():
    stories = load_stories()
    (ROOT / "index.html").write_text(index_page(stories))
    out = ROOT / "stories"
    if out.exists():
        shutil.rmtree(out)
    for i, story in enumerate(stories):
        newer = stories[i - 1] if i > 0 else None
        older = stories[i + 1] if i + 1 < len(stories) else None
        page_dir = out / story["slug"]
        page_dir.mkdir(parents=True)
        (page_dir / "index.html").write_text(
            story_page(story, newer, older, len(stories))
        )
    total_words = sum(s["words"] for s in stories)
    print(f"built index.html and {len(stories)} story pages ({total_words} words)")


if __name__ == "__main__":
    main()
