var loadFromBoxes, textToHTML, updateRadiusBox, updateRadiusSlider,
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

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
  }, $('#study_peaks_table').on('click', 'tr', (function(_this) {
    return function(e) {
      var data, i, row;
      row = $(e.target).closest('tr')[0];
      data = $('#study_peaks_table').dataTable().fnGetData(row);
      data = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = data.length; _i < _len; _i++) {
          i = data[_i];
          _results.push(parseInt(i));
        }
        return _results;
      })();
      return viewer.moveToAtlasCoords(data);
    };
  })(this)));
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
  $('#feature_table').dataTable({
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "sAjaxSource": '/api/features/' + url_id.pop(),
    "bDeferRender": true,
    "bStateSave": true
  });
  $('#feature-content-menu').click(function(e) {
    return e.preventDefault();
  });
  $(this).tab('show');
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
    sAjaxSource: '/api/locations/' + url_id + '/?sEcho=1'
  });
});

window.loadImages = function(imgs, clear) {
  var img, _i, _len;
  if (imgs == null) {
    imgs = null;
  }
  if (clear == null) {
    clear = true;
  }
  if (imgs == null) {
    imgs = images;
  }
  if (clear) {
    window.viewer.clearImages();
    imgs.unshift({
      'id': 'anatomical',
      'json': true,
      'name': 'anatomical',
      'colorPalette': 'grayscale',
      'cache': true,
      'url': '/images/anatomical/data'
    });
  }
  for (_i = 0, _len = imgs.length; _i < _len; _i++) {
    img = imgs[_i];
    if ((img.id != null) && (img.url == null)) {
      img.url = '/images/' + img.id + '/';
    }
  }
  return viewer.loadImages(imgs);
};

textToHTML = function(el) {
  return $(el).html($(el).text());
};

$(document).ready(function() {
  var cache, viewer;
  cache = settings.cache || true;
  viewer = new Viewer("#layer-list", ".layer-settings", cache, options);
  viewer.addView("#view-axial", Viewer.AXIAL);
  viewer.addView("#view-coronal", Viewer.CORONAL);
  viewer.addView("#view-sagittal", Viewer.SAGITTAL);
  if (__indexOf.call(settings, 'nav') >= 0) {
    viewer.addSlider("nav-xaxis", ".slider#nav-xaxis", "horizontal", 0, 1, 0.5, 0.01, Viewer.XAXIS);
    viewer.addSlider("nav-yaxis", ".slider#nav-yaxis", "vertical", 0, 1, 0.5, 0.01, Viewer.YAXIS);
    viewer.addSlider("nav-zaxis", ".slider#nav-zaxis", "vertical", 0, 1, 0.5, 0.01, Viewer.ZAXIS);
  }
  if (__indexOf.call(settings, 'layers') >= 0) {
    viewer.addSlider("opacity", ".slider#opacity", "horizontal", 0, 1, 1, 0.01, null, '#opacity-text');
    viewer.addSlider("pos-threshold", ".slider#pos-threshold", "horizontal", 0, 1, 0, 0.01, null, '#pos-threshold-text');
    viewer.addSlider("neg-threshold", ".slider#neg-threshold", "horizontal", -1, 0, 0, 0.01, null, '#neg-threshold-text');
    viewer.addColorSelect("#select-color");
    viewer.addSignSelect("#select-sign");
    viewer.addTextField("image-intent", "#image-intent");
    viewer.addTextField("description", "#image-description");
    viewer.addDataField("voxelValue", "#data-current-value");
    viewer.addDataField("currentCoords", "#data-current-coords");
  }
  if (__indexOf.call(settings, 'checkboxes') >= 0) {
    viewer.addSettingsCheckboxes('#checkbox-list', 'standard');
  }
  window.viewer = viewer;
  loadImages();
  $(viewer).on('imagesLoaded', (function(_this) {
    return function(e) {
      return textToHTML('#image-description');
    };
  })(this));
  return $(viewer).on('layerSelected', (function(_this) {
    return function(e) {
      textToHTML('#image-description');
      return $('#description.data-row').toggle(!$('#image-description').is(':empty'));
    };
  })(this));
});
