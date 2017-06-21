
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
      .append($("<td>").text(item.date))
      .append($("<td>").text(item.name))
      .append(
        $("<td>").append( 
          addCategoryOptions(
            $("<select>").prop({class: 'form-control'}).attr({disabled: true}), 
            item.category_id
          )
        )
      )
      .append($("<td>").text(numeral(item.amount).format('0,0.00')))
      .append(
        $("<td>").append(
          $("<input>")
            .prop({type: 'checkbox', class: 'form-control', checked: item.yearly})
            .attr({disabled: true})
        )
      )
    ;

    table.append(row);
  }

  $("table#transactions tbody tr td a").click(function(){
    var tds = $(this).parent().parent().find('td');
    $("div#modalEdit h4.modal-title").text("Transaction " + $(tds[0]).find('a').text());
    $("div#modalEdit input#tid").val( $(tds[0]).find('a').text() );
    $("input#me_date").val( $(tds[1]).text() );
    $("input#me_name").val( $(tds[2]).text() );
    $("select#me_category option").each(function(i, elem){
      if ($(elem).attr('value') == $(tds[3]).find('select').val()) {
        $(elem).prop('selected', true);
      }
    });
    $("input#me_amount").val( $(tds[4]).text() );
    $("input#me_yearly").prop('checked', $(tds[5]).find('input').prop('checked'));
  });

  google.charts.setOnLoadCallback(drawVisualization);
}

function EditModal_update(url) {
  var tid = $("div#modalEdit input#tid").val(); 

  var date = $("input#me_date").val();
  var name = $("input#me_name").val();
  var category_id = $("select#me_category").val();
  var amount = $("input#me_amount").val();
  var yearly = $("input#me_yearly").prop('checked');
  
  $.post(
    url,
    {
      'id': tid,
      'date': date,
      'name': name,
      'category_id': category_id,
      'amount': amount,
      'yearly': yearly,
    },
    function(data, status) {
      processTransactions(data);
      $('div#modalEdit').modal('hide');
    }
  );
}

function EditModal_split() {
  var amount = $("input#me_amount").val();
  var category_id = $("select#me_category").val();
  var tid = $("div#modalEdit input#tid").val(); 

  $("div#modalSplit h4.modal-title").text("Split Transaction " + tid);
  $("div#modalSplit input#tid").val(tid);
  $("div#modalSplit input#ms_total").val(amount);

  $("input#ms_date").val( $("input#me_date").val() );
  $("input#ms_date2").val( $("input#me_date").val() );
  $("input#ms_name").val( $("input#me_name").val() );
  $("select#ms_category").find("option").each(function(i, elem){
    if ($(elem).attr('value') == category_id) {
      $(elem).prop('selected', true);
    }
  });
  $("input#ms_amount").val( amount );
  $("input#ms_yearly").prop('checked', $("input#me_yearly").prop('checked'));

  $('div#modalEdit').modal('hide');
  $('div#modalSplit').modal('show');
} 

function splitModal_update(url) {
  var data = {
    'curr_id': $("div#modalSplit input#tid").val(),  
    'curr_date': $("input#ms_date").val(), 
    'curr_name': $("input#ms_name").val(), 
    'curr_category_id': $("select#ms_category").val(), 
    'curr_amount': $("input#ms_amount").val(),  
    'curr_yearly': $("input#ms_yearly").prop('checked'),  

    'new_date': $("input#ms_date2").val(), 
    'new_name': $("input#ms_name2").val(), 
    'new_category_id': $("select#ms_category2").val(), 
    'new_amount': $("input#ms_amount2").val(),  
    'new_yearly': $("input#ms_yearly2").prop('checked')
  };
  $.post(url, data, function(data, status) {
    processTransactions(data);
    $('div#modalSplit').modal('hide');
  });
} 

function splitModal_change() {
  var amount = parseFloat($("div#modalSplit input#ms_total").val().replace(/,/g, ''));
  var sib_amount = amount - parseFloat($(this).val());

  $(this).parent().siblings().find("input").val(sib_amount);
}

