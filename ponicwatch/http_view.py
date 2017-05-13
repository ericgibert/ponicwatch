from bottle import Bottle, template
http_view = Bottle()

@http_view.route('/')
def default():
    return template("default")

