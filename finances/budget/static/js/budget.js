function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function sumTable(table) {
    var total = 0;
    $(table + " td.amount").each(function(){ 
        total += Number($(this).text().replace(/,/g, "")); 
    });
    return numberWithCommas(total);
}

function buildTables(data, budget_id) {
    var t = $("table#budget tbody")
    t.empty();
    for (i in data['rows']) {
        t.append(data['rows'][i]);

        $("table#budget tbody input[value='X']").off('click').on('click', function() {
            $.post("/rest/remove_item/" + budget_id, 
                { 'dbid': $(this).parent().parent().attr('dbid') },
                function(data, status) { buildTables(data); }
            );
        });

        $("table#budget tbody input[value='Edit']").off('click').on('click', function() {
            var dbid = $(this).parent().parent().attr('dbid'); 
            var category = $("tr[dbid="+dbid+"]").attr('category');
            var name = $("tr[dbid="+dbid+"] td:nth-child(1)").text();
            var monthly = $("tr[dbid="+dbid+"] td:nth-child(3)").text().replace(/,/g, '');
            var yearly = $("tr[dbid="+dbid+"] td:nth-child(4)").text().replace(/,/g, '');

            $.post("/rest/remove_item/" + budget_id, 
                { 'dbid': dbid },
                function(data, status) { 
                    buildTables(data); 

                    $("form input[name='category']").val(category);
                    $("form input[name='name']").val(name);
                    $("form input[name='monthly']").val(monthly);
                    $("form input[name='yearly']").val(yearly);
                    $("form input[type='text']:first").focus();
                }
            );
        });

        $("form input[type='text']").each(function(){ $(this).val(""); });
        $("form input[type='text']:first").focus();
    }
}


