class NSCookie

    constructor: (@contents = null) ->
        @contents ?= {
            locationTab: 0
            featureTab: 0
        }
        @save()

    save: () ->
        json = JSON.stringify(@contents)
        $.cookie('neurosynth', json, { expires: 7, path: '/' })

    set: (key, val, save = true) ->
        @contents[key] = val
        @save() if save

    get: (key) ->
        @contents[key]

    @load: () ->
        if !$.cookie('neurosynth')?
            new NSCookie()
        else
            new NSCookie(JSON.parse($.cookie('neurosynth')))

### METHODS USED ON MORE THAN ONE PAGE ###
urlToParams = () ->
    search = window.location.search.substring(1);
    JSON.parse "{\"" + decodeURI(search).replace(/"/g, "\"").replace(/&/g, "\",\"").replace(RegExp("=", "g"), "\":\"") + "\"}"
window.urlToParams = urlToParams

load_reverse_inference_image = (feature) ->
    imgs = [{
      'name': feature + ' (reverse inference)'
      'url': '/features/' + feature + '/images/reverseinference'
    }]
    # 4th argument is color cycling
    viewer.loadImages(imgs, null, null, true)


$(document).ready ->

  # # Update location based on current viewer coords
  # $('#load-location').click((e) =>
  #   xyz = viewer.coords_xyz()
  #   url = '/locations/?x=' + xyz[0] + '&y=' + xyz[1] + '&z=' + xyz[2]
  #   window.location.replace(url);
  # )

  # Make site-wide cookie available
  window.cookie = NSCookie.load()

  # Decoding results for pages that use it
  if $('#page-decode, #page-genes').length

    $('#decoding_results_table').dataTable
      paginationType: "full_numbers"
      displayLength: 10
      processing: true
      stateSave: true
      orderClasses: false
      # ajax: '/decode/' + image_id + '/data'
      order: [[2, 'desc']]
      columns: [
        {
          data: null
          # defaultContent: '<button>view</button>'
          defaultContent: '<i class="fa fa-arrow-left"></i>'
          width: '20%'
        },
        { 
          data: "feature"
          render: (data, type, row, meta) ->
            '<a href="/features/'+ data + '">' + data + '</a>'
          width: '%45%'
        }, 
        {
          data: 'r'
          width: '35%'
          },
        ]
