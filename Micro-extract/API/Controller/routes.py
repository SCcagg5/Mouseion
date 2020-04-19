from .routesfunc import *

def setuproute(app, call):
    @app.route('/test/',            ['OPTIONS', 'POST', 'GET'], lambda x = None: call([])                                            )
    @app.route('/login/',    	    ['OPTIONS', 'POST'],        lambda x = None: call([getauth])                                     )
    @app.route('/ocr/',    	        ['OPTIONS', 'POST'],        lambda x = None: call([myauth, download, analyse])                   )
    @app.route('/b64/',    	        ['OPTIONS', 'POST'],        lambda x = None: call([myauth, fromb64,  analyse])                   )
    @app.route('/multiocr/',    	['OPTIONS', 'POST'],        lambda x = None: call([myauth, mutlifile])                           )
    @app.route('/search/',    	    ['OPTIONS', 'POST'],        lambda x = None: call([myauth, search])                              )
    @app.route('/text/',    	    ['OPTIONS', 'POST'],        lambda x = None: call([myauth, gettext])                             )
    def base():
        return
