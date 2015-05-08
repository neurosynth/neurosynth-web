{div, br, ul, li, a, p, h1, h2, h4, h5, span, strong, form, input, button, hr, table, thead, tr, th, td, label, textarea} = React.DOM

SELECTED = 'info' # CSS class to apply to selected rows

# Local Storage Helper Functions
saveSelection = (selection) ->
  window.localStorage.setItem('ns-selection', JSON.stringify(selection))

saveToLocalStorage = (key, value) ->
  window.localStorage.setItem(key, JSON.stringify(value))

getFromLocalStorage = (key) ->
  val = window.localStorage.getItem(key)
  if val is null then val else JSON.parse(val)

getSelectedStudies = ->
  selection = JSON.parse(window.localStorage.getItem('ns-selection') or "{}")

getPMID = (tr) ->
  # Given tr DOM element parse the PMID
  # Assumes the first column has a link of the form ..../<pmid>
  href = $(tr).find('a').first().attr('href')
  return null if not href?
  return parseInt(/(\d+)/.exec(href)[0])

arrayToObject = (array) ->
  obj = {}
  for item in array
    obj[item] = 1
  return obj

Router = Backbone.Router.extend
  routes:
    "new": "new"
    "saved/:uid": "load"
  load: (uid) ->
    app.setActiveAnalysis(uid)
  new: ->
    console.log "/new URL matched" # Do nothing for now

