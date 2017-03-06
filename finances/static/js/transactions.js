var categories;
function processCategories(data) {
  categories = data;

  var select = $("div.modal table#transaction select");
  select.empty();
  for (var i=0; i<categories.length; i++) {
    c = categories[i]
    select.append($("<option>").prop({value: c[0]}).text(c[1]));
  }
}
function categoriesInput(category_id) {
  var select = $("<select>").prop('class', 'form-control');
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

var monthly_data;
function drawVisualization() {
  var data = google.visualization.arrayToDataTable(monthly_data);
  var options = {seriesType: 'bars', series: {1: {type: 'line'}}};

  var chart = new google.visualization.ComboChart(document.getElementById('chart_div'));
  chart.draw(data, options);
}

function processTransactions(data) {
  monthly_data = data.monthly_data;
  var table = $("table#transactions tbody");
  table.empty();
  for (var i=0; i<data.transactions.length; i++) {
    var item = data.transactions[i];
    var row = $("<tr>")
      .append("<td><a data-toggle='modal' href='#modalEdit'>"+item.id+"</a></td>")
      .append("<td><input type='text' class='datepicker form-control' value='"+item.date+"'></input></td>")
      .append($("<td>").append($("<input>").prop({type: 'text', class: 'form-control', value: item.name})))
      .append(
        $("<td>").append(categoriesInput(item.category_id, data.categories))
      )
      .append($("<td>").text(numeral(item.amount).format('0,0.00')))
      .append(
        $("<td>").append(
          $("<input>").prop({type: 'checkbox', class: 'form-control', checked: item.yearly})
        )
      )
    ;

    table.append(row);
  }

  $("table#transactions tbody tr td a").click(function(){
    var tds = $(this).parent().parent().find('td');
    var dests = $("div#modalEdit table#transaction tr");
    $("div#modalEdit h4.modal-title").text("Transaction " + $(tds[0]).find('a').text());
    $("div#modalEdit input#tid").val( $(tds[0]).find('a').text() );
    $(dests[0]).find("input").val( $(tds[1]).find('input').val() );
    $(dests[1]).find("input").val( $(tds[2]).find('input').val() );
    $(dests[2]).find("option").each(function(i, elem){
      if ($(elem).attr('value') == $(tds[3]).find('select').val()) {
        $(elem).prop('selected', true);
      }
    });
    $(dests[3]).find("input").val( $(tds[4]).text() );
    $(dests[4]).find("input").prop('checked', $(tds[5]).find('input').prop('checked'));
  });

  google.charts.setOnLoadCallback(drawVisualization);
}

function editModal_update() {
  var trs = $(document.body).find("div#modalEdit table#transaction tr");
  $.post(
    "{{url_for('transaction.rest_update_transaction', category_id=category_id)}}", 
    {
      'id': $("div#modalEdit input#tid").val(),
      'date': $(trs[1]).find('input').val(),
      'name': $(trs[2]).find('input').val(),
      'category_id': $(trs[3]).find('select').val(),
      'amount': $(trs[4]).find('input').val(), 
      'yearly': $(trs[5]).find('input').prop('checked')
    },
    function(data, status) {
      processTransactions(data);
      $('div#modalEdit').modal('hide');
    }
  );
} 

function editModal_split() {
  var trs = $(document.body).find("div#modalEdit table#transaction tr");
  var dests = $("div#modalSplit table#transaction tr");
  var tid = $("div#modalEdit input#tid").val(); 
  $("div#modalSplit h4.modal-title").text("Split Transaction " + tid);
  $("div#modalSplit input#tid").val(tid);
  $(dests[0]).find("input").val( $(trs[0]).find('input').val() );
  $(dests[1]).find("input").first().val( $(trs[1]).find('input').val() );
  $(dests[2]).find("select").first().find("option").each(function(i, elem){
    if ($(elem).attr('value') == $(trs[2]).find('select').val()) {
      $(elem).prop('selected', true);
    }
  });
  $(dests[3]).find("input").first().val( $(trs[3]).find('input').val() );
  $(dests[4]).find("input").first().prop('checked', $(trs[4]).find('input').prop('checked'));

  $('div#modalEdit').modal('hide');
  $('div#modalSplit').modal('show');
} 

function splitModal_update() {
  var trs = $(document.body).find("div#modalSplit table#transaction tr");
  $.post(
    "{{url_for('transaction.rest_split_transaction', category_id=category_id)}}", 
    {
      'curr': {
        'id': $("div#modalSplit input#tid").val(),  
        'date': $(trs[0]).find('input').first().val(),
        'name': $(trs[1]).find('input').first().val(),
        'category_id': $(trs[2]).find('select').first().val(),
        'amount': $(trs[3]).find('input').first().val(), 
        'yearly': $(trs[4]).find('input').first().prop('checked')
      },
      'new': {
        'date': $(trs[0]).find('input').last().val(),
        'name': $(trs[1]).find('input').last().val(),
        'category_id': $(trs[2]).find('select').last().val(),
        'amount': $(trs[3]).find('input').last().val(), 
        'yearly': $(trs[4]).find('input').last().prop('checked')
       }
    },
    function(data, status) {
      processTransactions(data);
      $('div#modalSplit').modal('hide');
    }
  );
} 
