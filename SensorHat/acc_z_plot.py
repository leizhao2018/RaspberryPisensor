from matplotlib import pyplot as plt
import pandas as pd
from numpy import mat,array
import math
import numpy as np
import datetime
def a2r(angle):
    a=np.array(angle)
    return np.pi*a/180.
def get_acc_vertical(pitch,roll,yaw,acc_x,acc_y,acc_z):
    g=0.980665
    x_d=mat(array([[1,0,0],[0,math.cos(a2r(pitch)),math.sin(a2r(pitch))],[0,-math.sin(a2r(pitch)),math.cos(a2r(pitch))]]))
    y_d=mat(array([[math.cos(a2r(roll)),0,-math.sin(a2r(roll))],[0,1,0],[math.sin(a2r(roll)),0,math.cos(a2r(roll))]]))
    z_d=mat(array([[math.cos(a2r(yaw)),math.sin(a2r(yaw)),0],[math.sin(a2r(yaw)),-math.cos(a2r(yaw)),0],[0,0,1]]))
    g_para=x_d*y_d*z_d*mat(array([[0],[0],[g]]))
    return acc_z-g_para[2,0]

def get_wave_height(data):
    index1=[]
    for i in range(len(data)):
        if data['acc_vertical'][i]<=0 and data['acc_vertical'][i+1]>0:
            index1.append(i)
    data.insert(0,'wave_height',0.)
    velocity=0.0
    for i in range(len(index1)-1):
        time_0=(data['acc_vertical'][index1[i]]*data['time'][index1[i]+1]-data['acc_vertical'][index1[i]+1]*data['time'][index1[i]])/(data['acc_vertical'][index1[i]]-data['acc_vertical'][index1[i]+1])
        time_1=(data['acc_vertical'][index1[i+1]]*data['time'][index1[i+1]+1]-data['acc_vertical'][index1[i+1]+1]*data['time'][index1[i+1]])/(data['acc_vertical'][index1[i+1]]-data['acc_vertical'][index1[i+1]+1])
        delta=(data['time'][index1[i]]-time_0)/1000.
        velocity+=0.5*(data['acc_vertical'][index1[i]]+data['acc_vertical'][index1[i]-1])/0.1*(data['time'][index1[i]]-time_0)/1000.
        sum=velocity*delta+0.5*(data['acc_vertical'][index1[i]]+data['acc_vertical'][index1[i]-1])/0.1*(delta/1000.)**2
        for j in range(index1[i],index1[i+1]+1):
            sum=velocity*delta
            if j==index1[i+1]+1:
                delta=(time_1-data['time'][j])/1000.
            else:
                delta=(data['time'][j]-data['time'][j-1])/1000.
            sum+=velocity*delta+0.5*(data['acc_vertical'][j]+data['acc_vertical'][j-1])/0.1*delta**2 
            velocity+=0.5*(data['acc_vertical'][j]+data['acc_vertical'][j-1])/0.1*delta
            data['wave_height'][j]=sum
    return data

path='/home/jmanning/Desktop/sensorhat/sensorhat_data/2018121500z.csv'
data=pd.read_csv(path,sep=',')
data.insert(0,'acc_vertical',0)
data['acc_vertical']=data.apply(lambda x:get_acc_vertical(x['pitch'],x['roll'],x['yaw'],x['acc_x'],x['acc_y'],x['acc_z']),axis=1)
data=get_wave_height(data)

time_title=(datetime.datetime.strptime('2000-01-01 00:00:00','%Y-%m-%d %H:%M:%S')+datetime.timedelta(seconds=data['time'][0]/1000)).strftime('%Y-%m-%d %H:%M:%S')
    
data['time']=data['time'].map(lambda x:(x-data['time'][0])/1000)
plt.title(str(time_title), fontsize=20)

plt.xlabel('time(s)',fontsize=10)
plt.ylabel('wave height(m)',fontsize=10)
plt.plot(data['time'],data['wave_height'])
plt.show()