app =
  props:
    fetchAllAnalysesURL: '/api/custom/all/'
    fetchAllStudiesURL: '/api/studies/all/'
    saveURL: '/api/custom/save/'
    deleteURL: '/api/custom/'
    getCustomAnalysis: '/api/custom/'  # /api/custom/<uid>
    getFullAnalysisURL: '/api/analyses/full/' # /api/analyses/full/
    runAnalysisURL: '/analyses/custom/run/'

  state: # All mutable app state must be contained here
    analyses: []
    allStudies: []
    studyDetails: {}
    activeAnalysis:
      blank: true
      studies: {}
    showModal: false
    modalMessage: 'No message'
    editMode: false

  getAnalysis: (uuid, callback) ->
    # See if the analysis is in the pre-loaded list of saved analyses -
    # (it should be, if it belongs to the current user)
    analysis = @state.analyses.filter((a) -> a.uuid is uuid)[0]
    if analysis?
      analysis.owned = true
      callback(analysis)
      return
    $.ajax
      dataType: 'json'
      type: 'GET'
      url: @props.getCustomAnalysis + uuid.toString() + '/'
      success: (response) =>
        response.owned = false
        callback(response)
      error: ->
        alert "Sorry, the analysis you're trying to access is either private or does not exist"

  setActiveAnalysis: (uuid) ->
    if not (@state.activeAnalysis.saved or @state.activeAnalysis.blank)
      if not confirm "You have unsaved changes that will be discarded. Are you sure you want to proceed?"
        return
    @getAnalysis uuid, (analysis) =>
      @state.activeAnalysis = $.extend {}, analysis
      @state.activeAnalysis.studies = arrayToObject(@state.activeAnalysis.studies)
      @state.activeAnalysis.saved = true

      @syncToLocalStorage()
      @state.editMode = false
      @render()
      @router.navigate('saved/' + uuid)

  activeStudies: ->
    if Object.keys(@state.studyDetails).length is 0
      return []
    return Object.keys(@state.activeAnalysis.studies).map (pmid) => @state.studyDetails[pmid]

  syncToLocalStorage: ->
    window.localStorage.setItem('ns-active-analysis', JSON.stringify(@state.activeAnalysis))

  update: ->
    @state.activeAnalysis.saved = false
    @state.activeAnalysis.blank = false
    @syncToLocalStorage()
    @render()

  removeStudy: (pmid) ->
    delete @state.activeAnalysis.studies[pmid]
    @update()

  removeStudies: (pmids) ->
    for pmid in pmids
      delete @state.activeAnalysis.studies[pmid]
    @update()

  addStudy: (pmid) ->
    @state.activeAnalysis.studies[pmid] = 1
    @update()

  addStudies: (pmids) ->
    for pmid in pmids
      @state.activeAnalysis.studies[pmid] = 1
    @update()

  addAllStudies: ->
    for study in @state.allStudies
      @state.activeAnalysis.studies[study.pmid] = 1
    @update()

  removeAllStudies: ->
    @state.activeAnalysis.studies = {}
    @update()

  cloneActiveAnalysis: ->
    @state.activeAnalysis.uuid = null
    @state.activeAnalysis.id = null
    @state.activeAnalysis.saved = false
    @syncToLocalStorage()
    @router.navigate('new')
    @state.editMode = true
    @render()

  clearActiveAnalysis: ->
    @state.activeAnalysis =
      blank: true
      name: ''
      description: ''
      studies: {}
    @syncToLocalStorage()
    @render()

  setActiveAnalysisAttr: (name, value) ->
    @state.activeAnalysis[name] = value
    @state.activeAnalysis.saved = false
    @render()

  enterEditMode: ->
    @state.editMode = true
    @render()

  deleteAnalysis: (uuid) ->
    if not confirm "Are you sure you want to delete this analysis? "
      return
    $.ajax
      dataType: 'json'
      type: 'DELETE'
      url: @props.deleteURL + uuid.toString() + '/'
      success: (response) =>
        @state.activeAnalysis =
          blank: true
          studies: {}
        @syncToLocalStorage()
        @router.navigate('new')
        @state.editMode = true
        @fetchAllAnalyses()

  saveActiveAnalysis: ->
    @state.showModal = true
    @state.modalMessage = 'Saving analysis. Please wait...'
    data =
      studies: Object.keys(@state.activeAnalysis.studies)
      name: @state.activeAnalysis.name
      description: @state.activeAnalysis.description
      private: @state.activeAnalysis.private
      uuid: @state.activeAnalysis.uuid
    $.ajax
      dataType: 'json'
      type: 'POST'
      data:
        data: JSON.stringify(data)
      url: @props.saveURL
      success: (data) =>
        @state.activeAnalysis.uuid = data.uuid
        @state.activeAnalysis.id = data.id
        @state.activeAnalysis.saved = true
        @state.showModal = false
        @state.editMode = false
        @syncToLocalStorage()
        @router.navigate('saved/' + data.uuid)
        @fetchAllAnalyses()
    @render()

  fetchAllAnalyses: (callback) ->
    $.ajax
      dataType: 'json'
      type: 'GET'
      url: @props.fetchAllAnalysesURL
      success: (data) =>
        @state.analyses = data.analyses
        callback() if typeof(callback) is 'function'
        @render()
      error: (xhr, status, err) =>
        console.error @props.url, status, err.toString()

  fetchAllStudies: (callback) ->
    $.ajax
      dataType: 'json'
      type: 'GET'
      url: @props.fetchAllStudiesURL
      cache: true
      headers:
        'Cache-Control': 'max-age=600'
      success: (data) =>
        @state.allStudies = data.studies
        @state.studyDetails = {}
        for study in data.studies
          @state.studyDetails[study.pmid] = study
        callback() if typeof(callback) is 'function'
        @render()
      error: (xhr, status, err) =>
        console.error @props.url, status, err.toString()

  router: new Router()

  init: ->
    active = getFromLocalStorage('ns-active-analysis')
    if active
      @state.activeAnalysis = active
    else
      @state.editMode = true
    @fetchAllAnalyses =>
      @fetchAllStudies =>
        started = Backbone.history.start
          root: '/analyses/custom/'
        console.log "started ", started

  render: ->
    if not document.getElementById('custom-list-container')?
      return
    React.render React.createElement(AnalysisList, {analyses:@state.analyses, selected_uuid:@state.activeAnalysis.uuid}),
      document.getElementById('custom-list-container')
    React.render(React.createElement(ActiveAnalysis, {analysis: @state.activeAnalysis}), document.getElementById('active-analysis-container'))
    React.render(React.createElement(DialogBox, {}), document.getElementById('modal-container'))

AnalysisListItem = React.createClass
  loadHandler: ->
    app.setActiveAnalysis(@props.uuid)

  render: ->
    div {className: "row bs-callout panel #{ if @props.selected then 'bs-callout-info' else ''}"},
      div {className: "col-md-10"},
        ul {className:'list-unstyled'},
          li {},
            strong {}, @props.name
          li {}, "ID: " + @props.uuid,
          li {}, "#{ @props.numStudies } studies"
      div {className: "col-md-2"},
        button {className:"btn btn-primary btn-sm #{ if @props.selected then '' else ''}", onClick: @loadHandler}, 'Load'

