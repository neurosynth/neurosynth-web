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
            


$(document).ready ->
    $('table[class*=default-datatable]').dataTable
        "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
        "sPaginationType": "bootstrap"
        "iDisplayLength": 10

    $('table[class*=small-datatable]').dataTable
        "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span12'i><'span12'p>>",
        "sPaginationType": "bootstrap"
        "iDisplayLength": 10

    # Make site-wide cookie available
    window.cookie = NSCookie.load()