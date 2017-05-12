from bottle import Bottle, run
app = Bottle()

class HTTP_View(object):
    """
    Handle the View part of the MVC model
    Provide the HTTP server to deliver pages
    """

    def __init__(self, controller):
        """Creation of the HTTP server"""
        self.controller = controller

    def run(self):
        self.app.run()

@app.route('/')
def default():
    return "Hello World!"

