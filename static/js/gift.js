function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  ev.dataTransfer.setData("text", ev.target.id);
  var source = ev.target.parentElement.getAttribute('data-section');
  ev.target.setAttribute('data-from', source)
}

function drop(ev) {
  ev.preventDefault();
  var data = ev.dataTransfer.getData("text");
  child = document.getElementById(data);
  var steals = parseInt(ev.target.parentElement.nextElementSibling.innerHTML); // Steals TD
  var parentTD = ev.target.parentElement;
  if (ev.target.nodeName == 'DIV') {
    if (child.getAttribute('data-from') == 'assign-gift' && steals <= 1) {
      ev.target.appendChild(child);
      ev.target.parentElement.nextElementSibling.innerHTML = steals + 1;
      child.removeAttribute("style");
    }
    else if (child.getAttribute('data-from') == 'gift-data') {
      ev.target.appendChild(child);
      var input = document.createElement("input");
      input.type = "hidden";
      input.name = "from";
      input.value = child.getAttribute('data-gift-from');
      parentTD.appendChild(input);
      child.removeAttribute("style");
    }
  }
}

function disableCheckboxOnceRevealed(ev) {
  if (ev.checked) {
    ev.setAttribute("disabled", "true");
  }
}

function previewImage(ev) {
  var url = ev.getAttribute('src');
  window.open(url, 'Image')
}