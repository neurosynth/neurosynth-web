# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://jashkenas.github.com/coffee-script/
$(document).ready ->
  return if not $('.selectable-table').length

  # Load the table layers
  if study?
    url = '/studies/' + study  + '/tables'
    $.get(url, (result) -> window.loadImages(result.data))

  createDataTable('#studies_table', { ajax: '/api/studies/', serverSide: true })

  url_id=document.URL.split('/')
  url_id=url_id[url_id.length-2]

  createDataTable('#study_analyses_table', {
    pageLength: 10
    ajax: '/api/studies/analyses/'+url_id+'/'
    order: [[1, 'desc']]
      })

  createDataTable('#study_peaks_table', {
    pageLength: 10
    ajax: '/api/studies/peaks/'+url_id+'/'
    order: [[0, 'asc'], [2, 'asc']]
      })


  $('#study_peaks_table').on('click', 'tr', (e) =>
    row = $(e.target).closest('tr')[0]
    data = $('#study_peaks_table').dataTable().fnGetData(row)
    data = (parseInt(i) for i in data[1..])
    viewer.moveToAtlasCoords(data)
  )



  # window.loadImages() if viewer?