$(document).ready ->

  return unless $('#page-home').length

  url = '/features/' + feature  + '/images'
  $.get(url, (result) ->
    loadImages(result.data.slice(1,2))
    )