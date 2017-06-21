
function addTransactionsToTable(transactions, table) {
  for (i=0; i<transactions.length; i++) {
    t = transactions[i];
    var row = $("<tr>").attr({record: JSON.stringify(t['record'])})
      .append( $("<td>").text(t['date']) )
      .append( $("<td>").text(t['name']) )
      .append( 
        $("<td>").append(
          addCategoryOptions(
            $("<select>").attr({name: 'category', class: 'form-control'}),
            t['category_id']
          )
        )
      )
      .append( $("<td>").text(t['amount']) )
      .append( 
        $("<td>").append(
          $("<input>").prop({type: 'checkbox', checked: t['yearly'] == '1'})
        )
      )
      .append( $("<td>").text(t['id']) ) ;

    table.append(row);
  }

  return table;
}

function createTable() {
  var table = $("<table>").prop({class: 'table table-striped'});
  var tr = $("<tr>");
  var headings = ['date', 'name', 'category', 'amount', 'yearly'];
  for (h=0; h<headings.length; h++) {
    tr.append( $("<th>").text(headings[h]) );
  }

  return table.append( $("thead").append(tr) )
    .append( $("tbody") )
  ;
}

function parseTransactions(data) {
  var dest = $("div#transactions");
  if (data['uncategorized'].length > 0) {
    var table = createTable().prop({id: 'uncategorized'});
    addTransactionsToTable(data['uncategorized'], table);
    dest.append(table);
  }

  if (data['uncategorized'].length > 0 && data['transactions'].length > 0) {
    dest.append("<p>&nbsp</p>");
    dest.append("<hr>");
    dest.append("<p>&nbsp</p>");
      //$("div").prop({class: 'col-xs-12'}).append($("<hr>"))
  }

  if (data['transactions'].length > 0) {
    var table = createTable().prop({id: 'output'});
    addTransactionsToTable(data['transactions'], table);
    dest.append(table);
  }
}
