# coding=utf-8
'''
Show optical flow

USAGE: python opt_flow.py [<video_source>] (Defaults to webcam if no video
source provided.

Keys:
    1      - Show HSV
    ESC    - Exit
'''

from __future__ import print_function
import numpy as np
import cv2
import sys


def draw_flow(img, flow, step=10):
    h, w = img.shape[:2]
    y, x = np.mgrid[step / 2:h:step, step / 2:w:step].reshape(2, -1).astype(
        int)
    fx, fy = flow[y, x].T
    lines = np.vstack([x, y, x + fx, y + fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), (x2, y2) in lines:
        cv2.circle(vis, (x1, y1), 1, (255, 0, 255), -1)
    return vis


def draw_hsv(flow):
    h, w = flow.shape[:2]
    fx, fy = flow[:, :, 0], flow[:, :, 1]
    ang = np.arctan2(fy, fx) + np.pi
    v = np.sqrt(fx * fx + fy * fy)
    hsv = np.zeros((h, w, 3), np.uint8)

    med_ang = np.average(np.ndarray.flatten(ang))
    med_ang *= 180 / np.pi / 2
    med_ang_arr = np.full(ang.shape, med_ang)

    hsv[..., 0] = med_ang_arr
    hsv[..., 1] = 255
    hsv[..., 2] = np.minimum(v * 4, 255)

    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bgr


if __name__ == '__main__':
    print(__doc__)

    try:
        fn = sys.argv[1]
    except IndexError:
        fn = 0

    cam = cv2.VideoCapture(fn)
    ret, prev = cam.read()

    prevgray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    show_hsv = False

    image_width = int(cam.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    image_height = int(cam.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
    fps = int(cam.get(cv2.cv.CV_CAP_PROP_FPS))
    out_flow = cv2.VideoWriter('flow.avi', cv2.cv.CV_FOURCC(*'DIVX'), fps,
                               (image_width, image_height))
    out_hsv = cv2.VideoWriter('hsv.avi', cv2.cv.CV_FOURCC(*'DIVX'), fps,
                              (image_width, image_height))

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prevgray, gray, 0.5, 15, 25, 20, 7,
                                            1.5, 0)
        prevgray = gray

        flow_img = draw_flow(gray, flow)
        cv2.imshow('flow', flow_img)
        out_flow.write(flow_img)

        if show_hsv:
            hsv_img = draw_hsv(flow)
            cv2.imshow('flow HSV', hsv_img)
            out_hsv.write(hsv_img)

        ch = 0xFF & cv2.waitKey(5)

        if ch == 27:
            break

        if ch == ord('1'):
            show_hsv = not show_hsv
            print('HSV flow visualization is', ['off', 'on'][show_hsv])

    cv2.destroyAllWindows()
    out_flow.release()
    out_hsv.release()
