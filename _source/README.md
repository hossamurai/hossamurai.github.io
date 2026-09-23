# Hossam TV website

A 14-page site in English and Arabic (28 pages in total), ready for GitHub Pages.

## Upload it

1. Open your `hossamurai.github.io` repository on GitHub.
2. Delete the old `index.html`. **Keep your images**: `logo.png`, `basic.png`, `premium.png`, `X.png`, `marvel.png`.
3. Upload everything in this zip (drag the files and folders into GitHub's "Add file → Upload files" page) and commit.
4. Wait a minute, then open https://hossamurai.github.io. Visitors are sent to Arabic or English automatically, and the site remembers their choice.

## What's inside

| Path | What it is |
|---|---|
| `index.html` | Picks Arabic or English and redirects |
| `en/…`, `ar/…` | The pages: Home, Plans, Channels, Setup (plus 7 device guides), Help, About, Policies |
| `assets/` | Shared stylesheet and script |
| `404.html` | "Page not found" page |
| `sitemap.xml`, `robots.txt` | Help Google find every page in both languages |
| `_source/` | The files that generate the site. GitHub Pages doesn't publish this folder. |

## Check before going live

- **Plan numbers.** The channel, movie and series counts are shown as `16K+`, `65K+` and so on. Your old site said "16 private", so confirm these are your real counts and fix them in `_source/content.py` → `PLANS` → `stats`.
- **Channels page.** The coloured tags show which plans are strongest in each category. Adjust `CATEGORIES` in `content.py` if needed.
- **Licensing.** Put your license text in `LICENSE_TEXT` in `content.py` and it appears on the About page.
- **Reviews.** Add real customer quotes (with their permission) to `REVIEWS` in `content.py` and a reviews section appears on the Home page.

## Making changes

All the text, prices, plans, app codes, FAQ and troubleshooting are in **`_source/content.py`**. Page layouts are in `_source/pages.py`.

After editing, run this on your computer (it needs Python 3):

```
cd _source
python build.py
```

It regenerates `en/`, `ar/`, `assets/`, `index.html`, `404.html` and the sitemap. Then upload the changed files.

For a quick text fix you can also edit the HTML files in `en/` and `ar/` directly. Just remember that the next build will overwrite those edits.

## Custom domain (recommended)

1. Buy a domain (for example `hossamtv.com`).
2. In the repository, go to **Settings → Pages → Custom domain**, enter it and save.
3. At your domain provider, add the DNS records GitHub shows you.
4. Change `BASE_URL` in `content.py` to `https://yourdomain.com`, rebuild and upload.
