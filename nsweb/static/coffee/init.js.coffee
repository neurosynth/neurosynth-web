class NSCookie

    constructor: (@contents = null) ->
        @contents ?= {
            locationTab: 0
            analysisTab: 0
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


### DATATABLES-RELATED CODE ###

# tabletools defaults for CSV/XLS export
$.fn.dataTable.TableTools.defaults.aButtons = [
    {
      sExtends: 'copy'
      sButtonText: 'Copy'
      oSelectorOpts: page: 'filter'
    },
    {
      sExtends: 'csv'
      sButtonText: 'CSV'
      oSelectorOpts: page: 'filter'
    },
    {
      sExtends: 'xls'
      sButtonText: 'XLS'
      oSelectorOpts: page: 'filter'
    }
  ]

createDataTable = (element, ajax=null, serverSide=false, displayLength=25,
  columns=null, tableTools=true, filterDelay=true, orderClass=false) ->
  opts = {
    pagingType: "full_numbers"
    serverSide: serverSide
    displayLength: displayLength
    stateSave: false
    orderClasses: false
    processing: true
    dom: 'T<"clear">lfrtip'
  }
  if columns?
    opts.autoWidth = false
    opts.columns = columns
  opts.tableTools = { sSwfPath: "/static/swf/copy_csv_xls.swf" } if tableTools
  opts.ajax = ajax if ajax?
  tbl = $(element).dataTable(opts)
  tbl.fnSetFilteringDelay(iDelay=400) if filterDelay
  tbl


### METHODS USED ON MORE THAN ONE PAGE ###
urlToParams = () ->
    search = window.location.search.substring(1);
    JSON.parse "{\"" + decodeURI(search).replace(/"/g, "\"").replace(/&/g, "\",\"").replace(RegExp("=", "g"), "\":\"") + "\"}"
window.urlToParams = urlToParams

load_reverse_inference_image = (analysis, fdr=false) ->
  url = '/analyses/' + analysis + '/images/reverseinference'
  url += '?nofdr' if not fdr
  [{
    name: analysis + ' (reverse inference)'
    url: url
    colorPalette: 'yellow'
    download: true
  }]

$(document).ready ->

  # Make site-wide cookie available
  window.cookie = NSCookie.load()

  # Decoding results for pages that use it
  if $('#page-decode-show, #page-genes-show').length
    
    tbl = $('#decoding_results_table').dataTable
      paginationType: "simple"
      displayLength: 10
      processing: true
      stateSave: false
      orderClasses: false
      autoWidth: false
      order: [[2, 'desc']]
      dom: 'T<"clear">lfrtip'
      tableTools: { sSwfPath: "/static/swf/copy_csv_xls.swf" }
      columns: [
        {
          data: null
          defaultContent: '<button type="button" class="btn btn-xs btn-primary" style="line-height: 1em;"><span class="glyphicon glyphicon-arrow-left"></span></button>'
          width: '20%'
        },
        { 
          data: "analysis"
          render: (data, type, row, meta) ->
            '<a href="/analyses/terms/'+ data + '">' + data + '</a>'
          width: '%60%'
        }, 
        {
          data: 'r'
          width: '20%'
          },
        ]

