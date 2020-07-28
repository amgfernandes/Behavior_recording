'''libraries'''
import psychopy
from ximea import xiapi
from cv2 import VideoWriter, VideoWriter_fourcc
import PIL.Image
import subprocess as sp
import cv2
import time
import sys, signal, os
import numpy as np
from matplotlib import pyplot as plt
#import skvideo
#skvideo.setFFmpegPath(r'D:\Fernandes\ffmpeg-20200724-21442a8-win64-static\bin')
#import skvideo.io


'''default recording parameters'''
width = 320
height = 256
fps = 100

#create instance for first connected camera 
cam = xiapi.Camera()

#start communication
print('Opening camera...')
cam.open_device()


#settings
cam.set_imgdataformat('XI_MONO8')
cam.set_acq_timing_mode("XI_ACQ_TIMING_MODE_FRAME_RATE")



#create instance of Image to store image data and metadata
img = xiapi.Image()

cam.set_width(width)
cam.set_height(height)

camHeight = cam.get_height()
camWidth = cam.get_width()

cam.set_gain(1)#set gain
cam.set_framerate(fps) #frame rate
cam.set_exposure(29) #exposure in us
print('Exposure was set to %i us' %cam.get_exposure())


#start data acquisition
cam.start_acquisition()

num = 0
folder_save='D:/test_ximea/MF344/M4/' #where to store behavioral data


'''how long is the experiment'''
exp_minutes=7  


'''number of frames to save'''
max_frames=fps*exp_minutes*60 #based on frame rate and number of minutes, how many frames to take

if not os.path.exists(folder_save): #create folder for behavioral data if not existing
    os.makedirs(folder_save)

num_frames_save=[] #to store number of frames
time_save=[] # to store recording time


out = cv2.VideoWriter(filename=folder_save+'beh_video.avi', fourcc=0, fps=0, frameSize=(width,height)) 
#0 on both fourcc and fps is uncompressed. Compress with VirtualDub Xvid Batch mode after. Compressing may lead to dropping frames

try:
    print('Starting video. Press CTRL+C to exit.')
    t0 = time.time()
    print('recording height, width, fps:',camHeight, camWidth, cam.get_framerate())
    while True:

        #get data and pass them from camera to img
        cam.get_image(img)

        #create numpy array with data from camera. Dimensions of the array are 
        #determined by imgdataformat
        data = img.get_image_data_numpy()
        


        #show acquired image with time since the beginning of acquisition
        font = cv2.FONT_HERSHEY_PLAIN
        text = '{:5.2f}'.format(time.time()-t0)
        
        num_frames_save.append(num)
        time_save.append(text)
'''can use text to check time, gets written on each frame'''
#        cv2.putText(
#            data, text, (5,100), font, 4, (255, 255, 255), 1
#            )
        cv2.imshow('/XiCAM recording', data)
        
        out.write(data) #save behavioral data

        #cv2.imwrite(folder_save+'ximea'+str(num)+'.png', data)# if needed to save images one by one
        num += 1
        cv2.waitKey(1)
        
        if num >= max_frames:
            break
        
except KeyboardInterrupt:
        cv2.destroyAllWindows()
finally:
        cv2.destroyWindow('XiCAM recording')
        out.release()



'''store csv file with time and frames'''
num_frames_save=np.array(num_frames_save)
time_save=np.array(time_save)
save_timing=np.vstack([num_frames_save,time_save.astype(float)])
np.savetxt(folder_save+'frames.csv',save_timing.T, delimiter=',', header='frames,time')
print('Total frames:', num_frames_save.max()+1)
print ('Number of dropped frames', max_frames-num_frames_save.shape[0])

#stop data acquisition
print('Stopping acquisition...')
cam.stop_acquisition()

#stop communication
cam.close_device()


print('Done.')
