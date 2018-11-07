# -*- coding: utf-8 -*-
"""
Created on Sun Aug 04 2015

@author: Nate E
"""

from slab import *
from slab.datamanagement import SlabFile
from numpy import *
import os
from slab.instruments.PNAX import N5242A

from slab.instruments import InstrumentManager
from slab.instruments import Alazar, AlazarConfig
from slab.instruments import InstrumentManager
from liveplot import LivePlotClient
#from slab.instruments import N5242A
from slab.dsfit import fithanger_new_withQc

im = InstrumentManager()
#plotter = LivePlotClient()
dcflux = im['YOKO4']

nwa = im['PNAX']
# nwa = N5242A("N5242A", address="192.168.14.221", query_timeout=10e3)
print nwa.get_id()
#drive = im['RF3']
print 'Deviced Connected'
expt_path = os.getcwd() + '\data'



# initial NWA configuration values
ifbw = 100
read_power = -60.0
probe_power = 10.0
probe_start_freq = 4.88e9
probe_stop_freq = 4.93e9
#If doing a two tone measurement, the read start and stop should be the same thing.
read_start_freq = 4.88e9#4.915e9#
read_stop_freq = 4.93e9#4.915e9#
sweep_pts = 101
avgs = 5
delay = 0
print "Configuring the NWA"
nwa.set_timeout(10E3)
nwa.set_ifbw(ifbw)
nwa.set_trigger_average_mode("point")
nwa.set_trigger_source("EXTERNAL")
# nwa.set_center_frequency(center)
# nwa.set_span(span)
nwa.write(":SOURCE:POWER1 %f" %(read_power))
nwa.write(":SOURCE:POWER3 %f" %(probe_power))
nwa.set_sweep_points(sweep_pts)
nwa.clear_traces()
nwa.setup_measurement("S21")
nwa.setup_take(averages_state=True)
nwa.set_averages_and_group_count(avgs, True)
nwa.set_trigger_average_mode("point")
nwa.set_trigger_source("EXTERNAL")

print "NWA Configured. IFBW = %f Hz, Read_Power = %f, Drive_Power = %f, NumPts = %d, Avgs = %d " %(ifbw,read_power,probe_power,sweep_pts,avgs)

vary_param = "flux"
print "Swept Parameter: %s" % (vary_param)
vary_pts = linspace(-0.36,-0.37,51)
# read_freqs = 4.91e9#4.915e9
two_tone = 0
single_tone = 1
prefix = "singletone_flux_scan"
fname = get_next_filename(expt_path, prefix, suffix='.h5')
print fname
fname = os.path.join(expt_path, fname)

# lp.clear()-
with SlabFile(fname) as f:

    print nwa.get_settings()

    f.save_settings(nwa.get_settings())

if vary_param == "flux":
    if two_tone:
        "Set up for Two Tone Measurement"
        nwa.setup_two_tone_measurement(read_frequency=read_start_freq, read_power=read_power, probe_start=probe_start_freq, probe_stop=probe_stop_freq,probe_power=probe_power,two_tone=1)
    elif single_tone:
        print "Set up for a Single Tone Sweep"
        nwa.setup_two_tone_measurement(read_frequency=read_start_freq, read_power=read_power, probe_start=probe_start_freq,probe_stop=probe_stop_freq, probe_power=probe_power,two_tone=0)
    dcflux.set_output(True)
    dcflux.set_mode('volt')

    for ii,pt in enumerate(vary_pts):

        # if two_tone:
            # read_freq = read_freqs[ii]
            # print "Setting Read Frequency to %.5f GHz" % (read_freq / 1e9)
            # nwa.setup_two_tone_measurement(read_frequency=read_freq)
        print "Driving at %.4f V or %.3f mA" %(pt,pt*(1000.0/50.0))
        dcflux.set_volt(pt)
        time.sleep(0.2)

        data = nwa.take_one_in_mag_phase()
        fpoints = data[0]
        mags = data[1]
        phases = data[2]
        print "finished downloading"
        #time.sleep(na.get_query_sleep())

        with SlabFile(fname) as f:
            f.append_pt((vary_param + '_pts'), pt)
            f.append_line('fpts', fpoints)
            f.append_line('mags', mags)
            f.append_line('phases', phases)
            # f.append_line('read_freq',read_freqs)
            f.append_pt('read_power', read_power)
            f.append_pt('probe_power', probe_power)

        #plotter.append_z('S21',mags,start_step=(fpoints[0], fpoints[1]-fpoints[0]))
    print fname

