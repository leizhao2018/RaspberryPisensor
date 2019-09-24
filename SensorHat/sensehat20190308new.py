from sense_hat import SenseHat
from datetime import datetime,timedelta
import csv
from matplotlib import pyplot as plt
import pandas as pd
from numpy import mat,array
import math
import numpy as np
import os


sense=SenseHat()


def get_sense_data():
    '''get the data from the sensor,temperature,humidity, pressure, compass,accelerometer,gyroscope'''
    sense_data=[]
    # time unit: milliseconds since: 2000-01-01 00:00:00
    time_delta=datetime.now()-datetime.strptime('2000-01-01 00:00:00','%Y-%m-%d %H:%M:%S')
    time=int((time_delta.days*24*3600+time_delta.seconds)*1000+time_delta.microseconds/1000)
    sense_data.append(time)
    
    sense_data.append(sense.get_temperature())  #temperature
    sense_data.append(sense.get_pressure())  #pressure
    sense_data.append(sense.get_humidity())   #humidity
    
    orientation=sense.get_orientation()  
    sense_data.append(orientation['yaw'])
    sense_data.append(orientation['pitch'])
    sense_data.append(orientation['roll'])
    
    mag=sense.get_compass_raw()  #compass
    sense_data.append(mag['x'])
    sense_data.append(mag['y'])
    sense_data.append(mag['z'])
    
    acc=sense.get_accelerometer_raw() #accelerometer
    sense_data.append(acc['x'])
    sense_data.append(acc['y'])
    sense_data.append(acc['z'])

    gyro=sense.get_gyroscope_raw()  #gyroscope
    sense_data.append(gyro['x'])
    sense_data.append(gyro['y'])
    sense_data.append(gyro['z'])
    
    return sense_data



def creat_csv(path,head_raw):
    "create a csv file"
    with open(path,'wb') as f:
        csv.writer(f).writerow(head_raw)
        
def write_csv(path,data):
    '''write the data to csv file'''
    for i in range(len(data)):
        with open(path,'a+') as f:
            csv.writer(f).writerow(data[i])
            
def a2r(angle):
    '''transfer the angle to radian'''
    a=np.array(angle)
    return np.pi*a/180.


def get_acc_vertical(pitch,roll,yaw,acc_x,acc_y,acc_z):
    '''calculate the vertical accelerometer'''
    g=0.980665
    x_d=mat(array([[1,0,0],[0,math.cos(a2r(pitch)),math.sin(a2r(pitch))],[0,-math.sin(a2r(pitch)),math.cos(a2r(pitch))]]))
    y_d=mat(array([[math.cos(a2r(roll)),0,-math.sin(a2r(roll))],[0,1,0],[math.sin(a2r(roll)),0,math.cos(a2r(roll))]]))
    z_d=mat(array([[math.cos(a2r(yaw)),math.sin(a2r(yaw)),0],[math.sin(a2r(yaw)),-math.cos(a2r(yaw)),0],[0,0,1]]))
    g_para=x_d*y_d*z_d*mat(array([[0],[0],[g]]))
    return acc_z-g_para[2,0]

def get_wave_height(data):
    '''calculate the height of wave'''
    index1=[]
    for i in range(len(data)-1):
        if data['acc_vertical'][i]<=0 and data['acc_vertical'][i+1]>0:
            index1.append(i)
    data.insert(0,'wave_height',0.)
    for i in range(len(index1)-1):
        velocity=0.0
        time_0=(data['acc_vertical'][index1[i]]*data['time'][index1[i]+1]-data['acc_vertical'][index1[i]+1]*data['time'][index1[i]])/(data['acc_vertical'][index1[i]]-data['acc_vertical'][index1[i]+1])
        time_1=(data['acc_vertical'][index1[i+1]]*data['time'][index1[i+1]+1]-data['acc_vertical'][index1[i+1]+1]*data['time'][index1[i+1]])/(data['acc_vertical'][index1[i+1]]-data['acc_vertical'][index1[i+1]+1])
        delta=(time_0-data['time'][index1[i]])/1000.
        velocity+=.5*(data['acc_vertical'][index1[i]]+data['acc_vertical'][index1[i]-1])*delta
        #sum=velocity*delta+0.5*(data['acc_vertical'][index1[i]]+data['acc_vertical'][index1[i]-1])/0.1*(delta/1000.)**2
        sum=velocity*delta
        for j in range(index1[i]+1,index1[i+1]+1):
            if j==index1[i+1]+1:
                delta=(time_1-data['time'][j-1])/1000.
            else:
                delta=(data['time'][j]-data['time'][j-1])/1000.
            sum+=velocity*delta+.5*(data['acc_vertical'][j]+data['acc_vertical'][j-1])*delta**2 
            velocity+=.5*(data['acc_vertical'][j]+data['acc_vertical'][j-1])*delta
            data['wave_height'][j]=sum
    return data

def acc_wave_plot(path):

    ''''''
    data=pd.read_csv(path,sep=',')
    data.insert(0,'acc_vertical',0)
    data['acc_vertical']=data.apply(lambda x:get_acc_vertical(x['pitch'],x['roll'],x['yaw'],x['acc_x'],x['acc_y'],x['acc_z']),axis=1)
    data=get_wave_height(data)
    time_title=(datetime.strptime('2000-01-01 00:00:00','%Y-%m-%d %H:%M:%S')+timedelta(seconds=data['time'][0]/1000.)).strftime('%Y-%m-%d %H:%M:%S')
    data['time']=data['time'].map(lambda x:(x-data['time'][0])/1000)
    plt.title(str(time_title), fontsize=20)
    plt.xlabel('time(s)',fontsize=10)
    plt.ylabel('wave height(m)',fontsize=10)
    plt.plot(10*data['time'],data['wave_height'])
    plt.show()
    return data
    
def save_sensor_data(path):
    head_raw=['time','temp','pressure','humidity','yaw','pitch','roll','compass_x','compass_y','compass_z','acc_x','acc_y','acc_z','gyro_x','gyro_y','gyro_z']
    data=[]
    #if not os.path.exists(path):
    creat_csv(path,head_raw)
    for i in range(300):
        data.append(get_sense_data())
    write_csv(path,data)



    
time_str=datetime.now().strftime('%Y%m%d%H')
#path='/home/pi/Desktop/sensorhat/sensorhat_data/'+time_str+'z.csv'
path='/home/pi/Desktop/sensorhat/sensorhat_data/2019031414z.csv'

#save_sensor_data(path)
wave=acc_wave_plot(path)
