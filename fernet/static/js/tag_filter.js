function tagFilter(form) {
  filter = form.getElementsByClassName("tag-filter")[0];

  filter.addEventListener("input", function () {
    var re = new RegExp(this.value, "i");

    var tags = form.getElementsByClassName("tags")[0].getElementsByClassName("field");

    for (var i = 0; i < tags.length; i++) {
      var label = tags[i].getElementsByTagName("label")[0];

      if (re.test(label.innerHTML)) {
        tags[i].style.display = "block";
      } else {
        tags[i].style.display = "none";
      }
    }
  })
}

var forms = document.getElementsByClassName("tag-set");
for (var f = 0; f < forms.length; f++) {
  var form = forms[f];
  tagFilter(form);
}
