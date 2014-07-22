# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://jashkenas.github.com/coffee-script/
$(document).ready ->

  return if not $('#page-study').length

  # Load the table layers
  study = document.URL.split('/').slice(-2)[0]
  url = '/studies/' + study  + '/tables'
  $.get(url, (result) -> window.loadImages(result.data))

  tbl=$('#studies_table').dataTable
    # "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
    paginationType: "full_numbers"
    displayLength: 10
    processing: true
    serverSide: true
    ajaxSource: '/api/studies/'
    deferRender: true
    stateSave: true
    orderClasses: false
  tbl.fnSetFilteringDelay(iDelay=400)

  url_id=document.URL.split('/')
  url_id=url_id[url_id.length-2]
  
  $('#study_features_table').dataTable
    paginationType: "full_numbers"
    displayLength: 10
    processing: true
    ajaxSource: '/api/studies/features/'+url_id+'/'
    deferRender: true
    stateSave: true
    order: [[1, 'desc']]
    orderClasses: false

  $('#study_peaks_table').dataTable
    paginationType: "full_numbers"
    displayLength: 10
    processing: true
    ajaxSource: '/api/studies/peaks/'+url_id+'/'
    deferRender: true
    stateSave: true
    order: [[0, 'asc'], [2, 'asc']]
    orderClasses: false

  $('#study_peaks_table').on('click', 'tr', (e) =>
    row = $(e.target).closest('tr')[0]
    data = $('#study_peaks_table').dataTable().fnGetData(row)
    data = (parseInt(i) for i in data[1..])
    viewer.moveToAtlasCoords(data)
  )

  # window.loadImages() if viewer?