#!/usr/bin/env python3
"""SEO checks for Intelligent Dithering posts (Markdown source, no dependencies).

    tools/seo-check.py                 # drafts + posts changed since origin/main
    tools/seo-check.py --all           # every post
    tools/seo-check.py content/posts/2025/07/foo/index.md ...

Prints ERROR / WARN / OK per post. Exit code 1 if any ERROR (missing image,
empty title, archetype placeholder left in), otherwise 0 - warnings never fail.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_HOST = "intelligentdithering.com"
SITE_SUFFIX = " | Intelligent Dithering"
# Same rules as layouts/partials/seo.html
TITLE_MAX = 60          # Google shows roughly 50-60 characters
DESC_MIN, DESC_MAX = 70, 160
MIN_WORDS = 300
MAX_IMAGE_KB = 500
PLACEHOLDERS = ["Intro paragraph", "![Alt text]", "images/example.webp"]

USE_COLOUR = sys.stdout.isatty()


def c(code, s):
    return f"\033[{code}m{s}\033[0m" if USE_COLOUR else s


# ---------------------------------------------------------------- helpers --
def split_front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def fm_value(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.*)$", fm, re.M | re.I)
    if not m:
        return None
    v = m.group(1).strip()
    if v.startswith("#"):
        return ""
    return re.sub(r"""^["'](.*)["']$""", r"\1", v)


def fm_list(fm, key):
    """Values of a YAML list (block or inline) for key."""
    m = re.search(rf"^{key}:[ \t]*(.*)$((?:\n[ \t]+-.*)*)", fm, re.M | re.I)
    if not m:
        return []
    inline, block = m.group(1).strip(), m.group(2)
    vals = []
    if inline.startswith("["):
        vals = [v.strip(" \"'") for v in inline.strip("[]").split(",")]
    elif inline:
        vals = [inline.strip("\"'")]
    vals += [v.strip(" \"'") for v in re.findall(r"^\s+-\s*(.*)$", block, re.M)]
    return [v for v in vals if v]


def strip_code(body):
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", body)


def plain_text(body):
    t = strip_code(body)
    t = re.sub(r"\{\{[<%].*?[%>]\}\}", " ", t, flags=re.S)     # shortcodes
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)                # images
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)             # links -> text
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"[#*_>|~-]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def known_post_urls():
    """Map of every post's URL and alias -> URL, from the Markdown sources."""
    urls, aliases = set(), {}
    base = os.path.join(ROOT, "content")
    for d, _, files in os.walk(base):
        if "index.md" not in files:
            continue
        rel = "/" + os.path.relpath(d, base).replace(os.sep, "/") + "/"
        fm, _ = split_front_matter(open(os.path.join(d, "index.md"), encoding="utf-8").read())
        url = fm_value(fm, "url") or rel
        url = "/" + url.strip("/") + "/"
        urls.add(url)
        for a in fm_list(fm, "aliases"):
            aliases["/" + a.strip("/") + "/"] = url
    for section in ("tags", "categories", "archive", "posts"):
        urls.add(f"/{section}/")
    return urls, aliases


