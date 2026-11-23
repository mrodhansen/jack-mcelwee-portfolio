// Loaded in <head> on every page so the saved theme is applied before the page
// paints. On the home page it also builds the theme picker in the About section.
(function () {
  'use strict';

  var STORAGE_KEY = 'jack-mcelwee-portfolio:theme';
  var DEFAULT_ID = 'index';
  var FONTS_URL = 'https://fonts.googleapis.com/css2?';

  // Index uses the IBM Plex fonts every page already loads; the others add
  // their own Google Fonts only when chosen.
  var THEMES = [
    {
      id: 'index',
      name: 'Index',
      note: 'The original: paper, black rules and a side menu.',
    },
    {
      id: 'broadsheet',
      name: 'Broadsheet',
      note: 'Newspaper columns, serif headlines and a red accent.',
      fonts:
        'family=Libre+Franklin:wght@400;500;600;700' +
        '&family=Playfair+Display:ital,wght@0,400;0,700;0,800;0,900;1,400' +
        '&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400',
    },
    {
      id: 'night',
      name: 'Night Desk',
      note: 'Dark mode with story cards and amber accents.',
      fonts: 'family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700',
    },
    {
      id: 'gallery',
      name: 'Gallery',
      note: 'Large type and big photos on a clean white grid.',
      fonts: 'family=Inter+Tight:wght@500;600;700&family=Inter:wght@400;500;600',
    },
    {
      id: 'sagebrush',
      name: 'Sagebrush',
      note: 'Soft greens, rounded photos that alternate sides.',
      fonts:
        'family=DM+Mono:wght@400;500' +
        '&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600' +
        '&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400',
    },
    {
      id: 'wire',
      name: 'Wire',
      note: 'News-service blue with stories on a dated timeline.',
      fonts:
        'family=Source+Sans+3:wght@400;500;600;700' +
        '&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400',
    },
    {
      id: 'capitol',
      name: 'Capitol',
      note: 'Navy sidebar and a two-column list of clips, like a résumé.',
      fonts: 'family=Public+Sans:wght@400;500;600;700&family=Spectral:ital,wght@0,400;0,500;0,600;1,400',
    },
  ];

  var BLOCKED_MESSAGE =
    'This browser is blocking saved site settings, so your theme will reset when you leave the page.';

  var root = document.documentElement;

  function findTheme(id) {
    for (var i = 0; i < THEMES.length; i += 1) {
      if (THEMES[i].id === id) return THEMES[i];
    }
    return null;
  }

  var defaultTheme = findTheme(DEFAULT_ID);

  // Reading localStorage throws when the browser blocks site storage (some
  // private modes, blocked cookies). The picker then says so instead of
  // pretending the choice was saved.
  var storage = null;
  try {
    storage = window.localStorage;
    storage.getItem(STORAGE_KEY);
  } catch (err) {
    storage = null;
  }

  function savedTheme() {
    if (!storage) return defaultTheme;
    var id = storage.getItem(STORAGE_KEY);
    if (id === null) return defaultTheme;
    var theme = findTheme(id);
    if (theme) return theme;
    // A theme saved by an older version of the site that no longer exists.
    storage.removeItem(STORAGE_KEY);
    console.warn('Saved theme "' + id + '" does not exist any more; showing ' + DEFAULT_ID + '.');
    return defaultTheme;
  }

  function loadFonts(theme) {
    if (!theme.fonts) return;
    var id = 'theme-fonts-' + theme.id;
    if (document.getElementById(id)) return;
    var link = document.createElement('link');
    link.id = id;
    link.rel = 'stylesheet';
    link.href = FONTS_URL + theme.fonts + '&display=swap';
    document.head.appendChild(link);
  }

  function apply(theme) {
    loadFonts(theme);
    root.setAttribute('data-theme', theme.id);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (!meta) throw new Error('Page is missing <meta name="theme-color">');
    var color = getComputedStyle(root).getPropertyValue('--theme-color').trim();
    if (color) meta.setAttribute('content', color);
  }

  function showWarning(warning, message) {
    warning.textContent = message;
    warning.hidden = false;
  }

  function choose(theme, warning) {
    apply(theme);
    if (!storage) return;
    try {
      storage.setItem(STORAGE_KEY, theme.id);
      warning.hidden = true;
    } catch (err) {
      showWarning(
        warning,
        'This browser would not save your choice (' + err.name + '), so the theme will reset when you leave the page.'
      );
    }
  }

  function option(theme, current, warning) {
    var label = document.createElement('label');
    label.className = 'theme-option';

    var input = document.createElement('input');
    input.type = 'radio';
    input.name = 'site-theme';
    input.value = theme.id;
    input.checked = theme.id === current.id;
    input.addEventListener('change', function () {
      choose(theme, warning);
    });

    var swatch = document.createElement('span');
    swatch.className = 'swatch';
    swatch.setAttribute('data-preview', theme.id);
    swatch.setAttribute('aria-hidden', 'true');
    ['sw-rail', 'sw-title', 'sw-text', 'sw-accent'].forEach(function (part) {
      var piece = document.createElement('i');
      piece.className = part;
      swatch.appendChild(piece);
    });

    var name = document.createElement('span');
    name.className = 'theme-name';
    name.textContent = theme.name;

    var note = document.createElement('span');
    note.className = 'theme-desc';
    note.textContent = theme.note;

    label.appendChild(input);
    label.appendChild(swatch);
    label.appendChild(name);
    label.appendChild(note);
    return label;
  }

  function buildPicker(current) {
    var picker = document.getElementById('theme-picker');
    if (!picker) return;
    var list = picker.querySelector('.theme-options');
    var warning = picker.querySelector('.theme-warn');
    if (!list || !warning) throw new Error('#theme-picker needs .theme-options and .theme-warn');
    THEMES.forEach(function (theme) {
      list.appendChild(option(theme, current, warning));
    });
    if (!storage) showWarning(warning, BLOCKED_MESSAGE);
    picker.hidden = false;
  }

  var current = savedTheme();
  apply(current);
  document.addEventListener('DOMContentLoaded', function () {
    buildPicker(current);
  });
})();
