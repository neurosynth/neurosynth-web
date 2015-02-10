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

  SELECTED = 'info' # CSS class to apply to selected rows

  getSelection = ->
    selection = JSON.parse(window.localStorage.getItem('selection') or "{}")

  saveSelection = (selection) ->
    window.localStorage.setItem('selection', JSON.stringify(selection))

  getPMID = (tr) ->
    # Given tr DOM element parse the PMID
    # Assumes the first column has a link of the form ..../<pmid>
    href = $(tr).find('a').first().attr('href')
    return null if not href?
    return /(\d+)/.exec(href)[0]

  $('.selectable-table').on 'click', 'tr', ->
    pmid = getPMID(this)
    selection = getSelection()
    if pmid of selection
      delete selection[pmid]
    else
      selection[pmid] = 1
    saveSelection(selection)
    $(this).toggleClass(SELECTED)

  redrawTableSelection = ->
    selection = getSelection()
    $('tbody').find('tr').each ->
      pmid = getPMID(this)
      if pmid of selection
        $(this).addClass(SELECTED)
      else
        $(this).removeClass(SELECTED)

  $('.selectable-table').on 'draw.dt', ->
    redrawTableSelection()

  $('#select-all-btn').click ->
    selection = getSelection()
    $('tbody').find('tr').each ->
      pmid = getPMID(this)
      selection[pmid] = 1
    saveSelection(selection)
    redrawTableSelection()

  $('#deselect-all-btn').click ->
    selection = getSelection()
    $('tbody').find('tr').each ->
      pmid = getPMID(this)
      delete selection[pmid]
    saveSelection(selection)
    redrawTableSelection()

  # window.loadImages() if viewer?