var NSCookie, loadLocationFromCursor, loadLocationFromTextBoxes, textToHTML,
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

$(document).ready(function() {
  $('#decode_form').submit(function(e) {
    window.location.replace('/decode/' + $('#neurovault_id').val());
    return e.preventDefault();
  });
  $('table[class*=decode-datatable]').dataTable({
    "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
    "sPaginationType": "bootstrap",
    "iDisplayLength": 10,
    'aaSorting': [[1, 'desc']]
  });
  return $('#decode-tab-menu a:first').tab('show');
});

$(document).ready(function() {
  jQuery.fn.dataTableExt.oPagination.iFullNumbersShowPages = 3;
  $('#explore-tab-menu a:first').tab('show');
  $('#decode_form').submit(function(e) {
    window.location.replace('/decode/' + $('#neurovault_id').val());
    return e.preventDefault();
  });
  return $('#load-url-image').click(function(e) {
    var bits, name, url;
    url = $('#image_url').val();
    if (url.match(/nii(\.gz)*$/)) {
      bits = url.split('/');
      name = bits[bits.length - 1];
      return viewer.loadImages([
        {
          name: name,
          url: url,
          download: false
        }
      ]);
    } else {
      return alert("Error: remote files must be Nifti images with a .nii or .nii.gz extension.");
    }
  });
});

$(document).ready(function() {
  var activeTab;
  $('#feature_letter_table').hide();
  $('.feature_letter').click(function(e) {
    var id;
    e.preventDefault();
    $('#feature_letter_table').show();
    id = $(this).attr('id');
    return $('#feature_letter_table').dataTable({
      'bProcessing': true,
      'sAjaxSource': "/ajax_get_features_by_letter/" + id,
      'bDestroy': true,
      "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
      "sPaginationType": "bootstrap",
      "iDisplayLength": 25
    });
  });
  $('#feature_image_select').change(function(e) {
    var id, img, label;
    label = $(this).children("option:selected").text();
    id = $(this).val();
    img = [
      {
        name: label,
        id: id,
        download: "/images/" + id + "/download"
      }
    ];
    return window.loadImages(img);
  });
  $('#name.search-features').bind('railsAutocomplete.select', function(e, data) {
    return $(this).parents('form')[0].submit();
  });
  $('#feature-content-menu a').click(((function(_this) {
    return function(e) {
      var activeTab;
      e.preventDefault();
      activeTab = $('#feature-content-menu a').index($(e.target));
      window.cookie.set('featureTab', activeTab);
      $(e.target).tab('show');
      if (activeTab === 0) {
        return viewer.paint();
      }
    };
  })(this)));
  $('#load-location').click(function(e) {
    var coords;
    coords = viewer.coords_xyz();
    return window.location = '/locations/' + coords.join('_');
  });
  activeTab = window.cookie.get('featureTab');
  return $("#feature-content-menu li:eq(" + activeTab + ") a").tab('show');
});

$(document).ready(function() {
  var tbl;
  tbl = $('table[class*=images-datatable]').dataTable({
    "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
    "sPaginationType": "bootstrap",
    "iDisplayLength": 10,
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": '/images',
    aoColumns: [
      {
        bSearchable: false,
        bVisible: false
      }, {
        sWidth: '60%'
      }, {
        bSortable: false,
        sWidth: '35%'
      }, {
        sWidth: '5%',
        bSortable: false
      }
    ],
    aoColumnDefs: [
      {
        sClass: 'add-image',
        aTargets: [2]
      }
    ]
  });
  tbl.fnSetFilteringDelay(500);
  return tbl.on('click', 'td:nth-child(3)', (function(_this) {
    return function(e) {
      var cell, color, data, id, name, row, src;
      cell = $(e.target).closest('td')[0];
      row = tbl.fnGetPosition(cell)[0];
      data = tbl.fnGetData(row);
      id = data[0];
      name = data[1];
      color = viewer.layerList.getNextColor();
      if ($(e.target).attr('src').match(/^\/assets\/add/)) {
        loadImages([
          {
            id: id,
            name: name,
            colorPalette: color,
            download: "/images/" + id + "/download"
          }
        ], false);
        src = 'remove';
      } else {
        viewer.deleteLayer(name);
        src = 'add';
      }
      return $(e.target).attr('src', '/assets/' + src + '.png');
    };
  })(this));
});

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

