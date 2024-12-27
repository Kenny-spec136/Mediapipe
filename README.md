Requirements:

On Rpi : Python, OpenCV, RTMP, FFmpeg

On computer : Python, MediaPipe, OpenCV, TensorFlow, FFmpeg

How to use:

On Rpi:

Type the following command to start RTMP service.

ffmpeg -f v4l2 -i /dev/video0 -vcodec libx264 -preset ultrafast -tune zerolatency -maxrate 3000k -bufsize 6000k -f flv rtmp://(Rpi's IP address)/live/stream -rtmp_buffer 100000 -rtmp_live live

On computer:

Modify project.py line 117 Rpi's IP address

py .\project.py

How to get Rpi's IP address:

hostname -I

Input Example: (input.json)

Set take medicine time to (10,20), (30,40) and (47,55)
