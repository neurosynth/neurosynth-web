$(document).ready ->
  # $('#decode_form').submit( (e) ->
  #   window.location.replace('/decode/' + $('#neurovault_id').val())
  #   e.preventDefault()
  # )

  if $('#page-decode-show').length or $('#page-genes-show').length

    controller = if $('#page-decode-show').length then 'decode' else 'genes'
    console.log(controller)

    loadImages()

    tbl = $('#decoding_results_table').DataTable()
    tbl.ajax.url('/' + controller + '/' + image_id + '/data').load()

    last_row_selected = null
    $('#decoding_results_table').on('click', 'button', (e) =>
      row = $(e.target).closest('tr')
      $(last_row_selected).children('td').removeClass('highlight-table-row')
      $(row).children('td').addClass('highlight-table-row')
      last_row_selected = row
      analysis = $('td:eq(1)', row).text()
      imgs = load_reverse_inference_image(analysis)
      viewer.loadImages(imgs)
      $(viewer).off('imagesLoaded')
      $(viewer).on('imagesLoaded', (e) ->
        viewer.deleteLayer(1)  if viewer.layerList.layers.length == 4
      )
      # Load scatterplot
      $('#loading-message').show()
      $('#scatterplot').html('<img src="/' + controller + '/' + image_id + '/scatter/' + analysis + '.png" width="500px" style="display:none;">')
      $('#scatterplot>img').load( ->
        $('#scatterplot>img').show()
        $('#loading-message').hide()
      )
    )

    $(viewer).on("afterLocationChange", (evt, data) ->
      if scatter?
        xv = viewer.getValue(1, data.ijk, space='image')
        yv = viewer.getValue(0, data.ijk, space='image')
        scatter.select(xv, yv)
      )

    $('#load-location').click((e) ->
        xyz = viewer.coords_xyz()
        window.location.href = '/locations?x=' + xyz[0] + '&y=' + xyz[1] + '&z=' + xyz[2]
    )

  else if $('#page-decode-index').length

    $('#neurovault-button').click( ->
      window.location.href = 'http://neurovault.org/images/add_for_neurosynth'
      )

  # $('#decode-tab-menu a:first').tab('show')

  # $(viewer).on('imagesLoaded', () -> scatter()) if scatterplot
