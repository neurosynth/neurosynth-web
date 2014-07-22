var NSCookie, load_reverse_inference_image, textToHTML, urlToParams,
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

NSCookie = (function() {
  function NSCookie(contents) {
    this.contents = contents != null ? contents : null;
    if (this.contents == null) {
      this.contents = {
        locationTab: 0,
        featureTab: 0
      };
    }
    this.save();
  }

  NSCookie.prototype.save = function() {
    var json;
    json = JSON.stringify(this.contents);
    return $.cookie('neurosynth', json, {
      expires: 7,
      path: '/'
    });
  };

  NSCookie.prototype.set = function(key, val, save) {
    if (save == null) {
      save = true;
    }
    this.contents[key] = val;
    if (save) {
      return this.save();
    }
  };

  NSCookie.prototype.get = function(key) {
    return this.contents[key];
  };

  NSCookie.load = function() {
    if ($.cookie('neurosynth') == null) {
      return new NSCookie();
    } else {
      return new NSCookie(JSON.parse($.cookie('neurosynth')));
    }
  };

  return NSCookie;

})();


/* METHODS USED ON MORE THAN ONE PAGE */

urlToParams = function() {
  var search;
  search = window.location.search.substring(1);
  return JSON.parse("{\"" + decodeURI(search).replace(/"/g, "\"").replace(/&/g, "\",\"").replace(RegExp("=", "g"), "\":\"") + "\"}");
};

window.urlToParams = urlToParams;

load_reverse_inference_image = function(feature) {
  var imgs;
  imgs = [
    {
      'name': feature + ' (reverse inference)',
      'url': '/features/' + feature + '/images/reverseinference'
    }
  ];
  return viewer.loadImages(imgs, null, null, true);
};

