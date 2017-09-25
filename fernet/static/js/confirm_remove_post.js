document.getElementById("remove").addEventListener("click", function (event) {
  if (!confirm('This will delete the post *permanently*!\nAre you sure you want to do that?')) {
    event.preventDefault();
  }
}, false)
