import argparse
import datetime
import os

import boto3
import ffmpeg


# ------------------------------------------------------------------------------
def collect_and_store(rtsp_url: str,
                      start_seconds: int,
                      duration_seconds: int,
                      s3_bucket: str) -> int:

    # build URL with start and end times
    # NOTE URL is for Uniview RTSP, add options for other camera types
    url = args["rtsp"] + f"/c1/b{start_seconds}/replay/"
    # url = args["rtsp"] + f"/c1/b{start}/e{end}/replay/"

    # file where we'll write clip data
    temp_file = f"clip_b{start_seconds}_e{(start_seconds + duration_seconds)}.mp4"

    # create the equivalent of the ffmpeg command:
    # $ ffmpeg -i <rtsp_url> -vcodec copy -y -rtsp_transport tcp <output_mp4>
    stream = ffmpeg.input(url)
    stream = ffmpeg.output(stream, temp_file,
                           **{"codec:v": "copy",
                              "rtsp_transport": "tcp",
                              "t": f"00:00:{str(duration_seconds).zfill(2)}",
                              "y": None
                              }
                           )
    ffmpeg.run(stream)

    print(f"\n\nMP4 file created: {temp_file}")

    # store the clip to the S3 bucket using the name
    s3_client = boto3.client("s3")
    s3_client.upload_file(temp_file, args["s3_bucket"], temp_file)
    os.remove(temp_file)

    print(f"\n\nMP4 file stored to S3: {temp_file}")


# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # USAGE
    # $ python collect_and_store.py --rtsp rtsp://user:pass1@71.85.125.110:554 \
    #       --s3_bucket elasticbeanstalk-us-east-2-867324276890 \
    #       --duration 30 --count 10

    # construct the argument parser and parse the arguments
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--rtsp",
                             required=True,
                             type=str,
                             help="RTSP URL for video stream")
    args_parser.add_argument("--duration",
                             required=True,
                             type=int,
                             help="duration of saved clips (in seconds)")
    args_parser.add_argument("--count",
                             required=True,
                             type=int,
                             help="number of clips to save")
    args_parser.add_argument("--s3_bucket",
                             required=True,
                             type=str,
                             help="Destination S3 bucket")
    args = vars(args_parser.parse_args())

    # sanity check for some of the arguments
    if not args["rtsp"].lower().startswith("rtsp://"):
        raise ValueError("Invalid input URL -- only RTSP supported")

    start = int(datetime.datetime.now().strftime("%s"))
    end = start + args["duration"]
    number_of_files_to_collect = args["count"]

    while number_of_files_to_collect > 0:

        collect_and_store(args["rtsp"], start, args["duration"], args["s3_bucket"])

        number_of_files_to_collect -= 1
        start += args["duration"]
        end += args["duration"]
