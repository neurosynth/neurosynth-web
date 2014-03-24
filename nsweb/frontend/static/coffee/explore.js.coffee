# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://jashkenas.github.com/coffee-script/
$(document).ready ->

  jQuery.fn.dataTableExt.oPagination.iFullNumbersShowPages = 3

  $('#explore-tab-menu a:first').tab('show')
  # $('#load-file-dialog').dialog(({
  #     autoOpen: false
  #     height: 400
  #     width: 400
  #     modal: true
  #     buttons: [{
  #       text: 'Done'
  #       click: -> $(this).dialog('close')
  #       'class': 'btn btn-primary'
  #     }]
  #   }))

  # $('#load-file').click(() ->
  #   $('#load-file-dialog').dialog('open')
  # )

  # $('#file-form-button').click( (e) =>
  #   url = $('#remote-filename').val()
  #   bits = url.split('/')
  #   name = bits[bits.length-1]
  #   viewer.loadImages([{
  #     name: name
  #     url: url
  #   }])
  #   # $(e.target).dialog('close')
  # )

  $('#decode_form').submit( (e) ->
    window.location.replace('/decode/' + $('#neurovault_id').val())
    e.preventDefault()
  )

  $('#load-url-image').click((e) ->
    url = $('#image_url').val()
    if url.match(/nii(\.gz)*$/)
      bits = url.split('/')
      name = bits[bits.length-1]
      viewer.loadImages([{
        name: name
        url: url
        download: false
      }])
    else
      alert("Error: remote files must be Nifti images with a .nii or .nii.gz extension.")
  )