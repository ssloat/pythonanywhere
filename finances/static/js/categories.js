
var categories;

function addCategoryOptions(select, category_id) {
  for (var i=0; i<categories.length; i++) {
    var c = categories[i];
    select.append(
      $("<option>")
        .prop({value: c[0], selected: category_id==c[0]})
        .text(c[1])
    );
  }

  return select;
}

