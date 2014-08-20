$(document).ready ->

  return if not $('#page-topics').length

  topic = document.URL.split('/').slice(-2)[0]

  