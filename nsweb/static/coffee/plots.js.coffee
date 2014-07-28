
# Helper functions
runif = (min, max) -> Math.random() * (max - min) + min

Array::min = ->
  @reduce (p, v) ->
    (if p < v then p else v)

Array::max = ->
  @reduce (p, v) ->
    (if p > v then p else v)


class Scatter

  constructor: () ->

    # names = (layer.name for layer in viewer.layerList.layers)
    # alert(names)
    start = new Date().getTime()
    img_x = viewer.layerList.layers[1].image.data
    img_y = viewer.layerList.layers[0].image.data
    img_mask = viewer.layerList.layers[2].image.data

    x = []
    y = []

    canvas = $('canvas#scatter-bg').get(0)
    @context_bg = canvas.getContext('2d')
    [@w, @h] = [canvas.width, canvas.height]
    @context_bg.clearRect(0, 0, @w, @h)

    @context_fg = $('canvas#scatter-fg').get(0).getContext('2d')
    @lastCenter = [0, 0]

    [x_min, x_max, y_min, y_max] = [0, 0, 0, 0]
    nan_count = 0
    for i in [0...91]
      for j in [0...109]
        for k in [0...91]
          if img_mask[i][j][k] != 0
            x.push(img_x[i][j][k])
            y.push(img_y[i][j][k])

    console.log(x.length)
    console.log("loading the data took " + (new Date().getTime() - start))


    start = new Date().getTime()
    [@x_min, @x_max, @y_min, @y_max] = [x.min(), x.max(), y.min(), y.max()]
    # marginTopRight = 0.06
    # marginLeftBottom = 0.2
    margin = 0.05
    @x_min = @x_min - margin * (@x_max - @x_min)
    @x_max = @x_max + margin * (@x_max - @x_min)
    @y_min = @y_min - margin * (@y_max - @y_min)
    @y_max = @y_max + margin * (@y_max - @y_min)
    @x_range = @x_max - @x_min
    @y_range = @y_max - @y_min
    x_scale = @w/@x_range
    y_scale = @h/@y_range
    console.log("computing ranges took " + (new Date().getTime() - start))
    # @context_bg.setTransform(x_scale, 0, 0, -y_scale, -@x_min*x_scale, @y_max*y_scale)
    # console.log([@x_min, @x_max, @x_range, x_scale, @y_min, @y_max, @y_range, y_scale])

    # Background, gridlines, etc.
    @context_bg.fillStyle = '#F0F0FD'
    @context_bg.fillRect(0.1*@w, 0.05*@h, 0.85*@w, 0.85*@h)

    @context_bg.strokeStyle = 'white'
    @context_bg.lineWidth = 1
    for i in [0...5]
      xpos = (0.1 + 0.17*i)*@w
      @context_bg.beginPath()
      @context_bg.moveTo(xpos, 0.05*@h)
      @context_bg.lineTo(xpos, 0.9*@h)
      console.log([xpos, 0.05*@h, 0.9*@h])
      @context_bg.stroke()


    # @context_bg.moveTo(0.1*@w, 0)
    # @context_bg.lineTo(0.1*@w, @h - 0.1*@h)
    # @context_bg.lineTo(@w, @h - 0.1*@h)
    # @context_bg.globalAlpha = 1
    # console.log([0.1*@w, @h - 0.1*@h])
    # @context_bg.stroke()

    start = new Date().getTime()

    @context_bg.fillStyle = '#3366FF'
    @context_bg.globalAlpha = 0.05
    # @context_bg.strokeStyle = 'black'
    # @context_bg.lineWidth = 1
    for xv, i in x
      center = @getCenter(xv, y[i])
      @context_bg.beginPath()
      @context_bg.arc(Math.round(center[0]), Math.round(center[1]), 1.5, 0, 2 * Math.PI)
      @context_bg.fill()
      # @context_bg.stroke()

    # tmp_context.drawImage(canvas, 0, 0)
    # context.drawImage(tmp_canvas, 0, 0)
    console.log("painting the data took " + (new Date().getTime() - start))

    [@x, @y] = [x, y]

  getCenter: (xv, yv) ->
    [(xv - @x_min) / @x_range * @w, (1 - (yv - @y_min) / @y_range) * @h]

  select: (xv, yv) ->
    center = @getCenter(xv, yv)
    @context_fg.clearRect(@lastCenter[0]-10, @lastCenter[1]-10, 20, 20)
    @context_fg.fillStyle = '#00FF66'
    @context_fg.strokeStyle = 'black'
    @context_fg.lineWidth = 1
    @context_fg.globalAlpha = 1.0
    @context_fg.beginPath()
    @context_fg.arc(Math.round(center[0]), Math.round(center[1]), 6, 0, 2 * Math.PI)
    @context_fg.fill()
    @context_fg.stroke()
    @lastCenter = center

make_scatterplot = () ->

    window.scatter = new Scatter()


