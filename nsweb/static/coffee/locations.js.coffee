
# # Get the current cursor position and load the corresponding URL
# loadLocationFromCursor = (coords) ->
    # [x, y, z] = coords
    # $('#x-pos').val(x)
    # $('#y-pos').val(y)
    # $('#z-pos').val(z)
    # loadLocationFromTextBoxes()


$(document).ready ->

  return if not $('#page-location').length

  getLocationString = ->
    coords = [$('#x-in').val(), $('#y-in').val(), $('#z-in').val(), $('#rad-out').val()]
    coords[3] = 20 if coords[3] > 20
    coords.join('_')

  loadLocationStudies = ->
    url = '/api/locations/' + getLocationString() + '/studies?dt=1'
    $('#location_studies_table').DataTable().ajax.url(url).load().order([3, 'desc'])

  loadLocationImages = ->
    url = '/api/locations/' + getLocationString()  + '/images'
    $.get(url, (result) ->
      window.loadImages(result.data)
      loadLocationSimilarity(result.data[0].id)
      )

  loadLocationComparisons = ->
    url = '/api/locations/' + getLocationString() + '/compare'
    $('#location_analyses_table').DataTable().ajax.url(url).load().order([1, 'desc'])

  loadLocationSimilarity = (id) ->
    url = '/api/images/' + id + '/decode'
    $('#analysis-similarity-table').DataTable().ajax.url(url).load().order([1, 'desc'])
    #TODO: IMPLEMENT MOVE CURSOR TO SEED

  update = ->
    loadLocationStudies()
    loadLocationImages()
    loadLocationComparisons()
    base = window.location.href.split('?')[0]
    coords = { x: $('#x-in').val(), y: $('#y-in').val(), z: $('#z-in').val(), r: $('#rad-out').val()}
    xyz = [coords.x, coords.y, coords.z]
    study_info = 'Studies reporting activation within ' + coords.r + ' mm of (' + xyz.join(', ') + ')'
    $('#current-location-studies').text(study_info)
    
    # TODO: IMPLEMENT ONPOPSTATE  
    # window.history.pushState(null, null, base + '?' + $.param(coords))

  moveTo = ->
    base = window.location.href.split('?')[0]
    coords = [$('#x-in').val(), $('#y-in').val(), $('#z-in').val(), $('#rad-out').val()]
    url = '/locations/' + coords.join('_')
    window.location.href = url
  
  createDataTable('#location_studies_table', {
      pageLength: 10
      columns: [
        { width: '40%' }
        { width: '38%' }
        { width: '15%' }
        { width: '7%' }
      ]})

  createDataTable('#location_analyses_table', {
    pageLength: 10
    autoWidth: false
    columns: [
      {
        width: '28%'
        render: (data, type, row, meta) ->
          '<a href="/analyses/terms/'+ data + '">' + data + '</a>'
      }
      { width: '18%' }
      { width: '18%' }
      { width: '18%' }
      { width: '18%' }
    ]})

  # Load state (e.g., which tab to display)
  activeTab = window.cookie.get('locationTab')
  $("#location-menu li:eq(#{activeTab}) a").tab('show')

  update()

  ### EVENTS ###
  $('#radius-submit').click ((e) =>
    update()
  )

  $('#rad-in').change((e) =>
    $('#rad-out').val($('#rad-in').val())
  )

  $('#rad-out').change((e) =>
    $('#rad-in').val($('#rad-out').val())
  )

  # Update cookie to reflect last tab user was on
  $('#location-menu a').click ((e) =>
      e.preventDefault()
      activeTab = $('#location-menu a').index($(e.target))
      window.cookie.set('locationTab', activeTab)
      $(e.target).tab('show')
      if activeTab == 0
          viewer.paint()
  )

  $('.data-for-location').keypress((e) ->
      moveTo() if(e.which == 13)
  )

  $('#load-location').click((e) ->
      xyz = viewer.coords_xyz()
      $('#x-in').val(xyz[0])
      $('#y-in').val(xyz[1])
      $('#z-in').val(xyz[2])
      moveTo()
  )

