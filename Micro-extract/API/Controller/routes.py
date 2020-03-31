from .routesfunc import *

def setuproute(app, call):
    @app.route('/test/',            ['OPTIONS', 'POST', 'GET'], lambda x = None: call([])                                            )
    @app.route('/login/',    	    ['OPTIONS', 'POST'],        lambda x = None: call([getauth])                                     )
    @app.route('/ocr/',    	        ['OPTIONS', 'POST'],        lambda x = None: call([myauth, download, analyse])                   )
    def base():
        return
