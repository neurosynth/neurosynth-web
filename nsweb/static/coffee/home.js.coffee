$(document).ready ->

  return unless $('#page-home').length

  url = '/api/analyses/' + analysis  + '/images'
  $.get(url, (result) ->
    loadImages(result.data.slice(1,2))
    )