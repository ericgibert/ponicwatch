from bottle import Bottle, template
http_view = Bottle()

@http_view.route('/')
@http_view.route('/log')
@http_view.route('/log/<page:int>')
def default(page=0):
    rows = http_view.controller.log.get_all_records(from_page=page)
    return template("default", rows=rows, current_page=page)

