$(document).ready(function() {
  var url_id;
  $('#studies_table').dataTable({
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": '/api/studies/',
    "bDeferRender": true,
    "bStateSave": true
  });
  url_id = document.URL.split('/');
  url_id = url_id[url_id.length - 2];
  $('#study_features_table').dataTable({
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "sAjaxSource": '/api/studies/features/' + url_id + '/',
    "bDeferRender": true,
    "bStateSave": true
  });
  return $('#study_peaks_table').dataTable({
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "sAjaxSource": '/api/studies/peaks/' + url_id + '/',
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

$(document).ready(function() {
  var url_id;
  url_id = document.URL.split('/');
  url_id = url_id[url_id.length - 2];
  return $('#location_studies_table').dataTable({
    sPaginationType: "full_numbers",
    iDisplayLength: 10,
    bProcessing: true,
    sAjaxSource: '/api/locations/' + url_id
  });
});
