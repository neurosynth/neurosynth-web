var loadFromBoxes, updateRadiusBox, updateRadiusSlider;

$(document).ready(function() {
  var iDelay, tbl, url_id;
  tbl = $('#studies_table').dataTable({
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": '/api/studies/',
    "bDeferRender": true,
    "bStateSave": true
  });
  tbl.fnSetFilteringDelay(iDelay = 400);
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
  var iDelay, tbl, url_id;
  tbl = $('#features_table').dataTable({
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": '/api/features',
    "bDeferRender": true,
    "bStateSave": true
  });
  tbl.fnSetFilteringDelay(iDelay = 400);
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

loadFromBoxes = function() {
  var coords;
  coords = [$('#x-in').val(), $('#y-in').val(), $('#z-in').val(), $('#rad-out').val()];
  return window.location = '/locations/' + coords.join('_') + '/';
};

updateRadiusBox = function() {
  return $('#rad-out').val($('#rad-in').val());
};

updateRadiusSlider = function() {
  return $('#rad-in').val($('#rad-out').val());
};

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
