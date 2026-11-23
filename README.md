# Jack McElwee — writing portfolio

A one-page portfolio for Jack McElwee, news reporter for [The Arbiter](https://www.arbiteronline.com/author/jackmcelwee/), Boise State University's independent student newspaper.

Live site: https://mrodhansen.github.io/jack-mcelwee-portfolio/

## Editing

Everything is in `index.html`, with no build step. Each story is one `<li class="story">` block in the "Published work" list. The full text sits inside its `<details class="full">` block, one `<p>` per paragraph, and opens when someone clicks the headline or the "Read the full story" bar.

To add a story, copy one block and update:

- the `id` (`s14`, `s15`, ...) and the matching `href="#s14"` / `data-open` / `data-close` values
- the number, section (`data-section` is `news` or `culture`), date, headline, summary and link to the original
- the photo link and its credit line
- the paragraphs of the full text, the byline, and the word count (it appears twice in the block)
- the counts in the stats row, the side menu and the filter buttons

A single story can be shared by adding its id to the address, for example `.../jack-mcelwee-portfolio/#s06` opens the Engineering Building flood story.

Push to `main` and GitHub Pages republishes the site in about a minute.

Stories were first published by The Arbiter, and photos belong to the credited photographers. Each story links back to the original article.