AnalysisList = React.createClass
  render: ->
    div {className:'custom-analysis-list panel'},
      h5 {}, "You have #{ @props.analyses.length } saved custom analyses"
      hr {}, ''
      @props.analyses.map (analysis) =>
        selected = if @props.selected_uuid is analysis.uuid then true else false
        React.createElement AnalysisListItem, {key: analysis.uuid, uuid: analysis.uuid, name:analysis.name, numStudies: analysis.studies.length, selected: selected}


includeIf = (predicate, component) ->
  if predicate
    component
  else
    span {}

ActiveAnalysis = React.createClass
  save: ->
    app.saveActiveAnalysis()

  deleteHandler: ->
    app.deleteAnalysis(@props.analysis.uuid)

  cloneHandler: ->
    app.cloneActiveAnalysis()

  discardHandler: ->
    app.clearActiveAnalysis()

  nameChangeHandler: ->
    app.setActiveAnalysisAttr 'name', @refs.name.getDOMNode().value

  privateChangeHandler: ->
    app.setActiveAnalysisAttr 'private', @refs.private.getDOMNode().checked

  descriptionChangeHandler: ->
    app.setActiveAnalysisAttr 'description', @refs.description.getDOMNode().value

  editHandler: -> app.enterEditMode()

  cancelEditHandler: -> app.setActiveAnalysis(@props.analysis.uuid)

  componentDidMount: ->
    numSelected = Object.keys(app.state.activeAnalysis.studies).length
    if numSelected is 0 and app.state.editMode
      $('#selected-studies-tab-header').removeClass('active')
      $('#all-studies-tab-header').addClass('active')
      $('#selected-studies-tab').removeClass('active')
      $('#all-studies-tab').addClass('active')
    else
      $('#selected-studies-tab-header').addClass('active')
      $('#all-studies-tab-header').removeClass('active')
      $('#selected-studies-tab').addClass('active')
      $('#all-studies-tab').removeClass('active')

  render: ->
    uuid = @props.analysis.uuid
    studies = Object.keys(@props.analysis.studies)
    saved = @props.analysis.saved
    if not app.state.editMode
      header = div {className:'row'},
        div {className: 'col-md-8'},
          p {}, 'Analysis name: ',
            strong {}, @props.analysis.name
          p {}, "Analysis ID: #{ uuid }"
          p {}, "Created by: ",
            strong {}, @props.analysis.user
          h5 {}, "Description:"
          p {}, @props.analysis.description
          p {}, "Privacy: ",
            strong {}, "#{ if @props.analysis.private then 'Private' else 'Anyone with the URL can view this analysis' }"
          hr {}, ''
        div {className: 'col-md-4'},
          p {}, "#{ studies.length } studies in this analysis. "
          includeIf @props.analysis.owned, button {className: 'btn btn-info btn-sm', onClick: @editHandler}, 'Edit'
          span {}, ' '
          button {className: 'btn btn-info btn-sm', onClick: @cloneHandler}, 'Save as...'
          span {}, ' '
          includeIf (studies.length > 0),
            a {className: 'btn btn-primary btn-sm', href: app.props.runAnalysisURL + uuid}, if @props.analysis.owned then 'Run' else 'View Results'
          includeIf (studies.length > 0), span {}, ' '
          includeIf @props.analysis.owned, button {className: 'btn btn-danger btn-sm pull-right', onClick: @deleteHandler}, 'Delete'
    else
      if uuid # previously saved analysis
        header = div {},
          div {className:'row'},
            div {className: 'col-md-8'},
              div {className:'row'},
                label {className: 'col-md-6'}, 'Analysis name:',
                  input {type: 'text', className: 'form-control', ref: 'name', value: @props.analysis.name, onChange: @nameChangeHandler, required:'required'}
              div {className:'row'},
                div {className: 'col-md-8'},
                  p {}, "Analysis ID: #{ uuid }"
              div {className:'row'},
                div {className: 'col-md-12'},
                  form {},
                    div {className: "row"},
                      label {className: 'col-md-8'}, 'Description:',
                      textarea {className: 'form-control', rows: "4", ref: 'description', placeholder: 'Enter a description for this analysis', value: @props.analysis.description, onChange: @descriptionChangeHandler}
                    div {className: "row"},
                      label {className: 'col-md-8'},
                        input {type:'checkbox', ref:'private', checked:@props.analysis.private, onChange: @privateChangeHandler},
                          ' Make this analysis private'
              hr {}, ''
            div {className: 'col-md-4'},
              p {}, "#{ studies.length } studies in this analysis. "
              button {className: "btn #{ if saved then '' else 'btn-primary' } btn-sm", disabled: "#{ if saved then 'disabled' else ''}", onClick: @save}, 'Save'
              span {}, ' '
              button {className: 'btn btn-sm', onClick: @cancelEditHandler}, 'Cancel'
      else # headless (without uuid) analysis only present in browser's local storage
        header = div {},
          div {className: 'row'},
            div {className: 'col-md-12'},
              p {}
          div {className: 'row'},
            div {className: 'col-md-6'},
              div {className: 'row'},
                label {className: 'col-md-8'}, 'Analysis name:',
                  input {type: 'text', className: 'form-control', ref: 'name', value: @props.analysis.name, onChange: @nameChangeHandler, required:'required', placeholder: 'Enter a name for this analysis'}
                br {}, ''
            div {className: 'col-md-6'},
              span {className: ''},
                span {}, "#{ studies.length } studies selected "
                button {className:'btn btn-primary btn-sm', disabled: "#{ if saved then 'disabled' else ''}", onClick: @save}, 'Save as new custom analysis'
                span {}, ' '
                button {className:'btn btn-danger btn-sm', onClick: @discardHandler}, 'Discard'
          div {className:'row'},
            div {className: 'col-md-12'},
              form {},
                div {className: "row"},
                  label {className: 'col-md-8'}, 'Description:',
                    textarea {className: 'form-control', rows:"4", ref: 'description', value: @props.analysis.description, placeholder: 'Enter a description for this analysis',  onChange: @descriptionChangeHandler}
                div {className: "row"},
                  label {className: 'col-md-8'},
                    input {type:'checkbox', ref:'private', checked:@props.analysis.private, onChange: @privateChangeHandler},
                      ' Make this analysis private'
              hr {}, ''

    return div {},
      br {},
      header,
      div {className:'row'},
        div {className: 'col-md-12'},
          div {role: 'tabpanel'},
            ul {className: 'nav nav-tabs', role:'tablist'},
              li {role:'presentation', id:'selected-studies-tab-header'},
                a {href:'#selected-studies-tab', role:'tab', 'data-toggle':'tab'}, "Selected Studies (#{ studies.length })"
              includeIf app.state.editMode,
                li {role:'presentation', id:'all-studies-tab-header'},
                  a {href:'#all-studies-tab', role:'tab', 'data-toggle':'tab'}, "All studies (#{ app.state.allStudies.length })"
            div {className: 'tab-content'},
              div {className: 'tab-pane active', role:'tab-panel', id:'selected-studies-tab'},
                br {},
                React.createElement SelectedStudiesTable, {selectedCount: Object.keys(app.activeStudies()).length, editMode: app.state.editMode}
              div {className: 'tab-pane', role:'tab-panel', id:'all-studies-tab'},
                br {},
                p {}, "Add or remove studies to your analysis by clicking on the study. Studies that are already added are highlighted in blue."
                React.createElement AllStudiestable, {
                  allStudies: app.state.allStudies,
                  selectedCount: Object.keys(app.state.activeAnalysis.studies).length}

