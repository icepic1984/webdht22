#!/usr/bin/python
from flipflop import WSGIServer
from webdht22 import app
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename='yapp.log')
    try:
        WSGIServer(app).run()
    except:
        logging.exception("Oops:")
