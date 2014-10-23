
$(document).ready ->

  return if not $('#page-feature').length

  feature = document.URL.split('/').slice(-2)[0]

  tbl=$('#features_table').dataTable
    PaginationType: "full_numbers"
    displayLength: 10
    processing: true
    serverSide: true
    ajax: '/api/features'
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

    # autocomplete
    $.get('/features/feature_names', (result) ->

      $('#feature-search').autocomplete( 
        minLength: 2
        delay: 0
        select: (e, ui) -> 
          window.location.href = '/features/' + ui.item.value
        # only match words that start with string, and limit to 10
        source: (request, response) ->
          re = $.ui.autocomplete.escapeRegex(request.term)
          matcher = new RegExp('^' + re, "i" )
          filtered = $.grep(result.data, (item, index) ->
            return matcher.test(item)
          )
          response(filtered.slice(0, 10))
      )
    )
    
  $('#feature-search').keyup((e) ->
    text = $('#feature-search').val()
    window.location.href = ('/features/' + text) if (e.keyCode == 13)
  )

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
      if activeTab == 0
          viewer.paint()
  )

  $('#load-location').click((e) ->
      xyz = viewer.coords_xyz()
      window.location.href = '/locations?x=' + xyz[0] + '&y=' + xyz[1] + '&z=' + xyz[2]
  )
