# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://jashkenas.github.com/coffee-script/
$(document).ready ->
  tbl = $('#studies-datatable').dataTable
    # "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
    "sPaginationType": "full_numbers"
    "iDisplayLength": 10
    "bProcessing": true
    "bServerSide": true
    "sAjaxSource": '/api/studies'
    "bDeferRender": true
    "bStateSave": true

    #aoColumns: [ { sWidth: '45%'}, { sWidth: '25%' }, { sWidth: '15%'}, null, null]

    # tbl.fnSetFilteringDelay(500)

  #$('#study-tab-content a').click (e) ->
  #  #e.preventDefault()
  #  $(this).tab('show')
  #  return

  #$('#study-peaks').dataTable()
  #return

    # $('#study-peaks').on('click', 'tr', (e) =>
        # row = $(e.target).closest('tr')[0]
        # data = $('#study-peaks').dataTable().fnGetData(row)
        # data = (parseInt(i) for i in data)
        # # viewer.moveToAtlasCoords(data)
    # )

    # $('#study-menu a:first').tab('show')