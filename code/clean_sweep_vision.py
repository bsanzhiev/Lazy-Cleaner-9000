#!/usr/bin/env python

from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color

def nothing(*arg):
    pass

def is_allowed_color(cur_int, avg_int, m_val):
    b = abs(cur_int[0] - avg_int[0])
    g = abs(cur_int[1] - avg_int[1])
    r = abs(cur_int[2] - avg_int[2])

    if (b > m_val or g > m_val or r > m_val):
        return True
    else:
        return False


def make_gt_val(val, min_val):
    if val < min_val:
        val = min_val
    return val

def make_odd(val):
    if val % 2 == 0:
        val += 1

    return val


def get_avg_bgr(in_img, in_cntrs):
    ttlA = 0
    sum_roiA_mean = (0, 0, 0)
    avg_roiA_mean = (0, 0, 0)
    ttlA  = len(in_cntrs)

    for cnt2 in in_cntrs:

        x2, y2, w2, h2 = cv2.boundingRect(cnt2)
        roiA = in_img[y:y2+w2, x:x2+h2]
        roiA_mean = cv2.mean(roiA)
        int_roiA_mean = (int(roiA_mean[0]), int(roiA_mean[1]), int(roiA_mean[2]))
        sum_roiA_mean = (int_roiA_mean[0] + sum_roiA_mean[0], int_roiA_mean[1] + sum_roiA_mean[1], int_roiA_mean[2] + sum_roiA_mean[2])

        if ttlA > 0:
            avg_roiA_mean = (sum_roiA_mean[0]/ttlA, sum_roiA_mean[1]/ttlA, sum_roiA_mean[2]/ttlA)

    return avg_roiA_mean



window_nm = 'img_cntrls'

cam_res_w = 640
cam_res_h = 480
cam_fr_rt = 32

cv2.namedWindow(window_nm)
cv2.createTrackbar('blur_size', window_nm, 7 , 21, nothing)
cv2.createTrackbar('canny_min', window_nm, 156, 255, nothing)
cv2.createTrackbar('thresh_min', window_nm, 7 , 255, nothing)
cv2.createTrackbar('min_area', window_nm, 5 , 2000, nothing)
cv2.createTrackbar('max_area', window_nm, 40000 , 90000, nothing)
cv2.createTrackbar('max_delta', window_nm, 20 , 100, nothing)
cv2.createTrackbar('get_avg', window_nm, 0 , 1, nothing)
cv2.createTrackbar('get_mode', window_nm, 0, 7, nothing)

camera = PiCamera()
camera.resolution = (cam_res_w, cam_res_h)
camera.framerate = cam_fr_rt
rawCapture = PiRGBArray(camera, size=(cam_res_w, cam_res_h))

time.sleep(0.2)
avg_roi_mean = (0, 0, 0)  #b, g, r
delta_color = 000.0000


for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):

    #############################################
    ### GET THE CURRENT FRAME FROM THE CAMERA ###
    #############################################
    im = frame.array
    im_raw = im  #keep a copy in case we want to look at it later


    ####################
    ### GET SETTINGS ###
    ####################
    s = cv2.getTrackbarPos('get_avg', window_nm)
    blur_size = cv2.getTrackbarPos('blur_size',window_nm)
    canny_min = cv2.getTrackbarPos('canny_min',window_nm)
    thresh_min  = cv2.getTrackbarPos('thresh_min',window_nm)
    min_area = cv2.getTrackbarPos('min_area',window_nm)
    max_area = cv2.getTrackbarPos('max_area',window_nm)
    max_delta = cv2.getTrackbarPos('max_delta',window_nm)
    mode = cv2.getTrackbarPos('get_mode', window_nm)


    ############################
    ### ENSURE CORRECT VALUE ###
    ############################
    blur_size = make_odd(blur_size)
    blur_size = make_gt_val(blur_size, 0)
    thresh_min = make_odd(thresh_min)
    thresh_min = make_gt_val(thresh_min, 0)


    ########################################################
    ###  START IMAGE PROCESSING TO FIND OBJECTS IN RANGE ###
    ########################################################
    imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(imgray, (blur_size, blur_size))
    #edged = cv2.Canny(blur, canny_min, 255)
    ret3, thresh = cv2.threshold(blur, thresh_min, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

    ###S = 1 means get an average of the overall RGB picture
    if s == 1:
        blur_size == 0
        thresh_size = 1
        min_area = 0
        ovr_avg = get_avg_bgr(im, contours)
        avg_roi_mean = ovr_avg


        print avg_roi_mean
        cv2.setTrackbarPos('get_avg', window_nm, 0)

    else:
        ttl_area = 0
        ttl_cntrs = len(contours)
        ttl_color = 0
        sum_roi_mean = (0, 0, 0)

        for cnt in contours:
            a = cv2.contourArea(cnt)

            ### DO WE HAVE SOMETHING IN THE RIGHT SIZE (NO NEED TO PICK UP CARS) ###
            if min_area < a < max_area:
                ttl_area += 1
                x, y, h, w = cv2.boundingRect(cnt)
                roi = im[y:y+h, x:x+w]
                roi_mean = cv2.mean(roi)
                int_roi_mean = (int(roi_mean[0]), int(roi_mean[1]), int(roi_mean[2]))

                b, g, r = avg_roi_mean
                bckgrnd_lab = convert_color(sRGBColor(r, g, b), LabColor)

                contColor_lab = convert_color(sRGBColor(roi_mean[2],roi_mean[1], roi_mean[0]), LabColor)

                delta_color = round(delta_e_cie2000(bckgrnd_lab, contColor_lab),1)

                if delta_color >= max_delta:
                  # if is_allowed_color(int_roi_mean, avg_roi_mean, max_dev):
                  cv2.rectangle(im, (x, y), (x+h, y+w), int_roi_mean, 2)
                  ttl_color += 1
                  strLoc = str(x) + ',' + str(y) + ':' + str(delta_color)
                  cv2.putText(im, strLoc, (x,y), cv2.FONT_HERSHEY_PLAIN, 1.0, (0,0,0), 1)

    strTTL = str(ttl_cntrs) + ' - ' + str(ttl_area) + ' - ' + str(ttl_color)
    cv2.putText(im, str(strTTL), (20,20), cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 0), 2)
    cv2.putText(im, str(avg_roi_mean), (20, cam_res_h - 20) ,cv2.FONT_HERSHEY_PLAIN, 2.0, avg_roi_mean, 2)


    if mode == 0:
      cv2.imshow('imgview', im_raw)
      print 'Raw image view'
    elif mode == 1:
      cv2.imshow('imgview', imgray)
      print 'Grayscale view'
    elif mode == 2:
      cv2.imshow('imgview', blur)
      print 'Blur view'
    elif mode == 3:
      cv2.imshow('imgview', blur)
      print 'Blur view'
    elif mode == 4:
      cv2.imshow('imgview', thresh)
      print 'Threshold view'
    else:
      cv2.imshow('imgview', im)
      print 'Contour overlay on raw view'

    ch = cv2.waitKey(5)
    rawCapture.truncate(0)

    if ch == 27:
        break


cv2.destroyAllWindows()
