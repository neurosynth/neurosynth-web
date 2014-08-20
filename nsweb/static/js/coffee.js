var NSCookie, Scatter, load_reverse_inference_image, make_scatterplot, runif, textToHTML, urlToParams,
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

load_reverse_inference_image = function(feature, fdr) {
  var url;
  if (fdr == null) {
    fdr = false;
  }
  url = '/features/' + feature + '/images/reverseinference';
  if (!fdr) {
    url += '?nofdr';
  }
  return [
    {
      name: feature + ' (reverse inference)',
      url: url,
      colorPalette: 'yellow',
      download: true
    }
  ];
};

$(document).ready(function() {
  var tbl;
  window.cookie = NSCookie.load();
  if ($('#page-decode-show, #page-genes').length) {
    return tbl = $('#decoding_results_table').dataTable({
      paginationType: "simple",
      displayLength: 10,
      processing: true,
      stateSave: false,
      orderClasses: false,
      autoWidth: false,
      order: [[2, 'desc']],
      columns: [
        {
          data: null,
          defaultContent: '<button type="button" class="btn btn-xs btn-primary" style="line-height: 1em;"><span class="glyphicon glyphicon-arrow-left"></span></button>',
          width: '20%'
        }, {
          data: "feature",
          render: function(data, type, row, meta) {
            return '<a href="/features/' + data + '">' + data + '</a>';
          },
          width: '%60%'
        }, {
          data: 'r',
          width: '20%'
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
      id: 'anatomical',
      json: false,
      name: 'anatomical',
      colorPalette: 'grayscale',
      cache: true,
      download: '/images/anatomical',
      url: '/images/anatomical'
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
  $(viewer).on('layerSelected', (function(_this) {
    return function(e, layer) {
      $('.intensity-label').text(layer.intent + ":");
      textToHTML('#image-description');
      return $('#description.data-row').toggle(!$('#image-description').is(':empty'));
    };
  })(this));
  $('.plane-pos').change(function(e) {
    var c, coords;
    coords = [$('#current-x').val(), $('#current-y').val(), $('#current-z').val()];
    return viewer.moveToAtlasCoords((function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = coords.length; _i < _len; _i++) {
        c = coords[_i];
        _results.push(parseInt(c));
      }
      return _results;
    })());
  });
  return $(viewer).on('afterLocationChange', function() {
    var coords;
    coords = viewer.coords_xyz();
    $('#current-x').val(coords[0]);
    $('#current-y').val(coords[1]);
    return $('#current-z').val(coords[2]);
  });
});

runif = function(min, max) {
  return Math.random() * (max - min) + min;
};

Array.prototype.min = function() {
  return this.reduce(function(p, v) {
    if (p < v) {
      return p;
    } else {
      return v;
    }
  });
};

Array.prototype.max = function() {
  return this.reduce(function(p, v) {
    if (p > v) {
      return p;
    } else {
      return v;
    }
  });
};

Scatter = (function() {
  function Scatter() {
    var canvas, center, i, img_mask, img_x, img_y, j, k, margin, nan_count, start, x, x_max, x_min, x_scale, xpos, xv, y, y_max, y_min, y_scale, _i, _j, _k, _l, _len, _m, _ref, _ref1, _ref2, _ref3;
    start = new Date().getTime();
    img_x = viewer.layerList.layers[1].image.data;
    img_y = viewer.layerList.layers[0].image.data;
    img_mask = viewer.layerList.layers[2].image.data;
    x = [];
    y = [];
    canvas = $('canvas#scatter-bg').get(0);
    this.context_bg = canvas.getContext('2d');
    _ref = [canvas.width, canvas.height], this.w = _ref[0], this.h = _ref[1];
    this.context_bg.clearRect(0, 0, this.w, this.h);
    this.context_fg = $('canvas#scatter-fg').get(0).getContext('2d');
    this.lastCenter = [0, 0];
    _ref1 = [0, 0, 0, 0], x_min = _ref1[0], x_max = _ref1[1], y_min = _ref1[2], y_max = _ref1[3];
    nan_count = 0;
    for (i = _i = 0; _i < 91; i = ++_i) {
      for (j = _j = 0; _j < 109; j = ++_j) {
        for (k = _k = 0; _k < 91; k = ++_k) {
          if (img_mask[i][j][k] !== 0) {
            x.push(img_x[i][j][k]);
            y.push(img_y[i][j][k]);
          }
        }
      }
    }
    console.log(x.length);
    console.log("loading the data took " + (new Date().getTime() - start));
    start = new Date().getTime();
    _ref2 = [x.min(), x.max(), y.min(), y.max()], this.x_min = _ref2[0], this.x_max = _ref2[1], this.y_min = _ref2[2], this.y_max = _ref2[3];
    margin = 0.05;
    this.x_min = this.x_min - margin * (this.x_max - this.x_min);
    this.x_max = this.x_max + margin * (this.x_max - this.x_min);
    this.y_min = this.y_min - margin * (this.y_max - this.y_min);
    this.y_max = this.y_max + margin * (this.y_max - this.y_min);
    this.x_range = this.x_max - this.x_min;
    this.y_range = this.y_max - this.y_min;
    x_scale = this.w / this.x_range;
    y_scale = this.h / this.y_range;
    console.log("computing ranges took " + (new Date().getTime() - start));
    this.context_bg.fillStyle = '#F0F0FD';
    this.context_bg.fillRect(0.1 * this.w, 0.05 * this.h, 0.85 * this.w, 0.85 * this.h);
    this.context_bg.strokeStyle = 'white';
    this.context_bg.lineWidth = 1;
    for (i = _l = 0; _l < 5; i = ++_l) {
      xpos = (0.1 + 0.17 * i) * this.w;
      this.context_bg.beginPath();
      this.context_bg.moveTo(xpos, 0.05 * this.h);
      this.context_bg.lineTo(xpos, 0.9 * this.h);
      console.log([xpos, 0.05 * this.h, 0.9 * this.h]);
      this.context_bg.stroke();
    }
    start = new Date().getTime();
    this.context_bg.fillStyle = '#3366FF';
    this.context_bg.globalAlpha = 0.05;
    for (i = _m = 0, _len = x.length; _m < _len; i = ++_m) {
      xv = x[i];
      center = this.getCenter(xv, y[i]);
      this.context_bg.beginPath();
      this.context_bg.arc(Math.round(center[0]), Math.round(center[1]), 1.5, 0, 2 * Math.PI);
      this.context_bg.fill();
    }
    console.log("painting the data took " + (new Date().getTime() - start));
    _ref3 = [x, y], this.x = _ref3[0], this.y = _ref3[1];
  }

  Scatter.prototype.getCenter = function(xv, yv) {
    return [(xv - this.x_min) / this.x_range * this.w, (1 - (yv - this.y_min) / this.y_range) * this.h];
  };

  Scatter.prototype.select = function(xv, yv) {
    var center;
    center = this.getCenter(xv, yv);
    this.context_fg.clearRect(this.lastCenter[0] - 10, this.lastCenter[1] - 10, 20, 20);
    this.context_fg.fillStyle = '#00FF66';
    this.context_fg.strokeStyle = 'black';
    this.context_fg.lineWidth = 1;
    this.context_fg.globalAlpha = 1.0;
    this.context_fg.beginPath();
    this.context_fg.arc(Math.round(center[0]), Math.round(center[1]), 6, 0, 2 * Math.PI);
    this.context_fg.fill();
    this.context_fg.stroke();
    return this.lastCenter = center;
  };

  return Scatter;

})();

make_scatterplot = function() {
  return window.scatter = new Scatter();
};

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
  }, $.get('/features/feature_names', function(result) {
    return $('#feature-search').autocomplete({
      minLength: 2,
      delay: 0,
      select: function(e, ui) {
        return window.location.href = '/features/' + ui.item.value;
      },
      source: function(request, response) {
        var filtered, matcher, re;
        re = $.ui.autocomplete.escapeRegex(request.term);
        matcher = new RegExp('^' + re, "i");
        filtered = $.grep(result.data, function(item, index) {
          return matcher.test(item);
        });
        return response(filtered.slice(0, 10));
      }
    });
  }));
  $('#feature-search').keyup(function(e) {
    var text;
    text = $('#feature-search').val();
    if (e.keyCode === 13) {
      return window.location.href = '/features/' + text;
    }
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
  $('#feature-menu a').click(((function(_this) {
    return function(e) {
      e.preventDefault();
      activeTab = $('#feature-menu a').index($(e.target));
      window.cookie.set('featureTab', activeTab);
      $(e.target).tab('show');
      if (activeTab === 0) {
        return viewer.paint();
      }
    };
  })(this)));
  return $('#load-location').click(function(e) {
    var xyz;
    xyz = viewer.coords_xyz();
    return window.location.href = '/locations?x=' + xyz[0] + '&y=' + xyz[1] + '&z=' + xyz[2];
  });
});

$(document).ready(function() {
  var activeTab, getLocationString, loadLocationFeatures, loadLocationImages, loadLocationStudies, moveTo, update;
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
    var base, coords, map_info, study_info, xyz;
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
    xyz = [coords.x, coords.y, coords.z];
    study_info = 'Studies reporting activation within ' + coords.r + ' mm of (' + xyz.join(', ') + ')';
    $('#current-location-studies').text(study_info);
    map_info = 'Functional connectivity and coactivation maps for (' + xyz.join(', ') + ')';
    return $('#current-location-maps').html(map_info);
  };
  moveTo = function() {
    var base, coords, url;
    base = window.location.href.split('?')[0];
    coords = {
      x: $('#x-in').val(),
      y: $('#y-in').val(),
      z: $('#z-in').val(),
      r: $('#rad-out').val()
    };
    url = base + '?' + $.param(coords);
    return window.location.href = url;
  };
  $('#location_studies_table').dataTable({
    paginationType: "full_numbers",
    displayLength: 10,
    processing: true,
    autoWidth: true
  });
  $('#location_features_table').dataTable({
    paginationType: "full_numbers",
    displayLength: 10,
    processing: true,
    autoWidth: true,
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
      if (activeTab === 0) {
        return viewer.paint();
      }
    };
  })(this)));
  $('.data-for-location').keypress(function(e) {
    if (e.which === 13) {
      return moveTo();
    }
  });
  return $('#load-location').click(function(e) {
    var xyz;
    xyz = viewer.coords_xyz();
    $('#x-in').val(xyz[0]);
    $('#y-in').val(xyz[1]);
    $('#z-in').val(xyz[2]);
    return moveTo();
  });
});

