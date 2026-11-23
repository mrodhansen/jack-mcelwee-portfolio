# Jack McElwee — writing portfolio

A portfolio for Jack McElwee, news reporter for [The Arbiter](https://www.arbiteronline.com/author/jackmcelwee/), Boise State University's independent student newspaper.

Live site: https://mrodhansen.github.io/jack-mcelwee-portfolio/

The home page lists every story. Clicking a headline opens that story's own page (`stories/<name>/`) with a link to the original on The Arbiter at the top, then the section, date, headline, byline, photo and full text.

## How it is built

| File | What it is |
| --- | --- |
| `content/stories.json` | Every story: section, date, headline, summary, Arbiter link, photo, credit, authors and the paragraphs of the full text. Newest first. |
| `build.py` | Writes `index.html` and every `stories/<name>/index.html` from the data file. Story numbers, counts, word totals and dates are worked out here. |
| `assets/site.css` | Styles shared by all pages (the Index theme from the budget app), written with colour and font variables. |
| `assets/themes.css` | The six other looks. Each sets its own variables and the layout rules that differ from Index. |
| `assets/theme.js` | Every page: applies the saved theme before the page draws. Home page: builds the theme picker in About and saves the choice in the browser's local storage. |
| `assets/site.js` | Home page only: the News/Culture filter and the side menu highlight. |

`index.html` and `stories/` are generated. Edit the data file or `build.py`, not the output.

## Themes

Visitors pick a theme at the bottom of the About section: Index (the default), Broadsheet, Night Desk, Gallery, Sagebrush, Wire or Capitol. The choice is stored in the browser under `jack-mcelwee-portfolio:theme` and applies to every page. If the browser blocks storage, the picker says the choice will reset.

To add a theme, add an entry to `THEMES` in `assets/theme.js` (with its Google Fonts families) and a matching `[data-theme='id'], [data-preview='id']` block in `assets/themes.css`.

## Adding a story

1. Add an entry at the top of `content/stories.json` (newest first) with the same fields as the others. `image` is the part of the photo address after `/wp-content/uploads/`. `paragraphs` holds one HTML string per paragraph; links are allowed.
2. Run `python3 build.py`. It stops with a clear message if a field is missing, the order is wrong, or two stories would share an address.
3. Commit and push to `main`. GitHub Pages republishes in about a minute.

Stories were first published by The Arbiter, and photos belong to the credited photographers. Each story page links to the original article and names it as the original source.
