
$(document).ready ->

  return if not $('#page-genes-list').length

  # Initialize DataTables
  createDataTable('#gene-list-table', {ajax: '/api/genes/dt', serverSide: true})
  columns = [
    { width: '20%' }
    { width: '40%' }
    { width: '20%' }
    { width: '20%' }
  ]

  # autocomplete
  $.get('/analyses/gene_names', (result) ->

    $('#gene-search').autocomplete( 
      minLength: 2
      delay: 0
      select: (e, ui) -> 
        window.location.href = '/genes/' + ui.item.value
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
    
  $('#gene-search').keyup((e) ->
    text = $('#gene-search').val()
    window.location.href = ('/genes/' + text) if (e.keyCode == 13)
  )