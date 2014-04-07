$(document).ready(function() {
  var tbl;
  tbl = $('table[class*=studies-datatable]').dataTable({
    "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": '/api/studies',
    "bDeferRender": true,
    "bStateSave": true,
    aoColumns: [
      {
        sWidth: '45%'
      }, {
        sWidth: '25%'
      }, {
        sWidth: '15%'
      }, null, null
    ]
  });
  $('#study-peaks a').click(function(e) {
    e.preventDefault();
    $(this).tab('show');
  });
  return $(document).ready(function() {
    $('#study-peaks').dataTable();
  });
});

$(document).ready(function() {
  $('#feature-content-menu a').click(function(e) {});
  e.preventDefault();
  $(this).tab('show');
});

$(document).ready(function() {
  $('#features_table').dataTable();
});
