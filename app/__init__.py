from config import config
from flask import Flask,request,json,jsonify,Blueprint,send_from_directory
import os
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler


def create_app(config_name):
    app = Flask(__name__)
    
    # import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # import module
    from app.api.rag import rag
    #from app.api.handle_login import handle_login
    #from app.api.get_answer import  get_answer
    #from app.api.ask_lp import ask_lp
    #from app.api.history import history
    # register blueprint
    app.register_blueprint(rag)
    #app.register_blueprint(handle_login)
   # app.register_blueprint(get_answer)
   # app.register_blueprint(ask_lp)
   # app.register_blueprint(history)


    #######################################
    ##define log config and create log folder
    #######################################
    if os.path.isdir('log') == False:
        os.mkdir('log')
    if os.path.isfile('./log/flask.log') == False:
        with open("./log/flask.log",'w') as f:
            f.close()
    print("app  init before  log!")    
    #====================================logging config======================================
    formatter = logging.Formatter("[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s")
    handler = TimedRotatingFileHandler("log/flask.log", when="D", interval=1, backupCount=15,encoding="UTF-8", delay=False, utc=True)
    app.logger.addHandler(handler)
    handler.setFormatter(formatter)
    #====================================logging config======================================
    print("app  init before  return!")    

    return app
    
