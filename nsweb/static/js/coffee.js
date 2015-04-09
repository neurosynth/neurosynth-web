var ActiveAnalysis, AllStudiestable, AnalysisList, AnalysisListItem, NSCookie, SELECTED, Scatter, SelectedStudiesTable, a, app, arrayToObject, br, button, ce, createDataTable, div, form, getFromLocalStorage, getPMID, getSelectedStudies, h1, h2, h4, h5, hr, input, label, li, loadReverseInferenceImage, make_scatterplot, p, redrawTableSelection, runif, saveSelection, saveToLocalStorage, setupSelectableTable, span, table, td, textToHTML, textarea, th, thead, tr, ul, urlToParams, _ref,
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

NSCookie = (function() {
  function NSCookie(contents) {
    this.contents = contents != null ? contents : null;
    if (this.contents == null) {
      this.contents = {
        locationTab: 0,
        analysisTab: 0
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


/* DATATABLES-RELATED CODE */

$.fn.dataTable.TableTools.defaults.aButtons = [
  {
    sExtends: 'copy',
    sButtonText: 'Copy',
    oSelectorOpts: {
      filter: 'applied'
    }
  }, {
    sExtends: 'csv',
    sButtonText: 'CSV',
    oSelectorOpts: {
      filter: 'applied'
    }
  }, {
    sExtends: 'xls',
    sButtonText: 'XLS',
    oSelectorOpts: {
      filter: 'applied'
    }
  }
];

$.fn.dataTableExt.sErrMode = 'throw';

createDataTable = function(element, options) {
  var iDelay, tbl, _opts;
  _opts = {
    pagingType: "full_numbers",
    pageLength: 25,
    stateSave: true,
    orderClasses: true,
    processing: true,
    dom: 'T<"clear">lfrtip',
    tableTools: {
      sSwfPath: "/static/swf/copy_csv_xls.swf"
    },
    filterDelay: true
  };
  $.extend(_opts, options);
  tbl = $(element).dataTable(_opts);
  if (_opts.filterDelay) {
    tbl.fnSetFilteringDelay(iDelay = 400);
  }
  return tbl;
};


/* METHODS USED ON MORE THAN ONE PAGE */

urlToParams = function() {
  var search;
  search = window.location.search.substring(1);
  return JSON.parse("{\"" + decodeURI(search).replace(/"/g, "\"").replace(/&/g, "\",\"").replace(RegExp("=", "g"), "\":\"") + "\"}");
};

window.urlToParams = urlToParams;

loadReverseInferenceImage = function(analysis, fdr) {
  var url;
  if (fdr == null) {
    fdr = false;
  }
  url = '/analyses/' + analysis + '/images/reverse';
  if (!fdr) {
    url += '?unthresholded';
  }
  return [
    {
      name: analysis + ' (reverse inference)',
      url: url,
      colorPalette: 'yellow',
      download: true
    }
  ];
};

$(document).ready(function() {
  window.cookie = NSCookie.load();
  if ($('#page-decode-show, #page-genes-show').length) {
    return createDataTable('#decoding_results_table', {
      pagingType: "simple",
      pageLength: 10,
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
          data: "analysis",
          render: function(data, type, row, meta) {
            return '<a href="/analyses/terms/' + data + '">' + data + '</a>';
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
  var url, url_id;
  if (!$('.selectable-table').length) {
    return;
  }
  if (typeof study !== "undefined" && study !== null) {
    url = '/studies/' + study + '/tables';
    $.get(url, function(result) {
      return window.loadImages(result.data);
    });
  }
  createDataTable('#studies_table', {
    ajax: '/api/studies/',
    serverSide: true
  });
  url_id = document.URL.split('/');
  url_id = url_id[url_id.length - 2];
  createDataTable('#study_analyses_table', {
    pageLength: 10,
    ajax: '/api/studies/analyses/' + url_id + '/',
    order: [[1, 'desc']]
  });
  createDataTable('#study_peaks_table', {
    pageLength: 10,
    ajax: '/api/studies/peaks/' + url_id + '/',
    order: [[0, 'asc'], [2, 'asc']]
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
  var activeTab, columns, loadAnalysisImages, loadAnalysisStudies;
  if (!$('#page-analysis').length) {
    return;
  }
  createDataTable('#term-analyses-table', {
    ajax: '/api/terms',
    serverSide: true
  });
  createDataTable('#topic-set-list-table', {
    ajax: '/api/topics',
    serverSide: true
  });
  columns = [
    {
      width: '40%'
    }, {
      width: '38%'
    }, {
      width: '15%'
    }, {
      width: '7%'
    }
  ];
  createDataTable('#analysis-studies-table', {
    columns: columns
  });
  createDataTable('#analysis-similarity-table');
  if (typeof topic_set !== "undefined" && topic_set !== null) {
    createDataTable('#topic-set-table', {
      ajax: '/api/topics/' + topic_set
    });
  }
  $.get('/analyses/term_names', function(result) {
    return $('#term-analysis-search').autocomplete({
      minLength: 2,
      delay: 0,
      select: function(e, ui) {
        return window.location.href = '/analyses/terms/' + ui.item.value;
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
  });
  $('#term-analysis-search').keyup(function(e) {
    var text;
    text = $('#term-analysis-search').val();
    if (e.keyCode === 13) {
      return window.location.href = '/analyses/terms/' + text;
    }
  });
  loadAnalysisStudies = function() {
    var url;
    url = '/analyses/' + analysis + '/studies?dt=1';
    return $('#analysis-studies-table').DataTable().ajax.url(url).load().order([3, 'desc']);
  };
  loadAnalysisImages = function() {
    var url;
    url = '/analyses/' + analysis + '/images';
    return $.get(url, function(result) {
      return loadImages(result.data);
    });
  };
  activeTab = window.cookie.get('analysisTab');
  $("#analysis-menu li:eq(" + activeTab + ") a").tab('show');
  if (typeof analysis !== "undefined" && analysis !== null) {
    loadAnalysisStudies();
    loadAnalysisImages();
  }
  $('#analysis-menu a').click(((function(_this) {
    return function(e) {
      e.preventDefault();
      activeTab = $('#analysis-menu a').index($(e.target));
      window.cookie.set('analysisTab', activeTab);
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
  var activeTab, getLocationString, loadLocationComparisons, loadLocationImages, loadLocationSimilarity, loadLocationStudies, moveTo, update;
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
      window.loadImages(result.data);
      return loadLocationSimilarity(result.data[0].id);
    });
  };
  loadLocationComparisons = function() {
    var url;
    url = '/locations/' + getLocationString() + '/compare';
    return $('#location_analyses_table').DataTable().ajax.url(url).load().order([1, 'desc']);
  };
  loadLocationSimilarity = function(id) {
    var url;
    url = '/images/' + id + '/decode';
    return $('#analysis-similarity-table').DataTable().ajax.url(url).load().order([1, 'desc']);
  };
  update = function() {
    var base, coords, study_info, xyz;
    loadLocationStudies();
    loadLocationImages();
    loadLocationComparisons();
    base = window.location.href.split('?')[0];
    coords = {
      x: $('#x-in').val(),
      y: $('#y-in').val(),
      z: $('#z-in').val(),
      r: $('#rad-out').val()
    };
    xyz = [coords.x, coords.y, coords.z];
    study_info = 'Studies reporting activation within ' + coords.r + ' mm of (' + xyz.join(', ') + ')';
    return $('#current-location-studies').text(study_info);
  };
  moveTo = function() {
    var base, coords, url;
    base = window.location.href.split('?')[0];
    coords = [$('#x-in').val(), $('#y-in').val(), $('#z-in').val(), $('#rad-out').val()];
    url = '/locations/' + coords.join('_');
    return window.location.href = url;
  };
  createDataTable('#location_studies_table', {
    pageLength: 10,
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
  createDataTable('#location_analyses_table', {
    pageLength: 10,
    autoWidth: false,
    columns: [
      {
        width: '28%',
        render: function(data, type, row, meta) {
          return '<a href="/analyses/terms/' + data + '">' + data + '</a>';
        }
      }, {
        width: '18%'
      }, {
        width: '18%'
      }, {
        width: '18%'
      }, {
        width: '18%'
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
  if ($('#page-decode-show').length || $('#page-genes-show').length) {
    loadImages();
    tbl = $('#decoding_results_table').DataTable();
    tbl.ajax.url('/decode/' + image_id + '/data').load();
    last_row_selected = null;
    $('#decoding_results_table').on('click', 'button', (function(_this) {
      return function(e) {
        var analysis, imgs, row;
        row = $(e.target).closest('tr');
        $(last_row_selected).children('td').removeClass('highlight-table-row');
        $(row).children('td').addClass('highlight-table-row');
        last_row_selected = row;
        analysis = $('td:eq(1)', row).text();
        imgs = loadReverseInferenceImage(analysis);
        viewer.loadImages(imgs);
        $(viewer).off('imagesLoaded');
        $(viewer).on('imagesLoaded', function(e) {
          if (viewer.layerList.layers.length === 4) {
            return viewer.deleteLayer(1);
          }
        });
        $('#loading-message').show();
        $('#scatterplot').html('<img src="/decode/' + image_id + '/scatter/' + analysis + '.png" width="500px" style="display:none;">');
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
  var url;
  if (!$('#page-home').length) {
    return;
  }
  url = '/analyses/' + analysis + '/images';
  return $.get(url, function(result) {
    return loadImages(result.data.slice(1, 2));
  });
});

_ref = React.DOM, div = _ref.div, br = _ref.br, ul = _ref.ul, li = _ref.li, a = _ref.a, p = _ref.p, h1 = _ref.h1, h2 = _ref.h2, h4 = _ref.h4, h5 = _ref.h5, span = _ref.span, form = _ref.form, input = _ref.input, button = _ref.button, hr = _ref.hr, table = _ref.table, thead = _ref.thead, tr = _ref.tr, th = _ref.th, td = _ref.td, label = _ref.label, textarea = _ref.textarea;

ce = React.createElement;

SELECTED = 'info';

saveSelection = function(selection) {
  return window.localStorage.setItem('ns-selection', JSON.stringify(selection));
};

saveToLocalStorage = function(key, value) {
  return window.localStorage.setItem(key, JSON.stringify(value));
};

getFromLocalStorage = function(key) {
  var val;
  val = window.localStorage.getItem(key);
  if (val === null) {
    return val;
  } else {
    return JSON.parse(val);
  }
};

getSelectedStudies = function() {
  var selection;
  return selection = JSON.parse(window.localStorage.getItem('ns-selection') || "{}");
};

getPMID = function(tr) {
  var href;
  href = $(tr).find('a').first().attr('href');
  if (href == null) {
    return null;
  }
  return parseInt(/(\d+)/.exec(href)[0]);
};

arrayToObject = function(array) {
  var item, obj, _i, _len;
  obj = {};
  for (_i = 0, _len = array.length; _i < _len; _i++) {
    item = array[_i];
    obj[item] = 1;
  }
  return obj;
};

app = {
  props: {
    fetchAllAnalysesURL: '/api/custom/all/',
    fetchAllStudiesURL: '/api/studies/all/',
    saveURL: '/api/custom/save/',
    deleteURL: '/api/custom/',
    studiesTableURL: '/api/analyses/',
    getFullAnalysisURL: '/api/analyses/full/'
  },
  state: {
    analyses: [],
    allStudies: [],
    activeAnalysis: {
      blank: true,
      studies: {}
    }
  },
  setActiveAnalysis: function(uuid) {
    if (!(this.state.activeAnalysis.saved || this.state.activeAnalysis.blank)) {
      if (!confirm("You have unsaved changes that will be discarded. Are you sure you want to proceeed?")) {
        return;
      }
    }
    this.state.activeAnalysis = $.extend({}, this.state.analyses.filter(function(a) {
      return a.uuid === uuid;
    })[0]);
    this.state.activeAnalysis.studies = arrayToObject(this.state.activeAnalysis.studies);
    this.state.activeAnalysis.saved = true;
    this.syncToLocalStorage();
    return this.render();
  },
  activeStudies: function() {
    return Object.keys(this.state.activeAnalysis.studies).map((function(_this) {
      return function(pmid) {
        return _this.state.studyDetails[pmid];
      };
    })(this));
  },
  syncToLocalStorage: function() {
    return window.localStorage.setItem('ns-active-analysis', JSON.stringify(this.state.activeAnalysis));
  },
  update: function() {
    this.state.activeAnalysis.saved = false;
    this.state.activeAnalysis.blank = false;
    this.syncToLocalStorage();
    return this.render();
  },
  removeStudy: function(pmid) {
    delete this.state.activeAnalysis.studies[pmid];
    return this.update();
  },
  removeStudies: function(pmids) {
    var pmid, _i, _len;
    for (_i = 0, _len = pmids.length; _i < _len; _i++) {
      pmid = pmids[_i];
      delete this.state.activeAnalysis.studies[pmid];
    }
    return this.update();
  },
  addStudy: function(pmid) {
    this.state.activeAnalysis.studies[pmid] = 1;
    return this.update();
  },
  addStudies: function(pmids) {
    var pmid, _i, _len;
    for (_i = 0, _len = pmids.length; _i < _len; _i++) {
      pmid = pmids[_i];
      this.state.activeAnalysis.studies[pmid] = 1;
    }
    return this.update();
  },
  addAllStudies: function() {
    var study, _i, _len, _ref1;
    _ref1 = this.state.allStudies;
    for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
      study = _ref1[_i];
      this.state.activeAnalysis.studies[study.pmid] = 1;
    }
    return this.update();
  },
  removeAllStudies: function() {
    this.state.activeAnalysis.studies = {};
    return this.update();
  },
  cloneActiveAnalysis: function() {
    this.state.activeAnalysis.uuid = null;
    this.state.activeAnalysis.id = null;
    this.state.activeAnalysis.saved = false;
    this.syncToLocalStorage();
    return this.render();
  },
  clearActiveAnalysis: function() {
    this.state.activeAnalysis = {
      blank: true,
      studies: {}
    };
    this.syncToLocalStorage();
    return this.render();
  },
  setActiveAnalysisName: function(name) {
    this.state.activeAnalysis.name = name;
    this.state.activeAnalysis.saved = false;
    return this.render();
  },
  setActiveAnalysisDescription: function(description) {
    this.state.activeAnalysis.description = description;
    this.state.activeAnalysis.saved = false;
    return this.render();
  },
  deleteAnalysis: function(uuid) {
    if (!confirm("Are you sure you want to delete this analysis? ")) {
      return;
    }
    return $.ajax({
      dataType: 'json',
      type: 'DELETE',
      url: this.props.deleteURL + uuid.toString() + '/',
      success: (function(_this) {
        return function(response) {
          _this.state.activeAnalysis = {
            blank: true,
            studies: {}
          };
          _this.syncToLocalStorage();
          return _this.fetchAllAnalyses();
        };
      })(this)
    });
  },
  saveActiveAnalysis: function(name, description) {
    var data;
    this.state.activeAnalysis.name = name;
    data = {
      studies: Object.keys(this.state.activeAnalysis.studies),
      name: name,
      description: description,
      uuid: this.state.activeAnalysis.uuid
    };
    return $.ajax({
      dataType: 'json',
      type: 'POST',
      data: {
        data: JSON.stringify(data)
      },
      url: this.props.saveURL,
      success: (function(_this) {
        return function(data) {
          _this.state.activeAnalysis.uuid = data.uuid;
          _this.state.activeAnalysis.id = data.id;
          _this.state.activeAnalysis.saved = true;
          _this.syncToLocalStorage();
          return _this.fetchAllAnalyses();
        };
      })(this)
    });
  },
  fetchAllAnalyses: function() {
    return $.ajax({
      dataType: 'json',
      type: 'GET',
      url: this.props.fetchAllAnalysesURL,
      success: (function(_this) {
        return function(data) {
          _this.state.analyses = data.analyses;
          return _this.render();
        };
      })(this),
      error: (function(_this) {
        return function(xhr, status, err) {
          return console.error(_this.props.url, status, err.toString());
        };
      })(this)
    });
  },
  fetchAllStudies: function() {
    return $.ajax({
      dataType: 'json',
      type: 'GET',
      url: this.props.fetchAllStudiesURL,
      success: (function(_this) {
        return function(data) {
          var study, _i, _len, _ref1;
          _this.state.allStudies = data.studies;
          _this.state.studyDetails = {};
          _ref1 = data.studies;
          for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
            study = _ref1[_i];
            _this.state.studyDetails[study.pmid] = study;
          }
          return _this.fetchAllAnalyses();
        };
      })(this),
      error: (function(_this) {
        return function(xhr, status, err) {
          return console.error(_this.props.url, status, err.toString());
        };
      })(this)
    });
  },
  init: function() {
    var active;
    active = getFromLocalStorage('ns-active-analysis');
    if (active) {
      this.state.activeAnalysis = active;
    }
    return this.fetchAllStudies();
  },
  render: function() {
    if (document.getElementById('custom-list-container') == null) {
      return;
    }
    React.render(React.createElement(AnalysisList, {
      analyses: this.state.analyses,
      selected_uuid: this.state.activeAnalysis.uuid
    }), document.getElementById('custom-list-container'));
    return React.render(React.createElement(ActiveAnalysis, {
      analysis: this.state.activeAnalysis
    }), document.getElementById('active-analysis-container'));
  }
};

AnalysisListItem = React.createClass({
  loadHandler: function() {
    return app.setActiveAnalysis(this.props.uuid);
  },
  render: function() {
    return div({
      className: "row bs-callout panel " + (this.props.selected ? 'bs-callout-info' : '')
    }, div({
      className: "col-md-10"
    }, ul({
      className: 'list-unstyled'
    }, li({}, "Name: " + this.props.name), li({}, "uuid: " + this.props.uuid), li({}, "Number of studies: " + this.props.numStudies))), div({
      className: "col-md-2"
    }, button({
      className: "btn btn-primary btn-sm " + (this.props.selected ? 'disabled' : ''),
      onClick: this.loadHandler
    }, 'Load')));
  }
});

AnalysisList = React.createClass({
  render: function() {
    return div({
      className: 'custom-analysis-list panel'
    }, h4({}, "Your saved custom analyses (" + this.props.analyses.length + ")"), hr({}, ''), this.props.analyses.map((function(_this) {
      return function(analysis) {
        var selected;
        selected = _this.props.selected_uuid === analysis.uuid ? true : false;
        return React.createElement(AnalysisListItem, {
          key: analysis.uuid,
          uuid: analysis.uuid,
          name: analysis.name,
          numStudies: analysis.studies.length,
          selected: selected
        });
      };
    })(this)));
  }
});

ActiveAnalysis = React.createClass({
  save: function() {
    return app.saveActiveAnalysis(this.refs.name.getDOMNode().value, this.refs.description.getDOMNode().value);
  },
  deleteHandler: function() {
    return app.deleteAnalysis(this.props.analysis.uuid);
  },
  cloneHandler: function() {
    return app.cloneActiveAnalysis();
  },
  discardHandler: function() {
    return app.clearActiveAnalysis();
  },
  nameChangeHandler: function() {
    return app.setActiveAnalysisName(this.refs.name.getDOMNode().value);
  },
  descriptionChangeHandler: function() {
    return app.setActiveAnalysisDescription(this.refs.description.getDOMNode().value);
  },
  render: function() {
    var header, saved, studies, uuid;
    if (this.props.analysis.blank) {
      return div({}, 'No active analysis currently loaded');
    }
    uuid = this.props.analysis.uuid;
    studies = Object.keys(this.props.analysis.studies);
    saved = this.props.analysis.saved;
    if (uuid) {
      header = div({}, div({
        className: 'row'
      }, div({
        className: 'col-md-4'
      }, label({}, 'Analysis name:', input({
        type: 'text',
        className: 'form-control',
        ref: 'name',
        value: this.props.analysis.name,
        onChange: this.nameChangeHandler
      })), p({}, "uuid: " + uuid)), div({
        className: 'col-md-8'
      }, p({}, "" + studies.length + " studies in this analysis. "), button({
        className: "btn " + (saved ? '' : 'btn-primary') + " btn-sm",
        disabled: "" + (saved ? 'disabled' : ''),
        onClick: this.save
      }, 'Save Analysis'), span({}, ' '), button({
        className: 'btn btn-primary btn-sm'
      }, 'Run Analysis'), span({}, ' '), button({
        className: 'btn btn-info btn-sm',
        onClick: this.cloneHandler
      }, 'Clone Analysis'), span({}, ' '), button({
        className: 'btn btn-danger btn-sm',
        onClick: this.deleteHandler
      }, 'Delete Analysis'))), div({
        className: 'row'
      }, div({
        className: 'col-md-12'
      }, label({}, 'Description:', textarea({
        className: 'form-control',
        ref: 'description',
        placeholder: 'Enter a description for this analysis',
        value: this.props.analysis.description,
        onChange: this.descriptionChangeHandler
      })), hr({}, ''))));
    } else {
      header = div({}, div({
        className: 'row'
      }, div({
        className: 'col-md-4'
      }, input({
        type: 'text',
        className: 'form-control',
        placeholder: 'Enter a name for this analysis',
        ref: 'name'
      }), br({}, ''), button({
        className: 'btn btn-primary',
        disabled: "" + (saved ? 'disabled' : ''),
        onClick: this.save
      }, 'Save selection as new custom analysis'), span({}, ' '), button({
        className: 'btn btn-danger',
        onClick: this.discardHandler
      }, 'Discard current selection')), div({
        className: 'col-md-8'
      }, p({}, "" + studies.length + " studies selected"))), div({
        className: 'row'
      }, div({
        className: 'col-md-12'
      }, label({}, 'Description:', textarea({
        className: 'form-control',
        ref: 'description',
        placeholder: 'Enter a description for this analysis'
      })), h4({}, Description), p({}, this.props.analysis.description), hr({}, ''))));
    }
    return div({}, header, div({
      className: 'row'
    }, div({
      className: 'col-md-12'
    }, div({
      role: 'tabpanel'
    }, ul({
      className: 'nav nav-tabs',
      role: 'tablist'
    }, li({
      role: 'presentation',
      className: 'active'
    }, a({
      href: '#selected-studies-tab',
      role: 'tab',
      'data-toggle': 'tab'
    }, "Selected Studies (" + studies.length + ")")), li({
      role: 'presentation'
    }, a({
      href: '#all-studies-tab',
      role: 'tab',
      'data-toggle': 'tab'
    }, "All studies (" + app.state.allStudies.length + ")"))), div({
      className: 'tab-content'
    }, div({
      className: 'tab-pane active',
      role: 'tab-panel',
      id: 'selected-studies-tab'
    }, React.createElement(SelectedStudiesTable, {})), div({
      className: 'tab-pane',
      role: 'tab-panel',
      id: 'all-studies-tab'
    }, br({}, p({}, "Add or remove studies to your analysis by clicking on the study. Studies that are already added are highlighted in blue.")), React.createElement(AllStudiestable)))))));
  }
});

SelectedStudiesTable = React.createClass({
  tableData: function() {
    return app.activeStudies().map(function(item) {
      return $.extend({
        'remove': '<button class="btn btn-sm">remove</button>'
      }, item);
    });
  },
  setupRemoveButton: function() {
    return $('#selected-studies-table').find('tr').on('click', 'button', function() {
      var pmid;
      pmid = getPMID($(this).closest('tr'));
      return app.removeStudy(pmid);
    });
  },
  componentDidMount: function() {
    $('#selected-studies-table').DataTable({
      data: this.tableData(),
      columns: [
        {
          data: 'title'
        }, {
          data: 'authors'
        }, {
          data: 'journal'
        }, {
          data: 'year'
        }, {
          data: 'pmid'
        }, {
          data: 'remove'
        }
      ]
    });
    return this.setupRemoveButton();
  },
  componentDidUpdate: function() {
    var t;
    t = $('#selected-studies-table').DataTable();
    t.clear();
    t.rows.add(this.tableData());
    t.draw();
    return this.setupRemoveButton();
  },
  render: function() {
    return table({
      className: 'table table-hover',
      id: 'selected-studies-table'
    }, thead({}, tr({}, th({}, 'Title '), th({}, 'Authors'), th({}, 'Journal'), th({}, 'Year'), th({}, 'PMID'), th({}, 'Action'))));
  }
});

AllStudiestable = React.createClass({
  componentDidMount: function() {
    $('#all-studies-table').DataTable({
      data: app.state.allStudies,
      columns: [
        {
          data: 'title'
        }, {
          data: 'authors'
        }, {
          data: 'journal'
        }, {
          data: 'year'
        }, {
          data: 'pmid'
        }
      ]
    });
    return setupSelectableTable();
  },
  componentDidUpdate: function() {
    return redrawTableSelection();
  },
  addAllHandler: function() {
    return app.addAllStudies();
  },
  removeAllHandler: function() {
    return app.removeAllStudies();
  },
  filteredPMIDs: function() {
    var filteredrows;
    filteredrows = $("#all-studies-table").dataTable()._('tr', {
      "filter": "applied"
    });
    return filteredrows.map(function(item) {
      return item.pmid;
    });
  },
  addAllFilteredHandler: function() {
    return app.addStudies(this.filteredPMIDs());
  },
  removeAllFilteredHandler: function() {
    return app.removeStudies(this.filteredPMIDs());
  },
  render: function() {
    return div({}, button({
      className: 'btn btn-sm',
      onClick: this.addAllHandler
    }, "Add all studies"), span({}, ' '), button({
      className: 'btn btn-sm',
      onClick: this.removeAllHandler
    }, "Remove all studies"), span({}, ' '), button({
      className: 'btn btn-sm',
      onClick: this.addAllFilteredHandler
    }, "Add all filtered studies"), span({}, ' '), button({
      className: 'btn btn-sm',
      onClick: this.removeAllFilteredHandler
    }, "Remove all filtered studies"), br({}, ''), br({}, ''), table({
      className: 'table selectable-table',
      id: 'all-studies-table'
    }, thead({}, tr({}, th({}, 'Title '), th({}, 'Authors'), th({}, 'Journal'), th({}, 'Year'), th({}, 'PMID')))));
  }
});

redrawTableSelection = function() {
  return $('.selectable-table').find('tbody').find('tr').each(function() {
    var pmid;
    pmid = getPMID(this);
    if (pmid in app.state.activeAnalysis.studies) {
      return $(this).addClass(SELECTED);
    } else {
      return $(this).removeClass(SELECTED);
    }
  });
};

setupSelectableTable = function() {
  $('.selectable-table').on('click', 'tr', function() {
    var pmid;
    pmid = getPMID(this);
    if (pmid == null) {
      return;
    }
    if (pmid in app.state.activeAnalysis.studies) {
      app.removeStudy(pmid);
    } else {
      app.addStudy(pmid);
    }
    return redrawTableSelection();
  });
  $('.selectable-table').on('draw.dt', function() {
    return redrawTableSelection();
  });
  $('#select-all-btn').click(function() {
    var selection;
    selection = getSelectedStudies();
    $('tbody').find('tr').each(function() {
      var pmid;
      pmid = getPMID(this);
      return selection[pmid] = 1;
    });
    saveSelection(selection);
    return redrawTableSelection();
  });
  $('#deselect-all-btn').click(function() {
    var selection;
    selection = getSelectedStudies();
    $('tbody').find('tr').each(function() {
      var pmid;
      pmid = getPMID(this);
      return delete selection[pmid];
    });
    saveSelection(selection);
    return redrawTableSelection();
  });
  return redrawTableSelection();
};

$(document).ready(function() {
  setupSelectableTable();
  app.init();
  if (document.getElementById('custom-list-container') != null) {
    return window.onbeforeunload = function(e) {
      var message;
      if (app.state.activeAnalysis.saved || app.state.activeAnalysis.blank) {
        return;
      }
      e = e || window.event;
      message = 'You have unsaved changes.';
      if (e) {
        e.returnValue = message;
      }
      return message;
    };
  }
});
