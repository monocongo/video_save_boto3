import argparse
import time

import cv2
import ffmpeg
import imutils.video


# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # USAGE
    # $ python rtsp_to_mp4.py --rtsp rtsp://user:pass1@71.85.125.110:554/148/replay/ \
    #       --mp4 video_clip.mp4 \

    # construct the argument parser and parse the arguments
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--rtsp",
                             required=True,
                             type=str,
                             help="RTSP URL for video")
    args_parser.add_argument("--mp4",
                             required=True,
                             type=str,
                             help="Destination MP4 file")
    args_parser.add_argument('--ffmpeg',
                             dest='ffmpeg',
                             action='store_true')
    args_parser.add_argument('--no_ffmpeg',
                             dest='ffmpeg',
                             action='store_false')
    args_parser.set_defaults(ffmpeg=True)
    args = vars(args_parser.parse_args())

    # sanity check for some of the arguments
    if not args["rtsp"].lower().startswith("rtsp://"):
        raise ValueError("Invalid input URL -- only RTSP supported")
    elif not args["mp4"].lower().endswith(".mp4"):
        raise ValueError("Invalid output file -- only MP4 supported")

    if args["ffmpeg"]:

        # create the equivalent of the ffmpeg command:
        # $ ffmpeg -i <rtsp_url> -vcodec copy -y -rtsp_transport tcp <output_mp4>
        stream = ffmpeg.input(args["rtsp"])
        stream = ffmpeg.output(stream, args["mp4"],
                               **{"codec:v": "copy",
                                  "rtsp_transport": "tcp",
                                  "y": None
                                  }
                               )
        ffmpeg.run(stream)

    else:

        # start capturing the video stream, wait a few seconds for warm up
        video_stream = imutils.video.VideoStream(src=args["rtsp"]).start()
        time.sleep(2.0)

        # create VideoWriter object
        video_writer = cv2.VideoWriter()
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = video_stream.stream.get(cv2.CAP_PROP_FPS)
        width = int(video_stream.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_stream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_writer.open(args["mp4"], fourcc, fps, (width, height), True)

        # loop over the frames from the video stream
        while video_stream.grabbed:

            # grab the frame from the video stream and write it to the MP4 file
            frame = video_stream.read()
            video_writer.write(frame)

        # job is finished, release everything
        video_writer.release()
        video_stream.stop()
