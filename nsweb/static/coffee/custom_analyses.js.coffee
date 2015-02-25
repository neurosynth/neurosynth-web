{div, br, ul, li, a, p, h1, h2, h4, h5, span, form, input, button, hr} = React.DOM
ce = React.createElement

app =
  props:
    fetchAllURL: '/api/custom/all/'
    saveURL: '/api/custom/save/'
    deleteURL: '/api/custom/'

  state: # All mutable app state must be contained here
    activeAnalysis: null
    analyses: []

  setActiveAnalysis: (uuid) ->
    @state.activeAnalysis = @state.analyses.filter((a) -> a.uuid is uuid)[0]
    @render()

  deleteAnalysis: (uuid) ->
    $.ajax
      dataType: 'json'
      type: 'DELETE'
      url: @props.deleteURL + uuid.toString() + '/'
      success: (response) =>
        @fetchAll()

  saveActiveAnalysis: (name) ->
    @state.activeAnalysis.name = name
    data =
      studies: @state.activeAnalysis.studies
      name: name
      uuid: @state.activeAnalysis.uuid
    $.ajax
      dataType: 'json'
      type: 'POST'
      data:
        data: JSON.stringify(data)
      url: @props.saveURL
      success: (data) =>
        @state.activeAnalysis.uuid = data.uuid
        saveToLocalStorage('ns-uuid', data.uuid)
        @fetchAll()

  fetchAll: ->
    $.ajax
      dataType: 'json'
      type: 'GET'
      url: @props.fetchAllURL
      success: (data) =>
        @state.analyses = data.analyses
        @render()
      error: (xhr, status, err) =>
        console.error @props.url, status, err.toString()

  init: ->
    ###
    See if there are any selected studies in localStorage.
    If so, create a new analysis
    ###
    studies = getFromLocalStorage('ns-selection')
    uuid = getFromLocalStorage('ns-uuid')
    if studies
      studies = Object.keys(studies)
    else
      studies = []

    @state.activeAnalysis = {}
    if uuid is null
      @state.activeAnalysis =
        studies: studies
        uuid: uuid

    @fetchAll()

  render: ->
    React.render ce(AnalysisList, {analyses:@state.analyses, selected_uuid:@state.activeAnalysis.uuid}),
      document.getElementById('custom-list-container')
    React.render(ce(ActiveAnalysis, {analysis: @state.activeAnalysis}), document.getElementById('active-analysis-container'))

AnalysisListItem = React.createClass
  loadHandler: ->
    app.setActiveAnalysis(@props.uuid)

  deleteHandler: ->
    app.deleteAnalysis(@props.uuid)

  render: ->
    div {className: "#{ if @props.selected then 'bg-info' else ''}"},
      ul {className:'list-unstyled'},
        li {}, "Name: #{ @props.name }"
        li {}, "uuid: #{ @props.uuid }"
      button {className:"btn btn-primary btn-sm #{ if @props.selected then 'hide' else ''}", onClick: @loadHandler}, 'Load'
      span {}, ' '
      button {className: 'btn btn-info btn-sm'}, 'Copy'
      span {}, ' '
      button {className: 'btn btn-danger btn-sm', onClick: @deleteHandler}, 'Delete'
      hr {}

AnalysisList = React.createClass
  render: ->
    div {className:'custom-analysis-list'},
      h4 {}, "Your saved custom analyses (#{ @props.analyses.length })"
      hr {}, ''
      @props.analyses.map (analysis) =>
        selected = if @props.selected_uuid is analysis.uuid then true else false
        ce AnalysisListItem, {key: analysis.uuid, uuid: analysis.uuid, name:analysis.name, selected: selected}


ActiveAnalysis = React.createClass
  save: ->
    app.saveActiveAnalysis @refs.name.getDOMNode().value

  render: ->
    uuid = @props.analysis.uuid
    studies = @props.analysis.studies
    if uuid # previously saved analysis
      panel = div {},
        h4 {}, @props.analysis.name
        p {}, "uuid: #{ uuid }"
    else # headless (without uuid) analysis only present in browser's local storage
      panel = div {},
        input {type: 'text', className: 'form-control', placeholder: 'Enter a name for this analysis', ref: 'name'}
        br {}, ''
        button {className:'btn btn-primary', onClick: @save}, 'Save selection as new custom analysis'
    div {},
      div {className:'row'},
        div {className: 'col-md-4'},
          p {}, "#{ studies.length } studies selected"
        div {className: 'col-md-8'}, panel
      div {className:'row'},
        div {className: 'col-md-12'},
          @props.analysis.studies.map (study) ->
            p {}, study

#app.init()

SELECTED = 'info' # CSS class to apply to selected rows


# Local Storage Helper Functions
getSelectedStudies = ->
  selection = JSON.parse(window.localStorage.getItem('ns-selection') or "{}")

saveSelection = (selection) ->
  window.localStorage.setItem('ns-selection', JSON.stringify(selection))
  window.localStorage.setItem('ns-uuid', null)

saveToLocalStorage = (key, value) ->
  window.localStorage.setItem(key, JSON.stringify(value))

getFromLocalStorage = (key) ->
  val = window.localStorage.getItem(key)
  if val is null then val else JSON.parse(val)
#  JSON.parse(window.localStorage.getItem(key))

getPMID = (tr) ->
  # Given tr DOM element parse the PMID
  # Assumes the first column has a link of the form ..../<pmid>
  href = $(tr).find('a').first().attr('href')
  return null if not href?
  return /(\d+)/.exec(href)[0]

$(document).ready ->
  $('.selectable-table').on 'click', 'tr', ->
    pmid = getPMID(this)
    selection = getSelectedStudies()
    if pmid of selection
      delete selection[pmid]
    else
      selection[pmid] = 1
    saveSelection(selection)
    $(this).toggleClass(SELECTED)

  redrawTableSelection = ->
    selection = getSelectedStudies()
    $('tbody').find('tr').each ->
      pmid = getPMID(this)
      if pmid of selection
        $(this).addClass(SELECTED)
      else
        $(this).removeClass(SELECTED)

  $('.selectable-table').on 'draw.dt', ->
    redrawTableSelection()

  $('#select-all-btn').click ->
    selection = getSelectedStudies()
    $('tbody').find('tr').each ->
      pmid = getPMID(this)
      selection[pmid] = 1
    saveSelection(selection)
    redrawTableSelection()

  $('#deselect-all-btn').click ->
    selection = getSelectedStudies()
    $('tbody').find('tr').each ->
      pmid = getPMID(this)
      delete selection[pmid]
    saveSelection(selection)
    redrawTableSelection()

  app.init()
