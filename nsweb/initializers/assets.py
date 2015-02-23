from flask_assets import Environment, Bundle
from nsweb.initializers import settings
from settings import STATIC_FOLDER
from os.path import join

#sweetness: http://webassets.readthedocs.org/en/latest/builtin_filters.html

# application css bundle
css_nsweb = Bundle('scss/home.css.scss',
                'scss/viewer.css.scss',
                'scss/analyses.css.scss',
                'scss/studies.css.scss',
                'scss/locations.css.scss',
                'scss/decode.css.scss',
                'scss/genes.css.scss',
                'scss/jquery-ui-override.css.scss',
                'scss/style.scss',
                filters='pyscss', output='css/main.css')

# consolidated css bundle
css_bundle = Bundle('css/jquery*.css',
                    css_nsweb,
                  'css/font-awesome.min.css',
                  'css/bootstrap*.min.css',
                  'css/dataTables.tableTools.min.css',
                  'css/style.css',
                  filters='cssmin', output='css/main.min.css')

# Compile CoffeeScript to JS.
# NOTE: ORDER MATTERS HERE! Must load init, then viewer, then everything else
coffee_bundle = Bundle('coffee/init.js.coffee',
                 'coffee/viewer.js.coffee',
                 'coffee/plots.js.coffee',
                 'coffee/studies.js.coffee',
                 'coffee/analyses.js.coffee',
                 'coffee/locations.js.coffee',
                 'coffee/decode.js.coffee',
                 'coffee/home.js.coffee',
                 'coffee/custom_analyses.js.coffee',
                 filters='coffeescript', output='js/coffee.js')

# consolidated JavaScript bundle
js_bundle = Bundle('js/lib/jquery.js',
                  'js/lib/jquery-ui.js',
                  'js/lib/jquery.cookie.js',
                  'js/lib/jquery.dataTables.min.js',
                  'js/lib/bootstrap.js',
                  'js/lib/setfilterdelay.js',
                  'js/lib/dataTables.tableTools.min.js',
                  'js/lib/react-0.12.2.js',
                  'js/nsviewer/amplify.js',
                  'js/nsviewer/panzoom.js',
                  'js/nsviewer/rainbow.js',
                  'js/nsviewer/sylvester.js',
                  'js/nsviewer/xtk.js',
                  'js/nsviewer/viewer.js',
                  coffee_bundle,
                   filters='rjsmin', output='js/main.min.js')

def init_assets(app):
    app.config['ASSETS_DEBUG'] = settings.DEBUG
    webassets = Environment(app)
    webassets.config['PYSCSS_STATIC_ROOT'] = join(STATIC_FOLDER, 'scss')
    webassets.config['PYSCSS_STATIC_URL'] = join(STATIC_FOLDER, 'css/main.css')
    webassets.register('css', css_bundle)
    webassets.register('coffee', coffee_bundle)
    webassets.register('js', js_bundle)
    # webassets.manifest = 'cache' if not app.debug else False
    # webassets.cache = not app.debug
    # webassets.debug = app.debug