$(document).ready(function() {
  window.cookie = NSCookie.load();
  if ($('#page-decode, #page-genes').length) {
    return $('#decoding_results_table').dataTable({
      paginationType: "full_numbers",
      displayLength: 10,
      processing: true,
      stateSave: true,
      orderClasses: false,
      order: [[2, 'desc']],
      columns: [
        {
          data: null,
          defaultContent: '<i class="fa fa-arrow-left"></i>',
          width: '20%'
        }, {
          data: "feature",
          render: function(data, type, row, meta) {
            return '<a href="/features/' + data + '">' + data + '</a>';
          },
          width: '%45%'
        }, {
          data: 'r',
          width: '35%'
        }
      ]
    });
  }
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
      'json': false,
      'name': 'anatomical',
      'colorPalette': 'grayscale',
      'cache': true,
      'url': '/images/anatomical'
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
  if (!$('.view').length) {
    return;
  }
  cache = settings.cache || true;
  viewer = new Viewer("#layer-list", ".layer-settings", cache, options);
  if ($('#view-axial').length) {
    viewer.addView("#view-axial", Viewer.AXIAL);
  }
  if ($('#view-coronal').length) {
    viewer.addView("#view-coronal", Viewer.CORONAL);
  }
  if ($('#view-sagittal').length) {
    viewer.addView("#view-sagittal", Viewer.SAGITTAL);
  }
  if (__indexOf.call(settings, 'nav') >= 0) {
    if ($('#view-sagittal').length) {
      viewer.addSlider("nav-xaxis", ".slider#nav-xaxis", "horizontal", 0, 1, 0.5, 0.01, Viewer.XAXIS);
    }
    if ($('#view-coronal').length) {
      viewer.addSlider("nav-yaxis", ".slider#nav-yaxis", "vertical", 0, 1, 0.5, 0.01, Viewer.YAXIS);
    }
    if ($('#view-axial').length) {
      viewer.addSlider("nav-zaxis", ".slider#nav-zaxis", "vertical", 0, 1, 0.5, 0.01, Viewer.ZAXIS);
    }
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

$(document).ready(function() {
  var iDelay, study, tbl, url, url_id;
  if (!$('#page-study').length) {
    return;
  }
  study = document.URL.split('/').slice(-2)[0];
  url = '/studies/' + study + '/tables';
  $.get(url, function(result) {
    return window.loadImages(result.data);
  });
  tbl = $('#studies_table').dataTable({
    paginationType: "full_numbers",
    displayLength: 10,
    processing: true,
    serverSide: true,
    ajaxSource: '/api/studies/',
    deferRender: true,
    stateSave: true,
    orderClasses: false
  });
  tbl.fnSetFilteringDelay(iDelay = 400);
  url_id = document.URL.split('/');
  url_id = url_id[url_id.length - 2];
  $('#study_features_table').dataTable({
    paginationType: "full_numbers",
    displayLength: 10,
    processing: true,
    ajaxSource: '/api/studies/features/' + url_id + '/',
    deferRender: true,
    stateSave: true,
    order: [[1, 'desc']],
    orderClasses: false
  });
  $('#study_peaks_table').dataTable({
    paginationType: "full_numbers",
    displayLength: 10,
    processing: true,
    ajaxSource: '/api/studies/peaks/' + url_id + '/',
    deferRender: true,
    stateSave: true,
    order: [[0, 'asc'], [2, 'asc']],
    orderClasses: false
  });
  return $('#study_peaks_table').on('click', 'tr', (function(_this) {
    return function(e) {
      var data, i, row;
      row = $(e.target).closest('tr')[0];
      data = $('#study_peaks_table').dataTable().fnGetData(row);
      data = (function() {
        var _i, _len, _ref, _results;
        _ref = data.slice(1);
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          i = _ref[_i];
          _results.push(parseInt(i));
        }
        return _results;
      })();
      return viewer.moveToAtlasCoords(data);
    };
  })(this));
});

$(document).ready(function() {
  var activeTab, feature, iDelay, loadFeatureImages, loadFeatureStudies, tbl;
  if (!$('#page-feature').length) {
    return;
  }
  feature = document.URL.split('/').slice(-2)[0];
  tbl = $('#features_table').dataTable({
    PaginationType: "full_numbers",
    displayLength: 10,
    processing: true,
    serverSide: true,
    ajaxSource: '/api/features',
    deferRender: true,
    stateSave: true,
    autoWidth: true,
    orderClasses: false
  });
  tbl.fnSetFilteringDelay(iDelay = 400);
  $('#feature_studies_table').dataTable({
    paginationType: "full_numbers",
    displayLength: 25,
    processing: true,
    deferRender: true,
    stateSave: true,
    orderClasses: false,
    columns: [
      {
        width: '40%'
      }, {
        width: '38%'
      }, {
        width: '15%'
      }, {
        width: '7%'
      }
    ]
  });
  loadFeatureStudies = function() {
    var url;
    url = '/features/' + feature + '/studies?dt=1';
    return $('#feature_studies_table').DataTable().ajax.url(url).load().order([3, 'desc']);
  };
  loadFeatureImages = function() {
    var url;
    url = '/features/' + feature + '/images';
    return $.get(url, function(result) {
      return loadImages(result.data);
    });
  };
  activeTab = window.cookie.get('featureTab');
  $("#feature-menu li:eq(" + activeTab + ") a").tab('show');
  if (feature != null) {
    loadFeatureStudies();
    loadFeatureImages();
  }
  return $('#feature-menu a').click(((function(_this) {
    return function(e) {
      e.preventDefault();
      activeTab = $('#feature-menu a').index($(e.target));
      window.cookie.set('featureTab', activeTab);
      $(e.target).tab('show');
      if (activeTab === 1) {
        return viewer.paint();
      }
    };
  })(this)));
});

$(document).ready(function() {
  var activeTab, getLocationString, loadLocationFeatures, loadLocationImages, loadLocationStudies, update;
  if (!$('#page-location').length) {
    return;
  }
  getLocationString = function() {
    var coords;
    coords = [$('#x-in').val(), $('#y-in').val(), $('#z-in').val(), $('#rad-out').val()];
    if (coords[3] > 20) {
      coords[3] = 20;
    }
    return coords.join('_');
  };
  loadLocationStudies = function() {
    var url;
    url = '/locations/' + getLocationString() + '/studies?dt=1';
    return $('#location_studies_table').DataTable().ajax.url(url).load().order([3, 'desc']);
  };
  loadLocationImages = function() {
    var url;
    url = '/locations/' + getLocationString() + '/images';
    return $.get(url, function(result) {
      return window.loadImages(result.data);
    });
  };
  loadLocationFeatures = function() {
    var url;
    url = '/locations/' + getLocationString() + '/features';
    return $('#location_features_table').DataTable().ajax.url(url).load().order([1, 'desc']);
  };
  update = function() {
    var base, coords;
    loadLocationStudies();
    loadLocationImages();
    loadLocationFeatures();
    base = window.location.href.split('?')[0];
    coords = {
      x: $('#x-in').val(),
      y: $('#y-in').val(),
      z: $('#z-in').val(),
      r: $('#rad-out').val()
    };
    return window.history.pushState(null, null, base + '?' + $.param(coords));
  };
  $('#location_studies_table').dataTable({
    paginationType: "full_numbers",
    displayLength: 25,
    processing: true,
    autoWidth: true,
    orderClasses: false
  });
  $('#location_features_table').dataTable({
    paginationType: "full_numbers",
    displayLength: 50,
    processing: true,
    autoWidth: true,
    orderClasses: false,
    columnDefs: [
      {
        targets: 0,
        render: function(data, type, row, meta) {
          return '<a href="/features/' + data + '">' + data + '</a>';
        }
      }
    ]
  });
  activeTab = window.cookie.get('locationTab');
  $("#location-menu li:eq(" + activeTab + ") a").tab('show');
  update();

  /* EVENTS */
  $('#radius-submit').click(((function(_this) {
    return function(e) {
      return update();
    };
  })(this)));
  $('#rad-in').change((function(_this) {
    return function(e) {
      return $('#rad-out').val($('#rad-in').val());
    };
  })(this));
  $('#rad-out').change((function(_this) {
    return function(e) {
      return $('#rad-in').val($('#rad-out').val());
    };
  })(this));
  $('#location-menu a').click(((function(_this) {
    return function(e) {
      e.preventDefault();
      activeTab = $('#location-menu a').index($(e.target));
      window.cookie.set('locationTab', activeTab);
      $(e.target).tab('show');
      if (activeTab === 2) {
        return viewer.paint();
      }
    };
  })(this)));
  return $('.plane-pos').keypress(function(e) {
    if (e.which === 13) {
      return update();
    }
  });
});

$(document).ready(function() {
  var image_id;
  if (!$('#page-decode').length) {
    return;
  }
  image_id = document.URL.split('/').slice(-2)[0];
  loadImages();
  $('#decoding_results_table').DataTable().ajax.url('/decode/' + image_id + '/data').load();
  return $('#decoding_results_table').on('click', 'i', (function(_this) {
    return function(e) {
      var feature, row;
      row = $(e.target).closest('tr');
      feature = $('td:eq(1)', row).text();
      load_reverse_inference_image(feature);
      return $('.scatterplot').html('<img src="/decode/' + image_id + '/scatter/' + feature + '.png">');
    };
  })(this));
});

$(document).ready(function() {
  var gene;
  if (!$('#page-genes').length) {
    return;
  }
  gene = document.URL.split('/').slice(-2)[0];
  loadImages();
  $('#decoding_results_table').DataTable().ajax.url('/genes/' + gene + '/decode').load();
  return $('#decoding_results_table').on('click', 'i', (function(_this) {
    return function(e) {
      var feature, row;
      row = $(e.target).closest('tr');
      feature = $('td:eq(1)', row).text();
      load_reverse_inference_image(feature);
      return $('.scatterplot').html('<img src="/genes/' + gene + '/scatter/' + feature + '.png" width="550">');
    };
  })(this));
});