# ----------------------------------------------------------------- checks --
def check(path, urls, aliases):
    errors, warns = [], []
    text = open(path, encoding="utf-8").read()
    fm, body = split_front_matter(text)
    post_dir = os.path.dirname(path)

    # Title
    title = fm_value(fm, "title") or ""
    seo_title = fm_value(fm, "seoTitle")
    shown = seo_title or title
    if not title:
        errors.append("No title")
    elif len(shown) > TITLE_MAX:
        warns.append(f"Title is {len(shown)} chars (aim for <= {TITLE_MAX}, Google truncates) "
                     f"- shorten it or add a shorter `seoTitle:`")
    elif len(shown) < 20:
        warns.append(f"Title is only {len(shown)} chars - make it more descriptive")

    # Description (falls back to the summary, which is often a poor snippet)
    desc = fm_value(fm, "description")
    if not desc:
        summary = body.split("<!--more-->")[0] if "<!--more-->" in body else ""
        if summary:
            s = plain_text(summary)
            if len(s) < DESC_MIN:
                warns.append(f"No `description:` and the intro before <!--more--> is only {len(s)} chars")
            else:
                warns.append(f"No `description:` - search results will use the first {DESC_MAX} chars "
                             f"of the intro. Add one ({DESC_MIN}-{DESC_MAX} chars) to control the snippet")
        else:
            warns.append("No `description:` and no <!--more--> - add a description "
                         f"({DESC_MIN}-{DESC_MAX} chars)")
    elif not DESC_MIN <= len(desc) <= DESC_MAX:
        warns.append(f"Description is {len(desc)} chars (aim for {DESC_MIN}-{DESC_MAX})")

    # Taxonomies
    cats = fm_list(fm, "categories")
    tags = fm_list(fm, "tags")
    if not cats:
        warns.append("No categories (archetype \"\" placeholder counts as none)")
    if not tags:
        warns.append("No tags")
    for t in tags + cats:
        if t != t.lower() or " " in t:
            warns.append(f"Tag/category '{t}' - use lowercase-hyphenated so it matches existing ones")

    # URL / folder name
    slug = fm_value(fm, "slug") or os.path.basename(post_dir)
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        warns.append(f"URL slug '{slug}' should be lowercase words separated by hyphens")
    elif len(slug) > 75:
        warns.append(f"URL slug is {len(slug)} chars - shorter URLs read better in results")

    # Cover / share image
    cover = fm_value(fm, "coverImage")
    if not cover:
        warns.append("No coverImage - social shares and the home page will use the first image or the site default")
    elif not cover.startswith("/") and not cover.startswith("http"):
        found = any(os.path.basename(cover) == f for _, _, fs in os.walk(post_dir) for f in fs)
        if not found:
            errors.append(f"coverImage '{cover}' not found in the post folder")

    # Placeholders left over from the archetype
    for p in PLACEHOLDERS:
        if p in text:
            errors.append(f"Archetype placeholder still in post: {p!r}")

    code_free = strip_code(body)

    # Headings
    if re.search(r"^#\s", code_free, re.M):
        warns.append("Body has a '# ' H1 - the title is already the page's H1, use '## ' for sections")
    levels = [len(h) for h in re.findall(r"^(#{2,6})\s", code_free, re.M)]
    for a, b in zip(levels, levels[1:]):
        if b > a + 1:
            warns.append(f"Heading level jumps from H{a} to H{b} - don't skip levels")
            break
    if plain_text(body) and len(plain_text(body).split()) > 600 and not levels:
        warns.append("Long post with no '## ' subheadings - add some to break it up")

    # Images
    images = re.findall(r"!\[([^\]]*)\]\(\s*<?([^)\s>]+)", code_free)
    for tag in re.findall(r"<img\b[^>]*>", code_free, re.I):
        src = re.search(r"""\bsrc=["']([^"']+)""", tag)
        alt = re.search(r"""\balt=["']([^"']*)""", tag)
        if src:
            images.append((alt.group(1) if alt else "", src.group(1)))
    no_alt = 0
    for alt, src in images:
        if not alt.strip():
            no_alt += 1
        if src.startswith(("http://", "https://", "/")):
            continue
        f = os.path.join(post_dir, src)
        if not os.path.isfile(f):
            errors.append(f"Missing image file: {src}")
        elif os.path.getsize(f) > MAX_IMAGE_KB * 1024:
            warns.append(f"{src} is {os.path.getsize(f) // 1024} KB - compress it or convert to WebP "
                         f"(slow pages rank lower)")
    if no_alt:
        warns.append(f"{no_alt} image(s) with no alt text - describe what the image shows, e.g. ![Pi 5 on a desk](...)")

    # Links
    for label, href in re.findall(r"(?<!!)\[([^\]]*)\]\(\s*<?([^)\s>]+)", code_free):
        if not label.strip():
            warns.append(f"Link with no text: {href}")
        if re.match(r"(?i)^(click here|here|this|link|read more)$", label.strip()):
            warns.append(f"Vague link text '{label}' - describe the destination instead")
        if href.startswith("http://") and SITE_HOST not in href:
            warns.append(f"Insecure http:// link: {href}")
        m = re.match(rf"^(?:https?://(?:www\.)?{re.escape(SITE_HOST)})?(/[^#?]*)", href)
        if m and not href.startswith("//"):
            p = m.group(1)
            if re.search(r"\.[a-z0-9]{2,5}$", p, re.I):      # file e.g. /img/x.png, /index.xml
                continue
            p = "/" + p.strip("/") + "/" if p != "/" else "/"
            if href.startswith("http"):
                warns.append(f"Internal link uses full URL - use a relative path: {href}")
            if p in aliases:
                warns.append(f"Link goes to an old URL that redirects - use {aliases[p]} instead of {p}")
            elif p.startswith(("/tag/", "/category/")):
                warns.append(f"Old WordPress archive link {p} - use /{'tags' if '/tag/' in p else 'categories'}/"
                             f"{p.split('/')[2]}/")
            elif p != "/" and p not in urls and not p.startswith(("/tags/", "/categories/", "/page/")):
                errors.append(f"Internal link to a page that doesn't exist: {p}")

    internal = len(re.findall(rf"\]\((?:https?://(?:www\.)?{re.escape(SITE_HOST)})?/(?!/)", code_free))
    if internal == 0:
        warns.append("No links to other posts on the site - add one or two relevant internal links")

    # Length
    words = len(plain_text(body).split())
    if words < MIN_WORDS:
        warns.append(f"Only {words} words - thin posts rarely rank; aim for {MIN_WORDS}+")

    return title, errors, warns, words


