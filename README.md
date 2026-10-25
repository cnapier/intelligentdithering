# Intelligent Dithering

Source for [intelligentdithering.com](https://intelligentdithering.com), a Hugo site using a customised copy of the `puppet` theme.

You never build or upload the site by hand. Pushing to `main` on GitHub runs `.github/workflows/deploy.yml`, which builds the site with Hugo 0.167 and publishes it to the `deploy` branch. Plesk then pulls that branch into `httpdocs`.

```
content/posts/YYYY/MM/<slug>/index.md   one folder per post (a "page bundle"), served at /<slug>/
content/posts/YYYY/MM/<slug>/images/    that post's images
archetypes/posts.md                     template for new posts
layouts/                                site overrides of the theme (SEO tags, images, .htaccess, RSS)
assets/css/custom.scss                  site CSS (menu bar, header, thumbnails)
static/                                 copied as-is (robots.txt, favicons, img/)
tools/seo-check.py                      SEO checker for posts
test.sh                                 SEO check + local preview server
publish.sh                              check, test-build, commit, push, confirm live
```

---

## 1. Writing a new post on the Mac

**1. Get up to date**

```bash
cd ~/Sites/IntelligentDithering
git pull
```

**2. Create the post from the template.** The folder name becomes the URL (`/my-post-slug/` – the year/month folders just keep things tidy), so use short, lowercase words joined by hyphens, and don't rename it once it's published:

```bash
hugo new content posts/2026/11/my-post-slug/index.md
```

This creates `content/posts/2026/11/my-post-slug/index.md` from `archetypes/posts.md`, with `draft: true` and today's date. The post will appear at `/my-post-slug/`, and `/posts/2026/11/my-post-slug/` redirects there.

**3. Fill in the front matter**

```yaml
title: "Build a Pi Zero Wall Dashboard"         # aim for 60 characters or fewer
date: 2026-11-02T19:30:00+00:00
draft: true
description: "70–160 characters: what the reader gets from the post. This is the Google snippet."
categories:
  - "guides"                                    # exactly one: guides, recommended, news or personal
tags:
  - "raspberry-pi"                              # 2–4 from the list below
coverImage: "dashboard.webp"                    # file in this post's images/ folder
# seoTitle: "Shorter title just for search results"   # optional
```

**Tags** (topic): `raspberry-pi`, `ios`, `mac`, `apps`, `maker`, `education`, `open-source`, `sysadmin`, `networking`, `home-automation`, `productivity`, `wellbeing`. The list is whatever has a folder in `content/tags/`. To add a genuinely new tag, create `content/tags/<new-tag>/_index.md` with a `title:` and `description:`, and only once you'll have at least two posts for it. To retire or merge a tag, add it to `data/taxonomy_redirects.toml` so its old page redirects instead of 404ing.

Delete any template lines you don't use. An empty `""` placeholder counts as missing.

**4. Add images.** Put them in an `images/` folder next to `index.md` and reference them like this:

```markdown
![A Raspberry Pi Zero mounted behind a wall screen](images/dashboard.webp)
```

Always write the alt text in the square brackets. Prefer WebP and keep files under about 500 KB. The `coverImage` file appears at the top of the post, as the home page thumbnail and as the social share image.

**5. Write.** Everything above `<!--more-->` is the summary on the home page and in RSS. Use `##` for section headings (the post title is already the page's H1). For a longer post, put `{{< toc >}}` after the intro to get a table of contents built automatically from your `##` and `###` headings – don't write one by hand, as the links break when headings change, and link to a related older post using its relative URL, e.g. `[my Pi 5 post](/raspberry-pi-5-announced/)`.

**6. Preview and check**

```bash
./test.sh
```

See [section 2](#2-testsh). Fix any errors it reports, and as many warnings as are worth it.

**7. Publish**

```bash
./publish.sh
```

It offers to switch `draft: true` to `false`, then commits, pushes and waits until the post is live. See [section 3](#3-publishsh).

> **Dates:** a post dated in the future builds fine but won't appear on the live site until the next push after that date, because nothing rebuilds the site on a schedule.

---

## 2. `test.sh`

Runs the SEO check on your drafts and changed posts, then starts a local preview of the site.

**What it does, in order:**

1. `cd ~/Sites/IntelligentDithering`
2. Runs `tools/seo-check.py` (see [section 4](#4-seo-checks-before-publishing)), passing on any arguments you gave `test.sh`. If the check finds **errors** it prints a red warning, but the preview still starts so you can see the problem.
3. Opens http://127.0.0.1:1313 in your browser. The server takes a second or two to start, so refresh if the page is blank.
4. Runs `hugo server` with drafts (`-D`/`--buildDrafts`) and future-dated posts (`--buildFuture`) included. It builds into `/tmp/hugotest/` so your repo's `public/` folder stays untouched, and is reachable from other devices on your network (`--bind 0.0.0.0`). Pages reload automatically when you save. Press **Ctrl-C** to stop it.

**Arguments**

| Command | What it does |
|---|---|
| `./test.sh` | Checks drafts and posts changed since the last push, then starts the preview |
| `./test.sh --all` | Checks every post, then starts the preview |
| `./test.sh --links` | Also fetches every external link in the checked posts (slow – see below) |
| `./test.sh --all --links` | Full link check across every post |
| `./test.sh content/posts/2026/11/my-post-slug/index.md` | Checks only the post(s) you name, then starts the preview |
| `SKIP_SEO=1 ./test.sh` | Skips the check and goes straight to the preview |

Needs `hugo` (`brew install hugo`) and `python3` (comes with the Xcode command line tools: `xcode-select --install`). If `python3` is missing, the SEO check is skipped with a message.

---

## 3. `publish.sh`

Checks, test-builds, commits and pushes, then waits for the GitHub build and confirms the posts are live.

**Arguments**

| Command | What it does |
|---|---|
| `./publish.sh` | Normal publish. Asks before un-drafting posts and before committing |
| `./publish.sh "Fix typo in Pi 5 post"` | Uses your text as the commit message instead of the automatic one |
| `./publish.sh -y` / `--yes` | Answers yes to every question (un-draft, publish despite image problems, commit) |
| `./publish.sh -h` / `--help` | Shows the usage text |

The message and `-y` can be combined: `./publish.sh -y "New post"`.

**Environment variables (optional)**

| Variable | Default | Purpose |
|---|---|---|
| `SITE_URL` | `https://intelligentdithering.com` | Where to check the posts are live |
| `LIVE_CHECKS` | `24` | How many times to check, 5 seconds apart (24 = 2 minutes) |
| `INDEXNOW` | `1` | Set to `0` to skip the IndexNow ping (`INDEXNOW=0 ./publish.sh`) |

**What it does, in order:**

1. Checks you're on `main`, then pulls from GitHub, stashing and restoring any uncommitted changes.
2. Lists the posts in this publish: any `content/posts/**/index.md` changed since the last push. It flags `[DRAFT]` and `[future date]` posts.
3. Offers to set `draft: false` on drafts. If you say no, they stay drafts and **won't appear on the site**.
4. Checks each post's `coverImage` and `images/...` files exist. If any are missing, it asks whether to carry on.
5. Test-builds the whole site with Hugo into a temporary folder. If the build fails, nothing is pushed.
6. Commits everything (`git add -A`). The automatic message is `Publish: <post titles>`, or `Site update YYYY-MM-DD` if no posts changed. It shows the changes and asks before committing.
7. Pushes to GitHub.
8. If the GitHub CLI (`gh`) is installed and logged in, waits for the Actions build and reports if it fails.
9. Fetches each published post's URL until it returns HTTP 200, then reports it as live.
10. Pings **IndexNow** with the posts confirmed live (plus the home page, and any deleted posts that now return 404) so Bing, DuckDuckGo, Ecosia, Copilot/ChatGPT search, Yandex, Seznam, Naver and Yep re-crawl them within hours. Google doesn't use IndexNow – it still goes by the sitemap in Search Console. A failed ping is only a warning. Submissions show up in Bing Webmaster Tools under **IndexNow**.

**IndexNow key:** the key is the file `static/<key>.txt`, which contains nothing but its own name (32 hex characters), so Hugo publishes it at `https://intelligentdithering.com/<key>.txt` for the engines to verify. Don't delete or rename it. To replace it: delete the old file, then run `k=$(openssl rand -hex 16); printf '%s' "$k" > "static/$k.txt"` and publish. The ping is skipped until the new key file is live.

`publish.sh` doesn't run the SEO check, so run `./test.sh` first.

---

## 4. SEO checks before publishing

### The post checker

```bash
python3 tools/seo-check.py            # drafts + posts changed since the last push (what test.sh runs)
python3 tools/seo-check.py --all      # every post on the site
python3 tools/seo-check.py content/posts/2026/11/my-post-slug/index.md   # specific post(s)
python3 tools/seo-check.py --links    # also test external links (add --all for every post)
python3 tools/seo-check.py --help
```

It reads the Markdown files directly, so it needs no build and no extra Python packages. Each post gets ✔ (clean), ! (warnings) or ✘ (errors), and a total is printed at the end. It exits with code 1 if there are any errors and 0 otherwise. Warnings never fail it.

**Errors (fix before publishing):**

- No title
- Template placeholders left in (`Intro paragraph`, `![Alt text]`, `images/example.webp`)
- `coverImage` file not found in the post folder
- An image referenced in the post that doesn't exist
- An internal link to a page that doesn't exist
- A table-of-contents or `#anchor` link that doesn't match any heading in the post (it suggests the right one)

**Warnings (should fix):**

| Check | Why it matters |
|---|---|
| Title over 60 characters, or under 20 | Google cuts long titles off; short ones say too little. Add `seoTitle:` for a shorter search title |
| No `description:`, or not 70–160 characters | Without one, Google shows the first 155 characters of the post |
| No categories or tags; more than one category or more than 4 tags; a tag or category that isn't on the agreed list | Keeps tag pages useful (several posts each) instead of a sprawl of one-post pages |
| Slug not lowercase-hyphenated, or over 75 characters | Clean, readable URLs |
| No `coverImage` and no images at all | Shares and the home page fall back to the generic site image (if the post has any image, the first one is used automatically) |
| A `# ` H1 in the body, or skipped heading levels | The title is the H1; heading order helps search engines and screen readers |
| Long post with no `##` subheadings | Easier to skim, and gives Google sections to show |
| Images without alt text | Image search and accessibility |
| Images over 500 KB | Slow pages rank lower |
| Links with no text, or "click here"-style text | Link text tells Google what the destination is about |
| `http://` links to other sites | Insecure links |
| Internal links using the full `https://intelligentdithering.com/...` URL, or an old `/posts/YYYY/MM/...` URL | Use the relative `/post-slug/` path so there's no redirect hop |
| No links to other posts | Internal links help both readers and ranking |
| Under 300 words | Thin posts rarely rank |

### External link check (`--links`, opt-in)

Off by default because it makes a web request per link. A full `--all --links` run covers about 120 URLs and takes around a minute. It uses the Mac's `curl`, 8 links at a time, follows redirects, and times out after 20 seconds per link.

| Result | Reported as |
|---|---|
| 404 / 410, or the site can't be reached at all (DNS, connection refused, timeout, certificate error) | **ERROR** – dead link |
| Works, but now redirects to a *different* site | WARN – the domain may have been sold or the page moved |
| 401 / 403 / 405 / 429, or any failure from Amazon, `amzn.to`, social networks etc. | WARN – they block scripts; open the link by hand |
| Any other status (e.g. 500) | WARN |

Internal links (to your own posts) are always checked from the source files, with or without `--links`.

### What the site handles automatically

You don't need to check these per post. They're set up in `layouts/partials/seo.html` and friends:

- `<title>`, meta description, canonical URL
- Open Graph and Twitter/X cards with the post's image. Pages with no image of their own use `static/img/og-default.png`
- BlogPosting structured data on posts
- `sitemap.xml`, `robots.txt`, and real 301 redirects for every old WordPress URL in a post's `aliases` (generated into `.htaccess`)
- Image `alt` falls back to the post title if you forget. Write real alt text anyway, because the checker still warns.

### Optional manual checks after it's live

- **Share preview:** paste the post URL into a Mastodon draft, or a [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/) / [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/) check, to see the card.
- **Structured data:** run the post URL through Google's [Rich Results Test](https://search.google.com/test/rich-results).
- **Indexing:** in [Google Search Console](https://search.google.com/search-console), use URL Inspection → *Request indexing* for an important new post.
