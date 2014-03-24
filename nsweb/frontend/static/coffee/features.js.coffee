# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://jashkenas.github.com/coffee-script/
$(document).ready ->
    $('#feature_letter_table').hide()

    $('.feature_letter').click((e) ->
        e.preventDefault()
        $('#feature_letter_table').show()
        id = $(this).attr('id')
        $('#feature_letter_table').dataTable( {
            'bProcessing': true
            'sAjaxSource': "/ajax_get_features_by_letter/#{id}"
            'bDestroy': true
            "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>"
            "sPaginationType": "bootstrap"
            "iDisplayLength": 25
        })
    )

    $('#feature_image_select').change((e) ->
        label = $(this).children("option:selected").text()
        id = $(this).val()
        img = [{
            name: label
            id: id
            download: "/images/#{id}/download"
            }]
        window.loadImages(
            img
        )
    )

    $('#name.search-features').bind('railsAutocomplete.select', (e, data) ->
        $(this).parents('form')[0].submit()
    )

    $('#feature-content-menu a').click ((e) =>
        e.preventDefault()
        activeTab = $('#feature-content-menu a').index($(e.target))
        window.cookie.set('featureTab', activeTab)
        $(e.target).tab('show')
        if activeTab == 0
            viewer.paint()
    )

    $('#load-location').click((e) ->
        coords = viewer.coords_xyz()
        window.location = '/locations/' + coords.join('_')
    )

    # Load state (e.g., which tab to display)
    activeTab = window.cookie.get('featureTab')
    $("#feature-content-menu li:eq(#{activeTab}) a").tab('show')