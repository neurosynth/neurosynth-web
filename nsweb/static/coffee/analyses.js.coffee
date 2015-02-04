
$(document).ready ->

  return if not $('#page-analysis').length

  tbl=$('#term-analyses-table').dataTable
    PaginationType: "full_numbers"
    displayLength: 25
    processing: true
    serverSide: true
    ajax: '/api/terms'
    deferRender: true
    stateSave: true
    autoWidth: true
    orderClasses: false
    dom: 'T<"clear">lfrtip'
    tableTools: { sSwfPath: "/static/swf/copy_csv_xls.swf" }
  tbl.fnSetFilteringDelay(iDelay=400)

  tbl=$('#topic-set-table').dataTable
    PaginationType: "full_numbers"
    displayLength: 25
    processing: true
    ajax: '/api/topics'
    deferRender: true
    stateSave: true
    autoWidth: true
    orderClasses: false
    dom: 'T<"clear">lfrtip'
    tableTools: { sSwfPath: "/static/swf/copy_csv_xls.swf" }
  tbl.fnSetFilteringDelay(iDelay=400)

  if topic_set?
    tbl=$('#topic-set-table').dataTable
      PaginationType: "full_numbers"
      displayLength: 25
      processing: true
      ajax: '/api/topics/' + topic_set
      deferRender: true
      stateSave: true
      autoWidth: true
      orderClasses: false
      dom: 'T<"clear">lfrtip'
      tableTools: { sSwfPath: "/static/swf/copy_csv_xls.swf" }
    tbl.fnSetFilteringDelay(iDelay=400)

  $('#analysis-studies-table').dataTable
    paginationType: "full_numbers"
    displayLength: 25
    processing: true
    deferRender: true
    stateSave: true
    orderClasses: false
    dom: 'T<"clear">lfrtip'
    tableTools: { sSwfPath: "/static/swf/copy_csv_xls.swf" }    
    columns: [
      { width: '40%' }
      { width: '38%' }
      { width: '15%' }
      { width: '7%' }
    ]

    # autocomplete
    $.get('/analyses/term_names', (result) ->

      $('#term-analysis-search').autocomplete( 
        minLength: 2
        delay: 0
        select: (e, ui) -> 
          window.location.href = '/analyses/terms/' + ui.item.value
        # only match words that start with string, and limit to 10
        source: (request, response) ->
          re = $.ui.autocomplete.escapeRegex(request.term)
          matcher = new RegExp('^' + re, "i" )
          filtered = $.grep(result.data, (item, index) ->
            return matcher.test(item)
          )
          response(filtered.slice(0, 10))
      )
    )
    
  $('#term-analysis-search').keyup((e) ->
    text = $('#term-analysis-search').val()
    window.location.href = ('/analyses/terms/' + text) if (e.keyCode == 13)
  )

  loadAnalysisStudies = () ->
    url = '/analyses/' + analysis + '/studies?dt=1'
    $('#analysis-studies-table').DataTable().ajax.url(url).load().order([3, 'desc'])

  loadAnalysisImages = () ->
    url = '/analyses/' + analysis  + '/images'
    $.get(url, (result) ->
      loadImages(result.data)
      )

  # Load state (e.g., which tab to display)
  activeTab = window.cookie.get('analysisTab')
  $("#analysis-menu li:eq(#{activeTab}) a").tab('show')

  if analysis?
    loadAnalysisStudies()
    loadAnalysisImages()

  # Update cookie to reflect last tab user was on
  $('#analysis-menu a').click ((e) =>
      e.preventDefault()
      activeTab = $('#analysis-menu a').index($(e.target))
      window.cookie.set('analysisTab', activeTab)
      $(e.target).tab('show')
      if activeTab == 0
          viewer.paint()
  )

  $('#load-location').click((e) ->
      xyz = viewer.coords_xyz()
      window.location.href = '/locations?x=' + xyz[0] + '&y=' + xyz[1] + '&z=' + xyz[2]
  )
