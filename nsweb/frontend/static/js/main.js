$(document).ready(function() {
  var tbl;
  return tbl = $('#studies-datatable').dataTable({
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": '/api/studies',
    "bDeferRender": true,
    "bStateSave": true
  });
});

$(document).ready(function() {
  var tbl, url_id;
  tbl = $('#features_table').dataTable({
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": '/api/features',
    "bDeferRender": true,
    "bStateSave": true
  });
  url_id = document.URL.split('/');
  url_id.pop();
  return tbl = $('#feature_table').dataTable({
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "sAjaxSource": '/api/features/' + url_id.pop(),
    "bDeferRender": true,
    "bStateSave": true
  });
});