DialogBox = React.createClass
  render: ->
    div {className: "modal fade", tabIndex:"-1", role:"dialog", 'aria-hidden':'true'},
      div {className: "modal-dialog modal-sm"},
        div {className:"modal-content"},
          div {className:"modal-body"},
            h4 {}, app.state.modalMessage

  componentDidUpdate: ->
    if app.state.showModal
      $('.modal').modal('show')
    else
      $('.modal').modal('hide')

SelectedStudiesTable = React.createClass
  mixins: [React.addons.PureRenderMixin]

  tableData: ->
    if @props.editMode
      removeHTML = '<button class="btn btn-sm remove-btn btn-warning">remove</button>'
    else
      removeHTML = '-'

    app.activeStudies().map (item) ->
      $.extend({'remove': removeHTML }, item)

  setupRemoveButton: ->
    $('#selected-studies-table').off 'click', '.remove-btn'
    $('#selected-studies-table').on 'click', '.remove-btn', ->
      pmid = getPMID($(this).closest('tr'))
      app.removeStudy(pmid)

  componentDidMount: ->
    $('#selected-studies-table').DataTable
      data: @tableData()
      columns: [
        {data: 'title'}
        {data: 'authors'}
        {data: 'journal'}
        {data: 'year'}
        {data: 'pmid'}
        {data: 'remove'}
      ]
    @setupRemoveButton()

  componentDidUpdate: ->
    t = $('#selected-studies-table').DataTable()
    t.clear()
    t.rows.add @tableData()
    t.draw()
    @setupRemoveButton()

  render: ->
    table {className:'table table-hover', id: 'selected-studies-table'},
      thead {},
        tr {},
          th {}, 'Title '
          th {}, 'Authors'
          th {}, 'Journal'
          th {}, 'Year'
          th {}, 'PMID'
          th {}, 'Action'


