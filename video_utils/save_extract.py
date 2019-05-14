import argparse
import os

import boto3
from moviepy.editor import VideoFileClip


# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # USAGE
    # $ python save_extract.py --source /home/james/video/big_buck_bunny_720p_2mb.mp4 \
    #       --dest_s3_bucket elasticbeanstalk-us-east-2-867324276890 \
    #       --dest_s3_key bunny_clip.mp4 \
    #       --start 2 \
    #       --end 7

    # construct the argument parser and parse the arguments
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--source",
                             required=True,
                             type=str,
                             help="Path to the original video file")
    args_parser.add_argument("--dest_s3_bucket",
                             required=True,
                             type=str,
                             help="Destination S3 bucket where the "
                                  "video clip file should be stored")
    args_parser.add_argument("--dest_s3_key",
                             required=True,
                             type=str,
                             help="Destination S3 key for the video clip file")
    args_parser.add_argument("--start",
                             required=True,
                             type=int,
                             help="Starting time (seconds) where original "
                                  "video should be clipped")
    args_parser.add_argument("--end",
                             required=True,
                             type=int,
                             help="Ending time (seconds) where original "
                                  "video should be clipped")
    args = vars(args_parser.parse_args())

    # sanity check for some of the arguments
    if not args["source"].lower().endswith(".mp4"):
        raise ValueError("Invalid video type -- only MP4 supported")

    # open the video file and extract the clip
    video_full = VideoFileClip(args["source"])
    video_clip = video_full.subclip(args["start"], args["end"])

    # create a temporary file where we'll write the clip
    temp_file = "tmp.mp4"
    video_clip.write_videofile(temp_file, codec="libx264")

    # store the clip to the S3 bucket using the name
    s3_client = boto3.client("s3")
    s3_client.upload_file(temp_file, args["dest_s3_bucket"], args["dest_s3_key"])
    os.remove(temp_file)

    # verification
    bucket_contents = s3_client.list_objects(Bucket=args["dest_s3_bucket"])['Contents']
    bucket_keys = list(map(lambda x: x['Key'], bucket_contents))
    if args["dest_s3_key"] in bucket_keys:
        print(f"Successfully saved video clip to S3 bucket {args['dest_s3_bucket']} as {args['dest_s3_key']}")
    else:
        raise ValueError(f"Failed to save video clip to S3 bucket {args['dest_s3_bucket']}")