$(document).ready(function() {
  $('table[class*=default-datatable]').dataTable({
    "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
    "sPaginationType": "bootstrap",
    "iDisplayLength": 10
  });
  $('table[class*=small-datatable]').dataTable({
    "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span12'i><'span12'p>>",
    "sPaginationType": "bootstrap",
    "iDisplayLength": 10
  });
  return window.cookie = NSCookie.load();
});

loadLocationFromTextBoxes = function() {
  var coords;
  coords = [$('#x-pos').val(), $('#y-pos').val(), $('#z-pos').val()];
  return window.location = '/locations/' + coords.join('_');
};

loadLocationFromCursor = function(coords) {
  var x, y, z;
  x = coords[0], y = coords[1], z = coords[2];
  $('#x-pos').val(x);
  $('#y-pos').val(y);
  $('#z-pos').val(z);
  return loadLocationFromTextBoxes();
};

$(document).ready(function() {
  var activeTab, i, imgs, locationViewer, seed;
  seed = (function() {
    var _i, _len, _ref, _results;
    _ref = xyz.split('_');
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      i = _ref[_i];
      _results.push(parseInt(i));
    }
    return _results;
  })();
  if ($('.loc-viewer').length) {
    locationViewer = new Viewer("#dummy", ".dummy", true, {
      panzoomEnabled: false
    });
    locationViewer.addView("#loc-view-axial", Viewer.AXIAL);
    locationViewer.addView("#loc-view-coronal", Viewer.CORONAL);
    locationViewer.addView("#loc-view-sagittal", Viewer.SAGITTAL);
    locationViewer.addSlider("nav-xaxis", ".slider#loc-nav-xaxis", "horizontal", 0, 1, 0.5, 0.01, Viewer.XAXIS);
    locationViewer.addSlider("nav-yaxis", ".slider#loc-nav-yaxis", "vertical", 0, 1, 0.5, 0.01, Viewer.YAXIS);
    locationViewer.addSlider("nav-zaxis", ".slider#loc-nav-zaxis", "vertical", 0, 1, 0.5, 0.01, Viewer.ZAXIS);
    locationViewer.clearImages();
    imgs = {
      id: 'anatomical',
      json: true,
      name: 'anatomical',
      colorPalette: 'grayscale',
      cache: true,
      url: '/images/anatomical/data'
    };
    locationViewer.loadImages(imgs, null, true, true);
    locationViewer.moveToAtlasCoords(seed);
    $(locationViewer).on('afterClick', (function(_this) {
      return function(e) {
        return loadLocationFromCursor(locationViewer.coords_xyz());
      };
    })(this));
  }
  $('#location-menu a').click(((function(_this) {
    return function(e) {
      var activeTab;
      e.preventDefault();
      activeTab = $('#location-menu a').index($(e.target));
      window.cookie.set('locationTab', activeTab);
      $(e.target).tab('show');
      if (activeTab === 2) {
        return viewer.paint();
      }
    };
  })(this)));
  $('.plane-pos').keypress(function(e) {
    if (e.which === 13) {
      return loadLocationFromTextBoxes();
    }
  });
  $('#load-location').click(function(e) {
    return loadLocationFromCursor(viewer.coords_xyz());
  });
  $('#location-features-datatable').dataTable({
    sDom: "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
    sPaginationType: "bootstrap",
    iDisplayLength: 10,
    bProcessing: true,
    aaSorting: [[1, 'desc']],
    sAjaxSource: '/locations/' + xyz + '/features',
    fnRowCallback: function(nRow, aData, iDisplayIndex) {
      var $cell, feature, val;
      $cell = $('td:eq(0)', nRow);
      feature = $cell.text();
      val = '<a href="/features/' + feature + '">' + feature + '</a>';
      $cell.html(val);
      return nRow;
    }
  });
  activeTab = window.cookie.get('locationTab');
  return $("#location-menu li:eq(" + activeTab + ") a").tab('show');
});

$(document).ready(function() {
  var tbl;
  tbl = $('table[class*=studies-datatable]').dataTable({
    "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
    "iDisplayLength": 10,
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": '/api/studies',
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
      img.url = '/images/' + img.id + '/download';
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
