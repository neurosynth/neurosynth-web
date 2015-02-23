{div, ul, li, a, p, h1, h2, h5, span, form, input, button, hr} = React.DOM
ce = React.createElement

app =
  activeAnalysis: null
  setActiveAnalysis: (uuid) ->
    @activeAnalysis = uuid

  init: ->
    ###
    See if there are any selected studies in localStorage.
    If so, create a new analysis
    ###

    return

AnalysisListItem = React.createClass
  loadHandler: ->
    console.log 'Load button clicked'

  render: ->
    div {},
      ul {className:'list-unstyled'},
        li {}, "uuid: #{ @props.uuid }"
        li {}, "name: #{ @props.name }"
      button {className:'btn btn-primary btn-sm', onClick: @loadHandler}, 'Load'
      button {className: 'btn btn-info btn-sm'}, 'Copy'
      button {className: 'btn btn-danger btn-sm'}, 'Delete'
      hr {}

AnalysisList = React.createClass
  fetchData: ->
    $.ajax
      dataType: 'json'
      type: 'GET'
      url: @props.url
      success: (data) => @setState {analyses: data.analyses}
      error: (xhr, status, err) => console.error @props.url, status, err.toString()

  componentDidMount: -> @fetchData()

  getInitialState: -> {analyses: []}

  render: ->
    div {className:'analysis-list'},
      @state.analyses.map (analysis) ->
        ce AnalysisListItem, {key: analysis.uuid, uuid: analysis.uuid, name:analysis.name}


SelectedAnalysis = React.createClass
  render: ->
    @props.studies

React.render(ce(AnalysisList, {url:'/api/custom/all/'}), document.getElementById('custom-list-container'))
