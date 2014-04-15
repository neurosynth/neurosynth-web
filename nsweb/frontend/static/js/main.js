$(document).ready(function() {
  var url_id;
  $('#studies-datatable').dataTable({
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": '/api/studies',
    "bDeferRender": true,
    "bStateSave": true
  });
  url_id = document.URL.split('/');
  url_id.pop();
  return $('#study-features').dataTable({
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "sAjaxSource": '/api/studies/' + url_id.pop(),
    "bDeferRender": true,
    "bStateSave": true
  });
});

$(document).ready(function() {
  var url_id;
  $('#features_table').dataTable({
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
  return $('#feature_table').dataTable({
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "sAjaxSource": '/api/features/' + url_id.pop(),
    "bDeferRender": true,
    "bStateSave": true
  });
});
