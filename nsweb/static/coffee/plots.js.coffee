
# Helper functions
runif = (min, max) -> Math.random() * (max - min) + min

Array::min = ->
  @reduce (p, v) ->
    (if p < v then p else v)

Array::max = ->
  @reduce (p, v) ->
    (if p > v then p else v)


scatter = () ->

  # names = (layer.name for layer in viewer.layerList.layers)
  # alert(names)
  start = new Date().getTime()
  img_x = viewer.layerList.layers[1].image.data
  img_y = viewer.layerList.layers[0].image.data
  img_mask = viewer.layerList.layers[2].image.data

  x = []
  y = []
  canvas = $('canvas#scatterplot').get(0)
  context = canvas.getContext('2d')
  context.clearRect(0, 0, canvas.width, canvas.height)
  context.globalAlpha = 0.1

  [x_min, x_max, y_min, y_max] = [0, 0, 0, 0]
  nan_count = 0
  for i in [0...91]
    for j in [0...109]
      for k in [0...91]
        if img_mask[i][j][k] != 0
          x.push(img_x[i][j][k])
          y.push(img_y[i][j][k])

  console.log("loading the data took " + (new Date().getTime() - start))

  # console.log(x.length)
  # console.log(y.length)
  # console.log(mask.length)


  x_min = x.min()
  x_max = x.max()
  x_range = x_max - x_min
  y_min = y.min()
  y_max = y.max()
  y_range = y_max - y_min
  console.log([x_min, x_max, x_range, y_min, y_max, y_range])

  start = new Date().getTime()
  context.fillStyle = 'blue'

  for xv, i in x
    centerX = (xv - x_min)/x_range * canvas.width
    yv = y[i]
    centerY = (1 -(yv - y_min)/y_range) * canvas.height
    context.beginPath()
    context.arc(centerX, centerY, 2, 0, 2 * Math.PI)
    context.fill()

  console.log("painting the data took " + (new Date().getTime() - start))