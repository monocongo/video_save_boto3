import argparse
import json
from typing import List

import requests
from requests.auth import HTTPDigestAuth

from video_utils.collect_and_store import collect_and_store


# ------------------------------------------------------------------------------
def extract_and_store_event_clips(device: str,
                                  port: int,
                                  channel: int,
                                  stream: int,
                                  begin: int,
                                  end: int,
                                  user: str,
                                  password: str,
                                  s3_bucket: str,
                                  s3_prefix: str) -> List[str]:

    # build a Lightside API endpoint based on our various arguments
    endpoint = f"http://{device}:{port}/LAPI/V1.0/Channels/" \
        f"{channel}/Media/Video/Streams/{stream}/Records?" \
        f"Begin={begin}&End={end}"

    # make the API request for event records
    response = requests.get(endpoint, auth=HTTPDigestAuth(user, password))

    # get the response data into a list of event records
    content = response.content.decode('utf-8')
    json_data = json.loads(content)
    records = json_data["Response"]["Data"]["RecordInfos"]

    clip_s3_urls = []

    # save each event as an MP4 clip on the specified S3 bucket
    for record in records:
        begin = record["Begin"]
        end = record["End"]
        rtsp = f"rtsp://{user}:{password}@{device}:554/c1"
        clip_s3_urls.append(collect_and_store(rtsp,
                                              begin,
                                              (end - begin + 1),
                                              s3_bucket,
                                              s3_prefix))

    return clip_s3_urls


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

    clip_urls = extract_and_store_event_clips(args["device"],
                                              args["port"],
                                              args["channel"],
                                              args["stream"],
                                              args["begin"],
                                              args["end"],
                                              args["user"],
                                              args["password"],
                                              args["s3_bucket"],
                                              args["s3_prefix"])

    print("S3 URLs for event clips:")
    for url in clip_urls:
        print(url)
