from sense_hat import SenseHat
from datetime import datetime,timedelta
import csv

sense=SenseHat()


def get_sense_data():
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
    with open(path,'wb') as f:
        csv.writer(f).writerow(head_raw)
def write_csv(path,data):
    for i in range(len(data)):
        with open(path,'a+') as f:
            csv.writer(f).writerow(data[i])
time_str=datetime.now().strftime('%Y%m%d%H')
path='/home/pi/Desktop/sensorhat_data/'+time_str+'z.csv'
head_raw=['time','temp','pressure','humidity','yaw','pitch','roll','compass_x','compass_y','compass_z','acc_x','acc_y','acc_z','gyro_x','gyro_y','gyro_z']
data=[]
for i in range(100):
    data.append(get_sense_data())

creat_csv(path,head_raw)
write_csv(path,data)
