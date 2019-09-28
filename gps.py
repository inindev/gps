#
# gps data logger
#
#  tested with globalsat bu-353-s4 usb gps receiver
#  https://www.amazon.com/gp/product/B008200LHW
#
#  pip3 install pynmea2
#  prolific driver: https://plugable.com/drivers/prolific
#
#  John Clark 09/2019
#

import sys
import serial
import pynmea2

port = '/dev/cu.usbserial'


try:
    ser = serial.Serial(port, 4800, 8, 'N', 1, timeout=0.5)
except serial.SerialException:
    print('could not connect to {}'.format(port))
    sys.exit(1)

raw_only = False
gga = None
gsa = None
while True:
    try:
        data = ser.readline().decode('utf-8', 'ignore')
        if data.startswith('$GP'):
            # msg.sentence_type == GGA, GSA, RMC, GSV
            # https://www.gpsinformation.org/dale/nmea.htm
            msg = pynmea2.parse(data)

            if raw_only:
                print(msg)

            # GGA   https://www.gpsinformation.org/dale/nmea.htm#GGA
            #   timestamp
            #   lat
            #   lat_dir
            #   lon
            #   lon_dir
            #   gps_qual
            #   num_sats (in use)
            #   horizontal_dil
            #   altitude (meters)
            #   altitude_units
            #   geo_sep (geoidal separation, meters)
            #   geo_sep_units
            #   age_gps_data (age of differential gps data, secs)
            #   ref_station_id (differential rference station id)
            elif ('GGA' == msg.sentence_type) and msg.is_valid:
                #print('{}  {:2.8f}, {:2.8f}  alt: {} {}  num: {}'.format(msg.timestamp, msg.latitude, msg.longitude, msg.altitude, msg.altitude_units, msg.num_sats))
                gga = msg

            # GSA   https://www.gpsinformation.org/dale/nmea.htm#GSA
            #   mode
            #   mode_fix_type (1 = no fix, 2 = 2D fix, 3 = 3D fix)
            #   sv_id01 .. sv_id12
            #   pdop (dilution of precision)
            #   hdop (horizontal dop)
            #   vdop (vertical dop)
            elif 'GSA' == msg.sentence_type:
                #print('precision: {} ({}h {}v)'.format(msg.pdop, msg.hdop, msg.vdop))
                gsa = msg

            # RMC   https://www.gpsinformation.org/dale/nmea.htm#RMC
            #   timestamp
            #   status
            #   lat
            #   lat_dir
            #   lon
            #   lon_dir
            #   spd_over_grnd
            #   true_course
            #   datestamp
            #   mag_variation
            #   mag_var_dir
            #elif 'RMC' == msg.sentence_type:
            #    print('{}  {:2.8f}, {:2.8f}'.format(msg.timestamp, msg.latitude, msg.longitude))

            # GSV   https://www.gpsinformation.org/dale/nmea.htm#GSV
            #   num_messages
            #   msg_num
            #   num_sv_in_view
            #   sv_prn_num_1 .. sv_prn_num_4
            #   azimuth_1 .. azimuth_4
            #   snr_1 .. snr_4
            elif ('GSV' == msg.sentence_type) and (msg.num_messages == msg.msg_num) and gga and gsa:
                print('{}  {:2.8f}, {:2.8f}  alt: {} M  p:{} h:{} v:{}  sats: {}/{}'.format(gga.timestamp, gga.latitude, gga.longitude, gga.altitude, gsa.pdop, gsa.hdop, gsa.vdop, gga.num_sats, msg.num_sv_in_view))
                gga = None
                gsa = None

    except pynmea2.ParseError:
        pass


