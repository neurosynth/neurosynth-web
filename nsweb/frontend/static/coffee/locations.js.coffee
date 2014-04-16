# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://jashkenas.github.com/coffee-script/

# Grabs the current locations from the x/y/z fields and loads the corresponding URL
loadFromBoxes = () ->
  coords = [$('#x-in').val(), $('#y-in').val(), $('#z-in').val(), $('#rad-out').val()]
  window.location = '/locations/' + coords.join('_')+'/'

updateRadiusBox = () ->
  $('#rad-out').val($('#rad-in').val())

updateRadiusSlider = () ->
  $('#rad-in').val($('#rad-out').val())

#
# # Get the current cursor position and load the corresponding URL
# loadLocationFromCursor = (coords) ->
    # [x, y, z] = coords
    # $('#x-pos').val(x)
    # $('#y-pos').val(y)
    # $('#z-pos').val(z)
    # loadLocationFromTextBoxes()


$(document).ready ->
  url_id=document.URL.split('/')
  url_id=url_id[url_id.length-2]
  $('#location_studies_table').dataTable({
    #sDom: "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>"
    sPaginationType: "full_numbers"
    iDisplayLength: 10
    bProcessing: true
    #aaSorting: [[1, 'desc']]
    sAjaxSource: '/api/locations/'+url_id
    # fnRowCallback: (nRow, aData, iDisplayIndex) ->
                        # $cell=$('td:eq(0)', nRow)
                        # feature = $cell.text()
                        # val = '<a href="/features/' + feature + '">' + feature + '</a>'
                        # $cell.html(val)
                        # nRow
    # 'aoColumns': [ { sWidth: '45%'}, { sWidth: '25%' }, { sWidth: '15%'}]
  })
    # Handle location viewer separately because we already have a viewer on the page.
    # Eventually the code should be refactored to gracefully handle multiple viewers
    # by storing handles and calling as needed.

    # seed = (parseInt(i) for i in xyz.split('_'))
#
    # if $('.loc-viewer').length
        # locationViewer = new Viewer("#dummy", ".dummy", true, {panzoomEnabled: false})
        # locationViewer.addView "#loc-view-axial", Viewer.AXIAL
        # locationViewer.addView "#loc-view-coronal", Viewer.CORONAL
        # locationViewer.addView "#loc-view-sagittal", Viewer.SAGITTAL
        # locationViewer.addSlider "nav-xaxis", ".slider#loc-nav-xaxis", "horizontal",  0, 1, 0.5, 0.01, Viewer.XAXIS
        # locationViewer.addSlider "nav-yaxis", ".slider#loc-nav-yaxis", "vertical", 0, 1, 0.5, 0.01, Viewer.YAXIS
        # locationViewer.addSlider "nav-zaxis", ".slider#loc-nav-zaxis", "vertical", 0, 1, 0.5, 0.01, Viewer.ZAXIS
        # locationViewer.clearImages()
        # imgs = {
            # id: 'anatomical'
            # json: true
            # name: 'anatomical'
            # colorPalette: 'grayscale'
            # cache: true
            # url: '/images/anatomical/data'
        # }
        # locationViewer.loadImages(imgs, null, true, true)
        # locationViewer.moveToAtlasCoords(seed)
#
        # $(locationViewer).on('afterClick', (e) =>
            # loadLocationFromCursor(locationViewer.coords_xyz())
        # )
#
    # $('#location-menu a').click ((e) =>
        # e.preventDefault()
        # activeTab = $('#location-menu a').index($(e.target))
        # window.cookie.set('locationTab', activeTab)
        # $(e.target).tab('show')
        # if activeTab == 2
            # viewer.paint()
    # )
#
    # $('.plane-pos').keypress((e) ->
        # loadLocationFromTextBoxes() if(e.which == 13)
    # )
#
    # $('#load-location').click((e) ->
        # loadLocationFromCursor(viewer.coords_xyz())
    # )


  # Load state (e.g., which tab to display)
  # activeTab = window.cookie.get('locationTab')
  # $("#location-menu li:eq(#{activeTab}) a").tab('show')
  # $(viewer).on('imagesLoaded', ((e) ->
  #     # Start from seed voxel.
  #     # viewer.paint()
  #     viewer.moveToAtlasCoords(seed)
  # ))

