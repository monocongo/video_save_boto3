import argparse
import json

import requests
from requests.auth import HTTPDigestAuth

from video_utils.collect_and_store import collect_and_store


# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # USAGE
    # $ python clip_and_store_events.py --device admiraldemo.scw-ddns.com \
    #       --begin 1560052800 --end 1560139199 \
    #       --user admin --password opensesame \
    #       --s3_bucket scw.james.adams --s3_prefix events_test

    # construct the argument parser and parse the arguments
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--device",
                             required=True,
                             type=str,
                             help="IP address or DNS name for device")
    args_parser.add_argument("--port",
                             default=80,
                             type=int,
                             help="Port number")
    args_parser.add_argument("--channel",
                             default=1,
                             type=int,
                             help="Port number")
    args_parser.add_argument("--stream",
                             default=1,
                             type=int,
                             help="Stream number")
    args_parser.add_argument("--begin",
                             required=True,
                             type=int,
                             help="Begin time (UNIX epoch seconds)")
    args_parser.add_argument("--end",
                             required=True,
                             type=int,
                             help="End time (UNIX epoch seconds)")
    args_parser.add_argument("--user",
                             required=True,
                             type=str,
                             help="User credential")
    args_parser.add_argument("--password",
                             required=True,
                             type=str,
                             help="Password credential")
    args_parser.add_argument("--s3_bucket",
                             required=True,
                             type=str,
                             help="S3 bucket for MP4 clips")
    args_parser.add_argument("--s3_prefix",
                             required=True,
                             type=str,
                             help="Prefix for MP4 clips in S3 bucket")
    args = vars(args_parser.parse_args())

    # build a Lightside API endpoint based on our various arguments
    endpoint = f"http://{args['device']}:{args['port']}/LAPI/V1.0/Channels/" \
        f"{args['channel']}/Media/Video/Streams/{args['stream']}/Records?" \
        f"Begin={args['begin']}&End={args['end']}"

    # make the API request for event records
    response = requests.get(endpoint,
                            auth=HTTPDigestAuth(args["user"], args["password"]))

    # get the response data into a list of event records
    content = response.content.decode('utf-8')
    json_data = json.loads(content)
    records = json_data["Response"]["Data"]["RecordInfos"]

    # save each event as an MP4 clip on the specified S3 bucket
    for record in records:

        begin = record["Begin"]
        end = record["End"]
        rtsp = f"rtsp://{args['user']}:{args['password']}@{args['device']}:554/c1"
        collect_and_store(rtsp, begin, (end - begin + 1), args["s3_bucket"], args["s3_prefix"])
