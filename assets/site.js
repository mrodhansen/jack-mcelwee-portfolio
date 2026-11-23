(function () {
  // Old share links like #s06 opened a story in place; send them to its page.
  var oldLink = /^#(s\d\d)$/.exec(location.hash);
  if (oldLink) {
    var row = document.getElementById(oldLink[1]);
    if (row) {
      location.replace(row.querySelector('h3 a').href);
      return;
    }
  }

  var buttons = document.querySelectorAll('[data-filter]');
  var stories = document.querySelectorAll('.story');
  var status = document.getElementById('filter-status');

  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      var filter = button.getAttribute('data-filter');
      var shown = 0;
      buttons.forEach(function (other) {
        other.setAttribute('aria-pressed', String(other === button));
      });
      stories.forEach(function (story) {
        var match = filter === 'all' || story.getAttribute('data-section') === filter;
        story.hidden = !match;
        if (match) shown += 1;
      });
      status.textContent = 'Showing ' + shown + ' stories';
    });
  });

  var links = {};
  document.querySelectorAll('.nav a[href^="#"]').forEach(function (link) {
    links[link.getAttribute('href').slice(1)] = link;
  });
  var ids = Object.keys(links);
  var sections = ids.map(function (id) {
    var section = document.getElementById(id);
    if (!section) throw new Error('Nav link #' + id + ' has no matching section');
    return section;
  });

  function markCurrent() {
    var line = window.innerHeight * 0.35;
    var current = ids[0];
    sections.forEach(function (section) {
      if (section.getBoundingClientRect().top <= line) current = section.id;
    });
    var root = document.documentElement;
    if (window.innerHeight + window.scrollY >= root.scrollHeight - 2) {
      current = ids[ids.length - 1];
    }
    ids.forEach(function (id) {
      if (id === current) links[id].setAttribute('aria-current', 'location');
      else links[id].removeAttribute('aria-current');
    });
  }

  var queued = false;
  window.addEventListener(
    'scroll',
    function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(function () {
        queued = false;
        markCurrent();
      });
    },
    { passive: true }
  );
  window.addEventListener('resize', markCurrent);
  markCurrent();
})();
