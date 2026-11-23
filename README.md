# Jack McElwee — writing portfolio

A one-page portfolio for Jack McElwee, news reporter for [The Arbiter](https://www.arbiteronline.com/author/jackmcelwee/), Boise State University's independent student newspaper.

Live site: https://mrodhansen.github.io/jack-mcelwee-portfolio/

## Editing

Everything is in `index.html`, with no build step. To add a story, copy one `<li class="story">` block in the "Published work" list, then update:

- the number, section (`data-section` is `news` or `culture`), date, word count, headline, link and summary
- the photo link and its credit line
- the counts in the stats row, the side menu and the filter buttons

Push to `main` and GitHub Pages republishes the site in about a minute.

Stories and photos belong to The Arbiter and the credited photographers; each story links back to the original article.
