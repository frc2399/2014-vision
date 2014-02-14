from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from SocketServer import ThreadingMixIn
import threading
import time

import cv2, cv2.cv as cv
import numpy as np

HOST_NAME = ''
PORT_NUMBER = 80
FPS = 4

# NOTE: you must be running OpenCV 2.4+!!!
# Instructions for installing on Raspberry Pi here:
# http://denis.doublebuffer.net/lablog/2012/08/10/setting-everything-up-for-opencv-raspberry-pi/

# Usage:
# import webcam
# start_server()
# call update_image and pass a cv2 numpy array in, e.g.,
# update_image(frame)
# Access the webpage at http://<IP ADDRESS>/



buf = None

buf_lock = threading.Lock()

server = None

def start_server(port = None, host = None, fps = None):
    global server, PORT_NUMBER, HOST_NAME, FPS

    if not port is None:
        PORT_NUMBER = port
    if not host is None:
        HOST_NAME = host
    if not fps is None:
        FPS = fps

    server_class = ThreadedHTTPServer
    server = server_class((HOST_NAME, PORT_NUMBER), WebcamHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()


def update_image(img):
    global buf

    with buf_lock:
        retval, buf = cv2.imencode('.jpg', img)
        buf = np.array(buf).tostring()


class WebcamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        '''Respond to a GET request.'''
        if '.jpg' in self.path:
            # request is looking for a jpg
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            with buf_lock:
                self.wfile.write(buf)

        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            update_interval = 1.0/FPS*1000
            self.wfile.write('''
<html>
<body>
<img id="cam" src="/cam.jpg" width="100%%">
<script>
window.setInterval(function() {
  document.getElementById('cam').src = "/cam.jpg?random=" + new Date().getTime();
}, %d);
</script>
</body>
</html>
''' % int(update_interval))


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    '''Handle requests in separate threads'''






def main():
    start_webserver()
    print "Test this out by visiting http://<server>:80/image.jpg"

    try:
        x = 10
        dx = 5
        while True:
            if x > 300:
                x = 300
                dx = -5
            elif x < 10:
                x = 10
                dx = 5
            x += dx
            test_img = np.zeros((240, 320, 3), np.uint8)
            cv2.rectangle(test_img, (x, 10), (50, 100), (200, 200, 200))
            
            update_img(test_img)

            # with open('img%d.jpg' % x, 'w') as f:
            #     f.write(buf)

            time.sleep(.2)

    except KeyboardInterrupt:
        pass
    server.server_close()



if __name__ == '__main__':
    main()



