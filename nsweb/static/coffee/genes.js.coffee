
$(document).ready ->

  return if not $('#page-genes').length

  # Load the table layers
  gene = document.URL.split('/').slice(-2)[0]
  loadImages()

  $('#decoding_results_table').DataTable().ajax.url('/genes/' + gene + '/decode').load()

  $('#decoding_results_table').on('click', 'i', (e) =>
    row = $(e.target).closest('tr')
    feature = $('td:eq(1)', row).text()
    load_reverse_inference_image(feature)
    # Load scatterplot
    $('.scatterplot').html('<img src="/genes/' + gene + '/scatter/' + feature + '.png" width="550">')
  )

  $(viewer).on('afterClick', (e) =>
    xyz = viewer.coords_xyz()
    $('#x-in').val(xyz[0])
    $('#y-in').val(xyz[1])
    $('#z-in').val(xyz[2])
  )

  $(viewer).trigger('afterClick')

  # $('.plane-pos').keypress((e) ->
  #     update() if(e.which == 13)
  # )

  $('.plane-pos').change( (e) =>
    coords = [$('#x-in').val(), $('#y-in').val(), $('#z-in').val()]
    viewer.moveToAtlasCoords(parseInt(i) for i in coords)
    $(viewer).trigger('afterClick')  # To get values rounded to nearest voxel with data
  )