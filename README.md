Requirements:Python, MediaPipe, OpenCV, TensorFlow, RTMP, FFmpeg

How to use:
on rpi:
ffmpeg -f v4l2 -framerate 30 -i /dev/video0 -vcodec libx264 -preset ultrafast -tune zerolatency -maxrate 3000k -bufsize 6000k -f flv rtmp://(Rpi's IP address)/live/stream -rtmp_buffer 100000 -rtmp_live live

on computer:
modify project.py line 117 Rpi's IP address
py .\project.py
