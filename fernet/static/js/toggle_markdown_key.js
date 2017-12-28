function show_key(e, show, hide) {
  e.style.display = 'block';
  show.style.display = 'none';
  hide.style.display = 'block';
}

function hide_key(e, show, hide) {
  e.style.display = 'none';
  hide.style.display = 'none';
  show.style.display = 'block';
}

function init_toggles(e) {
  var show = document.createElement('button');
  var hide = document.createElement('button');

  show.setAttribute('type', 'button');
  hide.setAttribute('type', 'button');

  show.innerText = 'Show markdown key';
  hide.innerText = 'Hide key';

  show.addEventListener('click', function () { show_key(e, show, hide) });
  hide.addEventListener('click', function () { hide_key(e, show, hide) });

  e.parentNode.insertBefore(show, e);
  e.parentNode.insertBefore(hide, e);

  hide_key(e, show, hide);
}

function init() {
  var es = document.getElementsByClassName('markdown-key');

  for (var i = 0; i < es.length; i++) {
    init_toggles(es[i]);
  }
}

init();
