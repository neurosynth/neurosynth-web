# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://jashkenas.github.com/coffee-script/
$(document).ready ->
  # $('#decode_form').submit( (e) ->
  #   window.location.replace('/decode/' + $('#neurovault_id').val())
  #   e.preventDefault()
  # )

  return if not $('#page-decode').length

  image_id = document.URL.split('/').slice(-2)[0]

  loadImages()

  $('#decoding_results_table').DataTable().ajax.url('/decode/' + image_id + '/data').load()

  $('#decoding_results_table').on('click', 'i', (e) =>
    row = $(e.target).closest('tr')
    feature = $('td:eq(1)', row).text()
    load_reverse_inference_image(feature)
    # Load scatterplot
    $('.scatterplot').html('<img src="/decode/' + image_id + '/scatter/' + feature + '.png" width="500">')
  )

  # $('#decode-tab-menu a:first').tab('show')