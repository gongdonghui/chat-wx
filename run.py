# import module 
from app import create_app

app = create_app('default')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)


@app.route('/')
def index():
    return "Hello World"

@app.route('/error')
def error_m():
    app.logger.info('info log')
    try:
        raise
    except Exception as e:
        app.logger.warning(e,exc_info=True)
    return "Write error log"


@app.route('/get_route_map',methods=['GET'])
def getroutemap():
    return str(app.url_map)



