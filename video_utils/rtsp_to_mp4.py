import argparse
import time

import cv2
import imutils.video


# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # USAGE
    # $ python rtsp_to_mp4.py --rtsp rtsp://admin:strawberryfluff1@71.85.105.110:554/c4/b1557861006/e1557861148/replay/ \
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
    args_parser.add_argument("--duration",
                             type=int,
                             default=-1,
                             help="Number of seconds per MP4 file "
                                  "(-1 == no duration, full clip")
    args = vars(args_parser.parse_args())

    # sanity check for some of the arguments
    if not args["rtsp"].lower().startswith("rtsp://"):
        raise ValueError("Invalid input URL -- only RTSP supported")
    elif not args["mp4"].lower().endswith(".mp4"):
        raise ValueError("Invalid output file -- only MP4 supported")

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
