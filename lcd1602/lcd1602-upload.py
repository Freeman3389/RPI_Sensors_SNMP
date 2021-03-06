"""This script will get DHT22 sensor readings, and write to csv files."""
# !/usr/bin/python
# -*- coding: utf-8 -*-
# Originally written by 
# Re-written by Freeman Lee
# Version 0.1.0 @ 2017.06.30
# License: GPL 2.0

import I2C_LCD_driver
import atexit
import time, csv, sys, os, syslog, json
from array import *

# Get settings from '../settings.json'
with open(os.path.abspath(__file__ + '/../..') + '/settings.json') as json_handle:
    configs = json.load(json_handle)
data_path = configs['global']['base_path'] + configs['global']['csv_path']
sensor_location = configs['global']['sensor_location']
sensor_name = str(configs['lcd1602']['sensor_name'])
update_interval = int(configs[sensor_name]['update_interval'])
pid_file = str(configs['global']['base_path']) + sensor_name + '.pid'
# initial variables
mylcd = I2C_LCD_driver.lcd()
syslog.openlog(sys.argv[0], syslog.LOG_PID)
latest_reading_values = []


def get_reading_csv(sensor):
    """Get sensor readings from latest value csv files in sensor-value folder."""
    sensor_reading = None
    csv_path = data_path + sensor + '_' + sensor_location + '_latest_value.csv'
    with open(csv_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        next(csvreader)  # skip header of csv file
        for row in csvreader:
            sensor_reading = row[1]  # get second value
    return sensor_reading


while True:
    try:
        def all_done():
            """Define atexit function"""
            pid = str(pid_file)
            os.remove(pid)

        def write_pidfile():
            """Setup PID file"""
            pid = str(os.getpid())
            f_pid = open(pid_file, 'w')
            f_pid.write(pid)
            f_pid.close()
        atexit.register(all_done)
        # Display date, time, temperature, humidity on LCD
        idx = 0
        for idx in range(9):
            mylcd.lcd_display_string(time.strftime("%m/%d %H:%M:%S"), 1, 1)
            mylcd.lcd_display_string("T:" + str(get_reading_csv('temperature')) + "c", 2, 0)
            mylcd.lcd_display_string("H:" + str(get_reading_csv('humidity')) + "%", 2, 9)
            time.sleep(1)
        mylcd.lcd_clear()
        # Display PMx values on LCD
        mylcd.lcd_display_string("PM2.5: " + str(get_reading_csv('pm25-at') + " ug/m3"), 1, 0)
        mylcd.lcd_display_string("PM10 : " + str(get_reading_csv('pm10-at') + " ug/m3"), 2, 0)
        time.sleep(update_interval)
        mylcd.lcd_clear()
        # Display GPS Latitude and Longitude on LCD
        mylcd.lcd_display_string("Lat: N " + str(get_reading_csv('latitude')), 1, 0)
        mylcd.lcd_display_string("Lon: E " + str(get_reading_csv('longitude')), 2, 0)
        time.sleep(update_interval)
        mylcd.lcd_clear()
        write_pidfile()

    except IOError as e:
        mylcd.lcd_clear()
        syslog.syslog(syslog.LOG_WARNING, "I/O error({0}): {1}".format(e.errno, e.strerror))
        mylcd.lcd_display_string(time.strftime("%m/%d %H:%M:%S"), 1, 1)
        mylcd.lcd_display_string("CANNOT Get data.", 2, 0)
        pass

    except KeyboardInterrupt:
        sys.exit(0)
