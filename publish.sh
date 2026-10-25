#!/usr/bin/env bash
# Publish the site: check posts, test-build, commit, push, then wait for it to go live.
#
#   ./publish.sh                  # auto commit message from changed post titles
#   ./publish.sh "Fix typo"       # your own commit message
#   ./publish.sh -y               # don't ask before un-drafting posts
#
# Needs: git, hugo. Optional: gh (GitHub CLI, logged in) to follow the build.
# Written for macOS's bash 3.2, so no arrays-of-arrays or GNU-only flags.

set -euo pipefail

SITE_URL="${SITE_URL:-https://intelligentdithering.com}"
LIVE_CHECKS="${LIVE_CHECKS:-24}"   # x5s = how long to wait for posts to go live
BRANCH="main"
WORKFLOW="deploy.yml"

ASSUME_YES=0
MSG=""
for arg in "$@"; do
  case "$arg" in
    -y|--yes) ASSUME_YES=1 ;;
    -h|--help) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) MSG="$arg" ;;
  esac
done

cd "$(dirname "$0")"

bold()  { printf '\033[1m%s\033[0m\n' "$*"; }
ok()    { printf '\033[32m✔\033[0m %s\n' "$*"; }
warn()  { printf '\033[33m!\033[0m %s\n' "$*"; }
die()   { printf '\033[31m✘ %s\033[0m\n' "$*" >&2; exit 1; }
ask()   { [ "$ASSUME_YES" = 1 ] && return 0; printf '%s [y/N] ' "$1"; read -r a; [ "$a" = y ] || [ "$a" = Y ]; }
fm()    { { grep -m1 "^$2:" "$1" || true; } | sed -E "s/^$2:[[:space:]]*//; s/^[\"']//; s/[\"'][[:space:]]*\$//"; }
post_url() { echo "$SITE_URL/$(basename "$(dirname "$1")")/"; }   # posts are served at /<slug>/

command -v git  >/dev/null || die "git not found"
command -v hugo >/dev/null || die "hugo not found (brew install hugo)"

# --- 1. Branch and remote -----------------------------------------------------
[ "$(git rev-parse --abbrev-ref HEAD)" = "$BRANCH" ] || die "Not on $BRANCH branch"
bold "Syncing with GitHub…"
git fetch -q origin "$BRANCH"
if [ -n "$(git status --porcelain)" ]; then
  git pull -q --rebase --autostash origin "$BRANCH" || die "Pull failed – sort out the conflict, then re-run"
else
  git pull -q --rebase origin "$BRANCH" || die "Pull failed"
fi
ok "Up to date with origin/$BRANCH"

# --- 2. Which posts are being published? --------------------------------------
CHANGED=$( { git status --porcelain --untracked-files=all -- content | sed -E 's/^.{3}//; s/.* -> //'
             git diff --name-only "origin/$BRANCH" -- content; } \
           | grep -E '^content/posts/.+/index\.md$' | sort -u || true)

