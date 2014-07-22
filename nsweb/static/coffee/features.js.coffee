# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://jashkenas.github.com/coffee-script/
$(document).ready ->

  return if not $('#page-feature').length

  feature = document.URL.split('/').slice(-2)[0]

  tbl=$('#features_table').dataTable
    PaginationType: "full_numbers"
    displayLength: 10
    processing: true
    serverSide: true
    ajaxSource: '/api/features'
    deferRender: true
    stateSave: true
    autoWidth: true
    orderClasses: false
  tbl.fnSetFilteringDelay(iDelay=400)

  $('#feature_studies_table').dataTable
    paginationType: "full_numbers"
    displayLength: 25
    processing: true
    deferRender: true
    stateSave: true
    orderClasses: false
    columns: [
      { width: '40%' }
      { width: '38%' }
      { width: '15%' }
      { width: '7%' }
    ]


  loadFeatureStudies = () ->
    url = '/features/' + feature + '/studies?dt=1'
    $('#feature_studies_table').DataTable().ajax.url(url).load().order([3, 'desc'])

  loadFeatureImages = () ->
    url = '/features/' + feature  + '/images'
    $.get(url, (result) ->
      loadImages(result.data)
      )

  # Load state (e.g., which tab to display)
  activeTab = window.cookie.get('featureTab')
  $("#feature-menu li:eq(#{activeTab}) a").tab('show')

  if feature?
    loadFeatureStudies()
    loadFeatureImages()

  # Update cookie to reflect last tab user was on
  $('#feature-menu a').click ((e) =>
      e.preventDefault()
      activeTab = $('#feature-menu a').index($(e.target))
      window.cookie.set('featureTab', activeTab)
      $(e.target).tab('show')
      if activeTab == 1
          viewer.paint()
  )