$(document).ready(function() {
  var last_row_selected, tbl;
  if ($('#page-decode-show').length) {
    loadImages();
    tbl = $('#decoding_results_table').DataTable();
    tbl.ajax.url('/decode/' + image_id + '/data').load();
    last_row_selected = null;
    $('#decoding_results_table').on('click', 'button', (function(_this) {
      return function(e) {
        var feature, imgs, row;
        row = $(e.target).closest('tr');
        $(last_row_selected).children('td').removeClass('highlight-table-row');
        $(row).children('td').addClass('highlight-table-row');
        last_row_selected = row;
        feature = $('td:eq(1)', row).text();
        imgs = load_reverse_inference_image(feature);
        viewer.loadImages(imgs);
        $(viewer).off('imagesLoaded');
        $(viewer).on('imagesLoaded', function(e) {
          if (viewer.layerList.layers.length === 4) {
            return viewer.deleteLayer(1);
          }
        });
        $('#loading-message').show();
        $('#scatterplot').html('<img src="/decode/' + image_id + '/scatter/' + feature + '.png" width="500px" style="display:none;">');
        return $('#scatterplot>img').load(function() {
          $('#scatterplot>img').show();
          return $('#loading-message').hide();
        });
      };
    })(this));
    $(viewer).on("afterLocationChange", function(evt, data) {
      var space, xv, yv;
      if (typeof scatter !== "undefined" && scatter !== null) {
        xv = viewer.getValue(1, data.ijk, space = 'image');
        yv = viewer.getValue(0, data.ijk, space = 'image');
        return scatter.select(xv, yv);
      }
    });
    return $('#load-location').click(function(e) {
      var xyz;
      xyz = viewer.coords_xyz();
      return window.location.href = '/locations?x=' + xyz[0] + '&y=' + xyz[1] + '&z=' + xyz[2];
    });
  } else if ($('#page-decode-index').length) {
    return $('#neurovault-button').click(function() {
      return window.location.href = 'http://neurovault.org/images/add_for_neurosynth';
    });
  }
});