AllStudiestable = React.createClass
  mixins: [React.addons.PureRenderMixin]

  componentDidMount: ->
    @currLength = @props.allStudies.legnth
    $('#all-studies-table').DataTable
      data: @props.allStudies
      columns: [
        {data: 'title'}
        {data: 'authors'}
        {data: 'journal'}
        {data: 'year'}
        {data: 'pmid'}
      ]
    setupSelectableTable()

  componentDidUpdate: ->
    if @props.allStudies.length != @currLength
      @currLength = @props.allStudies.length
      t = $('#all-studies-table').DataTable()
      t.clear()
      t.rows.add @props.allStudies
      t.draw()
    redrawTableSelection()

  addAllHandler: ->
    app.addAllStudies()

  removeAllHandler: ->
    app.removeAllStudies()

  filteredPMIDs: ->
    filteredrows = $("#all-studies-table").dataTable()._('tr', {"filter": "applied"})
    filteredrows.map (item) -> item.pmid

  addAllFilteredHandler: ->
    app.addStudies @filteredPMIDs()

  removeAllFilteredHandler: ->
    app.removeStudies @filteredPMIDs()

  render: ->
    div {},
      button {className: 'btn btn-sm btn-info', onClick: @addAllFilteredHandler}, "Add all filtered studies"
      span {}, ' '
      button {className: 'btn btn-sm btn-info', onClick: @removeAllFilteredHandler}, "Remove all filtered studies"
      span {}, ' '
      button {className: 'btn btn-sm btn-warning', onClick: @addAllHandler}, "Add all studies"
      span {}, ' '
      button {className: 'btn btn-sm btn-warning', onClick: @removeAllHandler}, "Remove all studies"
      br {}, ''
      br {}, ''
      table {className: 'table selectable-table', id: 'all-studies-table'},
        thead {},
          tr {},
            th {}, 'Title '
            th {}, 'Authors'
            th {}, 'Journal'
            th {}, 'Year'
            th {}, 'PMID'

redrawTableSelection = ->
#  selection = getSelectedStudies()
  $('.selectable-table').find('tbody').find('tr').each ->
    pmid = getPMID(this)
    if pmid of app.state.activeAnalysis.studies
      $(this).addClass(SELECTED)
    else
      $(this).removeClass(SELECTED)

setupSelectableTable = ->
  $('.selectable-table').on 'click', 'tr', ->
    pmid = getPMID(this)
    if not pmid?
      return
    if pmid of app.state.activeAnalysis.studies
      app.removeStudy(pmid)
    else
      app.addStudy(pmid)
    redrawTableSelection()

  $('.selectable-table').on 'draw.dt', ->
    redrawTableSelection()

  $('#select-all-btn').click ->
    selection = getSelectedStudies()
    $('tbody').find('tr').each ->
      pmid = getPMID(this)
      app.addStudy(pmid)
    saveSelection(selection)
    redrawTableSelection()

  $('#deselect-all-btn').click ->
    selection = getSelectedStudies()
    $('tbody').find('tr').each ->
      pmid = getPMID(this)
      app.removeStudy(pmid)
    saveSelection(selection)
    redrawTableSelection()

  redrawTableSelection()

$(document).ready ->
  setupSelectableTable()
  # On the custom analyses page, warn user of unsaved changes before navigating away
  if document.getElementById('custom-list-container')?
    app.init()
    window.onbeforeunload = (e) ->
      if app.state.activeAnalysis.saved or app.state.activeAnalysis.blank
        return
      e = e or window.event
      message = 'You have unsaved changes.'
      # For IE6-8 and Firefox prior to version 4
      if e
        e.returnValue = message
      # For Chrome, Safari, IE8+ and Opera 12+
      return message
