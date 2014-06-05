# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://jashkenas.github.com/coffee-script/
$(document).ready ->
  tbl=$('#features_table').dataTable
    "sPaginationType": "full_numbers"
    "iDisplayLength": 10
    "bProcessing": true
    "bServerSide": true
    "sAjaxSource": '/api/features'
    "bDeferRender": true
    "bStateSave": true
  tbl.fnSetFilteringDelay(iDelay=400)

  url_id=document.URL.split('/')
  url_id.pop()
  $('#feature_table').dataTable
    "sPaginationType": "full_numbers"
    "iDisplayLength": 10
    "bProcessing": true
    "sAjaxSource": '/api/features/'+url_id.pop()
    "bDeferRender": true
    "bStateSave": true
