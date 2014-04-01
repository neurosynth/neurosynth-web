from flask_assets import Environment, Bundle

#sweetness: http://webassets.readthedocs.org/en/latest/builtin_filters.html

# application css bundle
css_nsweb = Bundle('scss/*.scss',
                       filters='pyscss', output='css/main.css')

# consolidated css bundle
css_all = Bundle('css/bootstrap.min.css',
                 css_nsweb,
                 filters='cssmin', output='css/main.min.css')

# vendor js bundle
js_vendor = Bundle('js/vendor/jquery-1.11.0.min.js',
                   'js/vendor/bootstrap.min.js',
                   'js/vendor/jquery.dataTables.js',
                   'js/vendor/modernizr-2.6.2-respond-1.1.0.min.js',
                   'js/nsviewer/*.js',
                   filters='jsmin', output='js/vendor.min.js')

# application js bundle
# js_main = Bundle('coffee/*.coffee', filters='coffeescript', output='js/main.js')
js_main = Bundle('coffee/studies.js.coffee',
#                  'coffee/viewer.js.coffee',
                 filters='coffeescript', output='js/main.js')


def init_assets(app):
    webassets = Environment(app)
    webassets.register('css_all', css_all)
    webassets.register('js_vendor', js_vendor)
    webassets.register('js_main', js_main)
    webassets.manifest = 'cache' if not app.debug else False
    webassets.cache = not app.debug
    webassets.debug = app.debug
