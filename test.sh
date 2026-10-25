#!/usr/bin/env bash
# Preview the site locally (drafts and future posts included), after an SEO check
# of any draft or changed posts.
#
#   ./test.sh            # SEO-check drafts/changed posts, then start the preview server
#   ./test.sh --all      # SEO-check every post first
#   ./test.sh --links    # ...and fetch every external link in those posts (slow)
#   ./test.sh --all --links
#   SKIP_SEO=1 ./test.sh # straight to the server

cd ~/Sites/IntelligentDithering/ || exit 1

if [ -z "${SKIP_SEO:-}" ]; then
  if command -v python3 >/dev/null; then
    python3 tools/seo-check.py "$@"
    if [ $? -ne 0 ]; then
      printf '\n\033[31mSEO check found errors (above) – fix them before publishing.\033[0m Starting preview anyway…\n\n'
    fi
  else
    echo "python3 not found – skipping SEO check (xcode-select --install)"
  fi
fi

mkdir -p /tmp/hugotest
open http://127.0.0.1:1313
hugo server --buildFuture -D --cleanDestinationDir --bind 0.0.0.0 --buildDrafts -d /tmp/hugotest/
