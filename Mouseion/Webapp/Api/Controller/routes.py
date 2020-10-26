from .routesfunc import *

def setuproute(app, call):
    @app.route('/',                     ['OPTIONS', 'POST', 'GET'], lambda x = None: call([])                                            )
    @app.route('/login',    	        ['OPTIONS', 'POST'],        lambda x = None: call([getauth])                                     )

    @app.route('/pdf/url',              ['OPTIONS', 'POST'],        lambda x = None: call([myauth, download, pdf_analyse])               )
    @app.route('/pdf/b64',              ['OPTIONS', 'POST'],        lambda x = None: call([myauth, pdf_fromb64, pdf_analyse])            )
    @app.route('/pdfs/_url',            ['OPTIONS', 'POST'],        lambda x = None: call([myauth, pdf_mutlifile])                       )

    @app.route('/img/url',              ['OPTIONS', 'POST'],        lambda x = None: call([myauth, download, img_analyse])               )

    @app.route('/file/url',             ['OPTIONS', 'POST'],        lambda x = None: call([myauth, download, file_analyse])              )


    @app.route('/search',    	        ['OPTIONS', 'GET'],         lambda x = None: call([search])                                      )
    @app.route('/search/<>',    	    ['OPTIONS', 'GET'],         lambda x = None: call([search])                                      )
    @app.route('/text/',    	        ['OPTIONS', 'POST'],        lambda x = None: call([myauth, gettext])                             )
    def base():
        return