elif vary_param == "drive_power":
    nwa.setup_two_tone_measurement(read_frequency=4.915e9, read_power=read_power, probe_start=probe_start_freq, probe_stop=probe_stop_freq, probe_power=probe_power, two_tone=1)
    for pt in vary_pts:
        print pt
        nwa.setup_two_tone_measurement(probe_power=pt)
        # nwa.write(":SOURCE:POWER3 %f" %(pt))

        data = nwa.take_one_in_mag_phase()
        fpoints = data[0]
        mags = data[1]
        phases = data[2]
        print "Finished Downloading Data at %.2f dB" %pt
        time.sleep(nwa.get_query_sleep())

        with SlabFile(fname) as f:
            f.append_pt((vary_param + '_pts'), pt)
            f.append_line('fpts', fpoints)
            f.append_line('mags', mags)
            f.append_line('phases', phases)

    print fname

elif vary_param == "drive_frequency":
    nwa.setup_two_tone_measurement(read_frequency=probe_start_freq, read_power=read_power, probe_start=read_start_freq, probe_stop=read_stop_freq, probe_power=probe_power, two_tone=0)
    for pt in vary_pts:
        print pt/1e9
        nwa.write('SENSE:FOM:RANGE4:FREQUENCY:START %f' % pt)
        nwa.write('SENSE:FOM:RANGE4:FREQUENCY:STOP %f' % pt)
        # nwa.setup_two_tone_measurement(read_frequency=pt)
        # nwa.write(":SOURCE:POWER3 %f" %(pt))

        data = nwa.take_one_in_mag_phase()
        fpoints = data[0]
        mags = data[1]
        phases = data[2]
        print "Finished Downloading Data at %.2f GHz" %pt
        time.sleep(nwa.get_query_sleep())

        with SlabFile(fname) as f:
            f.append_pt((vary_param + '_pts'), pt)
            f.append_line('fpts', fpoints)
            f.append_line('mags', mags)
            f.append_line('phases', phases)

    print fname


elif vary_param == "read_frequency":
    nwa.setup_two_tone_measurement(read_frequency=read_freq_start, read_power=read_power, probe_start=probe_start_freq, probe_stop=probe_stop_freq, probe_power=probe_power, two_tone=1)
    for pt in vary_pts:
        print pt/1e9
        nwa.setup_two_tone_measurement(read_frequency=pt)
        # nwa.write(":SOURCE:POWER3 %f" %(pt))

        data = nwa.take_one_in_mag_phase()
        fpoints = data[0]
        mags = data[1]
        phases = data[2]
        print "Finished Downloading Data at %.2f GHz" %pt
        time.sleep(nwa.get_query_sleep())

        with SlabFile(fname) as f:
            f.append_pt((vary_param + '_pts'), pt)
            f.append_line('fpts', fpoints)
            f.append_line('mags', mags)
            f.append_line('phases', phases)

    print fname

elif vary_param == "read_power":

    for pt in vary_pts:
        print pt
        nwa.write(":SOURCE:POWER1 %f" %(pt))

        data = nwa.take_one_in_mag_phase()
        fpoints = data[0]
        mags = data[1]
        phases = data[2]
        print "Finished Downloading Data at %.2f dB" %pt
        time.sleep(nwa.get_query_sleep())

        with SlabFile(fname) as f:
            f.append_pt((vary_param + '_pts'), pt)
            f.append_line('fpts', fpoints)
            f.append_line('mags', mags)
            f.append_line('phases', phases)

    print fname

elif vary_param == "none":
    data = nwa.take_one_in_mag_phase()
    fpoints = data[0]
    mags = data[1]
    phases = data[2]
    print "Finished Downloading Data"
    time.sleep(nwa.get_query_sleep())

    with SlabFile(fname) as f:
        f.append_line('fpts', fpoints)
        f.append_line('mags', mags)
        f.append_line('phases', phases)

    print fname
