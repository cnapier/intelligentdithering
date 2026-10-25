// https://stackoverflow.com/questions/1912501/unescape-html-entities-in-javascript
function htmlDecode(input) {
  var e = document.createElement('textarea');
  e.innerHTML = input;
  // handle case of empty input
  return e.childNodes.length === 0 ? "" : e.childNodes[0].nodeValue;
}

SimpleJekyllSearch({
  searchInput: document.getElementById('search-input'),
  resultsContainer: document.getElementById('search-results'),
  json: '{{ "index.json" | relURL }}',
  // Site override: title + short description + date, instead of the whole post
  searchResultTemplate:
    '<div class="search-result"><a href="{url}">{thumb}' +
    '<span class="search-result-text">' +
    '<span class="search-result-title">{title}</span>' +
    '<span class="search-result-desc">{description}</span>' +
    '<span class="search-result-date">{date}</span>' +
    '</span></a></div>',
  noResultsText: '<p class="search-no-results">No posts found</p>',
  limit: 20,
  fuzzy: false,
  // Titles and descriptions can contain HTML entities (&rsquo; etc.) – decode them
  templateMiddleware: function (prop, value) {
      if (prop === 'thumb') {
          return value
              ? '<img class="search-result-thumb" src="' + value + '" width="60" height="60" alt="" loading="lazy">'
              : '<span class="search-result-thumb search-result-thumb--empty"></span>';
      }
      if (prop === 'title' || prop === 'description') {
          return htmlDecode(value);
      }
  }
});

// Site override of the theme's search.js (assets/js/ beats themes/puppet/assets/js/).
// Spotlight-style panel: Esc or a click outside closes it, ↑/↓ move through the
// results, Enter opens the highlighted one, and "/" or Cmd/Ctrl+K opens search
// from anywhere. Focus goes back to the search button on close.
$(document).ready(function () {
  var $searchPage = $('.search-page');
  var $searchOpen = $('.search-icon');
  var $searchClose = $('.search-icon-close');
  var $searchInput = $('#search-input');
  var $results = $('#search-results');
  var $body = $('body');
  var prevClasses = '';
  var selected = 0;

  function isOpen() { return $searchPage.hasClass('search-active'); }
  function links() { return $results.find('.search-result a'); }

  function select(i) {
      var $l = links();
      $l.removeClass('is-selected').attr('aria-selected', 'false');
      if (!$l.length) return;
      selected = Math.max(0, Math.min(i, $l.length - 1));
      var el = $l.eq(selected).addClass('is-selected').attr('aria-selected', 'true')[0];
      if (el.scrollIntoView) el.scrollIntoView({ block: 'nearest' });
  }

  function openSearch() {
      if (isOpen()) return;
      prevClasses = $body.attr('class') || '';
      $searchPage.addClass('search-active');
      $body.addClass('no-scroll');
      setTimeout(function () { $searchInput.trigger('focus').select(); }, 50);
  }

  function closeSearch() {
      if (!isOpen()) return;
      $searchPage.removeClass('search-active');
      $body.attr('class', prevClasses);
      $searchOpen.find('button').trigger('focus');
  }

  // Highlight the first result whenever the result list changes
  if (window.MutationObserver) {
      new MutationObserver(function () { select(0); }).observe($results[0], { childList: true });
  }

  $searchOpen.on('click', function (e) {
      e.preventDefault();
      if (isOpen()) { closeSearch(); } else { openSearch(); }
  });

  $searchClose.on('click', function (e) {
      e.preventDefault();
      closeSearch();
  });

  // Click on the dimmed backdrop (outside the panel) closes search
  $searchPage.on('mousedown', function (e) {
      if (e.target === this) closeSearch();
  });

  $(document).on('keydown', function (e) {
      var key = e.key;
      if (!isOpen()) {
          var typing = /^(input|textarea|select)$/i.test(e.target.tagName) || e.target.isContentEditable;
          if ((key === '/' && !typing) || ((e.metaKey || e.ctrlKey) && (key === 'k' || key === 'K'))) {
              e.preventDefault();
              openSearch();
          }
          return;
      }
      if (key === 'Escape' || key === 'Esc') {
          e.preventDefault();
          closeSearch();
      } else if (key === 'ArrowDown') {
          e.preventDefault();
          select(selected + 1);
      } else if (key === 'ArrowUp') {
          e.preventDefault();
          select(selected - 1);
      } else if (key === 'Enter' && e.target === $searchInput[0]) {
          var $l = links();
          if ($l.length) {
              e.preventDefault();
              window.location.href = $l.eq(selected).attr('href');
          }
      }
  });

  // Mouse hover moves the highlight too, so keyboard and mouse agree
  $results.on('mousemove', '.search-result a', function () {
      var i = links().index(this);
      if (i !== selected) select(i);
  });
});