# ------------------------------------------------------------------ main --
def changed_posts():
    """Draft posts plus posts changed/untracked relative to origin/main."""
    files = set()
    git = ["git", "-C", ROOT]
    for cmd in (git + ["diff", "--name-only", "origin/main", "--", "content"],
                git + ["ls-files", "--others", "--exclude-standard", "--", "content"],
                git + ["diff", "--name-only", "HEAD", "--", "content"]):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, check=False).stdout
        except OSError:
            out = ""
        files.update(l for l in out.splitlines() if re.match(r"content/posts/.+/index\.md$", l))
    for d, _, fs in os.walk(os.path.join(ROOT, "content", "posts")):
        if "index.md" in fs:
            p = os.path.join(d, "index.md")
            fm, _ = split_front_matter(open(p, encoding="utf-8").read())
            if (fm_value(fm, "draft") or "").lower() == "true":
                files.add(os.path.relpath(p, ROOT))
    return sorted(os.path.join(ROOT, f) for f in files if os.path.isfile(os.path.join(ROOT, f)))


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__.strip())
        return 0
    if "--all" in args:
        paths = sorted(os.path.join(d, "index.md") for d, _, fs in os.walk(os.path.join(ROOT, "content", "posts"))
                       if "index.md" in fs)
    elif args:
        paths = [os.path.abspath(a) for a in args]
    else:
        paths = changed_posts()

    if not paths:
        print("SEO check: no draft or changed posts to check (use --all to check everything)")
        return 0

    urls, aliases = known_post_urls()
    total_err = total_warn = 0
    for p in paths:
        title, errors, warns, words = check(p, urls, aliases)
        total_err += len(errors)
        total_warn += len(warns)
        rel = os.path.relpath(p, ROOT)
        status = c("31", "✘") if errors else (c("33", "!") if warns else c("32", "✔"))
        print(f"\n{status} {c('1', title or rel)}  ({words} words)\n  {c('2', rel)}")
        for e in errors:
            print(f"  {c('31', 'ERROR')} {e}")
        for w in warns:
            print(f"  {c('33', 'WARN ')} {w}")
    print(f"\nSEO check: {len(paths)} post(s), {total_err} error(s), {total_warn} warning(s)")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
