# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://jashkenas.github.com/coffee-script/
$(document).ready ->

  tbl = $('table[class*=images-datatable]').dataTable
      "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
      "sPaginationType": "bootstrap"
      "iDisplayLength": 10
      "bProcessing": true
      "bServerSide": true
      "sAjaxSource": '/images'
      aoColumns: [
        { bSearchable: false, bVisible: false },
        { sWidth: '60%'}, { bSortable: false, sWidth: '35%'}, { sWidth: '5%', bSortable: false}],
      aoColumnDefs: [
        { sClass: 'add-image', aTargets: [2] }
      ]
  tbl.fnSetFilteringDelay(500)
  tbl.on('click', 'td:nth-child(3)', (e) =>
    cell = $(e.target).closest('td')[0] # Make sure we have the TD element
    row = tbl.fnGetPosition(cell)[0]
    data = tbl.fnGetData(row)
    id = data[0]
    name = data[1]
    color = viewer.layerList.getNextColor()
    if $(e.target).attr('src').match(/^\/assets\/add/)
        loadImages([{
          id: id
          name: name
          colorPalette: color
          download: "/images/#{id}/"
        }], false)
        src = 'remove'
    else
        viewer.deleteLayer(name)
        src = 'add'
    $(e.target).attr('src', '/assets/' + src + '.png')
  )

  # $('#image-library').dialog(({
  #     autoOpen: false
  #     height: 500
  #     width: 700
  #     modal: false
  #     buttons: [{
  #       text: 'Done'
  #       click: -> $(this).dialog('close')
  #       'class': 'btn btn-primary'
  #     }]
  #   }))

  # $('#load-images').click(() ->
  #   $('#image-library').dialog('open')
  # )