$(document).ready(function() {
  var gene;
  if (!$('#page-genes').length) {
    return;
  }
  gene = document.URL.split('/').slice(-2)[0];
  loadImages();
  $('#decoding_results_table').DataTable().ajax.url('/genes/' + gene + '/decode').load();
  $('#decoding_results_table').on('click', 'i', (function(_this) {
    return function(e) {
      var feature, row;
      row = $(e.target).closest('tr');
      feature = $('td:eq(1)', row).text();
      load_reverse_inference_image(feature);
      return $('.scatterplot').html('<img src="/genes/' + gene + '/scatter/' + feature + '.png" width="550">');
    };
  })(this));
  $(viewer).on('afterClick', (function(_this) {
    return function(e) {
      var xyz;
      xyz = viewer.coords_xyz();
      $('#x-in').val(xyz[0]);
      $('#y-in').val(xyz[1]);
      return $('#z-in').val(xyz[2]);
    };
  })(this));
  $(viewer).trigger('afterClick');
  return $('.plane-pos').change((function(_this) {
    return function(e) {
      var coords, i;
      coords = [$('#x-in').val(), $('#y-in').val(), $('#z-in').val()];
      viewer.moveToAtlasCoords((function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = coords.length; _i < _len; _i++) {
          i = coords[_i];
          _results.push(parseInt(i));
        }
        return _results;
      })());
      return $(viewer).trigger('afterClick');
    };
  })(this));
});

$(document).ready(function() {
  var url;
  if (!$('#page-home').length) {
    return;
  }
  url = '/features/' + feature + '/images';
  return $.get(url, function(result) {
    return loadImages(result.data.slice(1, 2));
  });
});