TODAY=$(date -u +%Y-%m-%d)
PUBLISHING=""
PROBLEMS=0
if [ -n "$CHANGED" ]; then
  bold "Posts in this publish:"
  for f in $CHANGED; do
    [ -f "$f" ] || { echo "  - (deleted) $f"; continue; }
    title=$(fm "$f" title); draft=$(fm "$f" draft); date=$(fm "$f" date | cut -c1-10)
    line="  - $title"
    if [ "$draft" = "true" ]; then
      line="$line  [DRAFT]"
    fi
    if [[ "$date" > "$TODAY" ]]; then
      line="$line  [future date $date – won't appear until a later rebuild]"
    fi
    echo "$line"
  done

  DRAFTS=""
  for f in $CHANGED; do
    [ -f "$f" ] && [ "$(fm "$f" draft)" = "true" ] && DRAFTS="$DRAFTS $f"
  done
  if [ -n "$DRAFTS" ]; then
    if ask "Mark the draft post(s) above as published (draft: false)?"; then
      for f in $DRAFTS; do perl -pi -e 's/^draft:\s*true\s*$/draft: false\n/' "$f"; done
      ok "Drafts set to draft: false"
    else
      warn "Leaving drafts as drafts – they won't appear on the site"
    fi
  fi

  for f in $CHANGED; do
    [ -f "$f" ] || continue
    [ "$(fm "$f" draft)" = "true" ] && continue
    # Check coverImage and local images actually exist
    dir=$(dirname "$f")
    cover=$(fm "$f" coverImage)
    if [ -n "$cover" ] && [ -z "$(find "$dir" -name "$(basename "$cover")" | head -1)" ]; then
      warn "$(fm "$f" title): coverImage '$cover' not found in $dir"
      PROBLEMS=1
    fi
    for img in $(grep -oE '\]\(images/[^) ]+' "$f" | sed 's/^](//' || true); do
      [ -f "$dir/$img" ] || { warn "$(fm "$f" title): missing image $img"; PROBLEMS=1; }
    done
    PUBLISHING="$PUBLISHING $f"
  done
  if [ "$PROBLEMS" = 1 ]; then
    ask "Publish anyway with the problems above?" || die "Stopped – fix the images and re-run"
  fi
else
  echo "No post changes – publishing site changes only."
fi

# --- 3. Test build ------------------------------------------------------------
bold "Test build…"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
if ! hugo --quiet --minify --gc -d "$TMP/public" 2>"$TMP/err"; then
  cat "$TMP/err"; die "Hugo build failed – nothing pushed"
fi
grep -i 'error' "$TMP/err" && die "Hugo reported errors – nothing pushed"
ok "Site builds ($(find "$TMP/public" -name '*.html' | wc -l | tr -d ' ') pages)"

# --- 4. Commit and push -------------------------------------------------------
git add -A
if git diff --cached --quiet; then
  if [ "$(git rev-list --count "origin/$BRANCH..HEAD")" = 0 ]; then
    ok "Nothing to publish"; exit 0
  fi
else
  if [ -z "$MSG" ]; then
    titles=""
    for f in $PUBLISHING; do titles="${titles:+$titles, }$(fm "$f" title)"; done
    MSG=${titles:+"Publish: $titles"}
    MSG=${MSG:-"Site update $(date +%Y-%m-%d)"}
  fi
  echo; git status --short; echo
  ask "Commit and push as \"$MSG\"?" || die "Cancelled – nothing pushed (changes are staged)"
  git commit -q -m "$MSG"
fi
git push -q origin "$BRANCH"
SHA=$(git rev-parse HEAD)
ok "Pushed ${SHA:0:7} to GitHub"

# --- 5. Follow the build and check it's live ----------------------------------
if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
  bold "Waiting for GitHub Actions…"
  RUN=""
  for _ in $(seq 1 15); do
    RUN=$(gh run list --workflow "$WORKFLOW" --commit "$SHA" --limit 1 --json databaseId -q '.[0].databaseId' 2>/dev/null || true)
    [ -n "$RUN" ] && break; sleep 2
  done
  if [ -n "$RUN" ]; then
    gh run watch "$RUN" --exit-status --interval 5 >/dev/null || die "Build failed – see: gh run view $RUN --log-failed"
    ok "Build finished"
  else
    warn "Couldn't find the Actions run – check the Actions tab on GitHub"
  fi
else
  warn "gh not installed/logged in – check the Actions tab on GitHub for the build"
fi

for f in $PUBLISHING; do
  url=$(post_url "$f")
  printf '  Checking %s ' "$url"
  for _ in $(seq 1 "$LIVE_CHECKS"); do
    code=$(curl -s -o /dev/null -w '%{http_code}' "$url" || true)
    [ "$code" = 200 ] && break; printf '.'; sleep 5
  done
  [ "$code" = 200 ] && printf ' \033[32mlive\033[0m\n' || printf ' \033[33mnot live yet (HTTP %s)\033[0m\n' "$code"
done

ok "Done"
