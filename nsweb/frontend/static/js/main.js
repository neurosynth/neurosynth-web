$(document).ready(function() {
  var tbl;
  tbl = $('table[class*=studies-datatable]').dataTable({
    "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
    "sPaginationType": "full_numbers",
    "iDisplayLength": 10,
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": '/api/studies',
    "bDeferRender": true,
    "bStateSave": true,
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
  $('#study-peaks').on('click', 'tr', (function(_this) {
    return function(e) {
      var data, i, row;
      row = $(e.target).closest('tr')[0];
      data = $('#study-peaks').dataTable().fnGetData(row);
      return data = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = data.length; _i < _len; _i++) {
          i = data[_i];
          _results.push(parseInt(i));
        }
        return _results;
      })();
    };
  })(this));
  return $('#study-menu a:first').tab('show');
});
