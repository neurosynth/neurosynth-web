$(document).ready(function() {
  var tbl;
  tbl = $('table[class*=studies-datatable]').dataTable({
    "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
    "iDisplayLength": 10,
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": '/api/studies?datatables',
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
  return tbl.fnSetFilteringDelay(500);
});
