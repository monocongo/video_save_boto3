import logging

from flask import Flask, request

from video_utils.collect_and_store import collect_and_store

# initialize the Flask application
app = Flask(__name__)


# ------------------------------------------------------------------------------
# set up a basic, global logger object which will write to the console
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s  %(message)s",
                    datefmt="%Y-%m-%d  %H:%M:%S")
_logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
@app.route('/clip', methods=['GET'])
def record_and_store_clip():

    # message = "Recording video clip with the following parameters:\n" + \
    #           f"\tRTSP URL: {request.args.get('rtsp')}\n" + \
    #           f"\tStart seconds: {request.args.get('start')}\n" + \
    #           f"\tDuration seconds: {request.args.get('duration')}\n" + \
    #           f"\tS3 bucket: {request.args.get('bucket')}\n" + \
    #           f"\tS3 key prefix: {request.args.get('prefix')}\n"
    #
    # _logger.info(message)

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
    app.run(debug=True)
