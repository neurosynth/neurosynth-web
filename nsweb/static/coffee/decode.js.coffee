# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://jashkenas.github.com/coffee-script/
$(document).ready ->
	$('#decode_form').submit( (e) ->
		window.location.replace('/decode/' + $('#neurovault_id').val())
		e.preventDefault()
	)

	$('table[class*=decode-datatable]').dataTable
		"sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
		"sPaginationType": "bootstrap"
		"iDisplayLength": 10
		'aaSorting': [[1, 'desc']]

	$('#decode-tab-menu a:first').tab('show')