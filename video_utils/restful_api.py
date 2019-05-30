import argparse
import logging

from flask import Flask, request

from video_utils.collect_and_store import collect_and_store

# initialize the Flask application
app = Flask(__name__)


# ------------------------------------------------------------------------------
@app.route('/clip', methods=['GET'])
def record_and_store_clip():

    s3_key = collect_and_store(request.args.get('rtsp'),
                               int(request.args.get('start')),
                               int(request.args.get('duration')),
                               request.args.get('bucket'),
                               request.args.get('prefix'))

    return s3_key


# ------------------------------------------------------------------------------
@app.route('/hello', methods=['GET'])
def hello():

    return "Hello!"


# ------------------------------------------------------------------------------
if __name__ == '__main__':

    # parse the command line arguments
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--port",
                             type=int,
                             default=5000,
                             help="port number to run on")
    args = vars(args_parser.parse_args())

    app.run(host="0.0.0.0", port=args["port"], debug=False)
