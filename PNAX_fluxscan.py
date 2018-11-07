# -*- coding: utf-8 -*-
"""
Created on Sun Aug 04 2015

@author: Nelson
"""

from slab import *
from slab.datamanagement import SlabFile
from slab.instruments import InstrumentManager
from slab.instruments import Alazar, AlazarConfig
from numpy import *
import time

# from liveplot import LivePlotClient

im=InstrumentManager()
#lp = LivePlotClient()

# dcflux1 = im['YOKO1']
dcflux1 = im['YOKO3']
nwa = im['PNAX1']
#drive = im['RF3']
import os
expt_path=os.getcwd()+'\data'

def nwa_general_scan():
    #set your swept parameter here
    vary_param = "flux"
    print("Swept Parameter: %s" %(vary_param))
    print(nwa.get_id())
    print('Device Connected')

    # initial NWA configuration
    sc_pw = -30
    sc_ifbw = 200
    sweep_pts = 1001
    avgs = 5

    nwa.configure(center=5.74e9, span=100e6, power=sc_pw, ifbw=sc_ifbw, sweep_points=sweep_pts, averages=avgs)

    # # initial NWA configuration values
    # print "Configuring the NWA"
    nwa.set_timeout(10E3)
    nwa.set_ifbw(sc_ifbw)
    # # nwa.set_center_frequency(center)
    # # nwa.set_span(span)
    nwa.write(":SOURCE:POWER1 %f" % (sc_pw))
    # # nwa.write(":SOURCE:POWER3 %f" % (probe_power))
    nwa.set_sweep_points(sweep_pts)
    nwa.clear_traces()
    nwa.setup_measurement("S21")
    nwa.setup_take(averages_state=True)
    nwa.set_averages_and_group_count(avgs, True)

    print("NWA Configured. IFBW = %f Hz, NumPts = %d, Avgs = %d " % (sc_ifbw, sweep_pts, avgs))

    #parameter sweep arrays

    # vary_pts1 = concatenate(linspace(-0.03,-0.02,5),linspace(-0.02,0.02,4))
    # vary_pts1 = concatenate(vary_pts1, linspace(0.02,0.03,5))
    # vary_pts1 = r_[linspace(-0.03,-0.02,5),linspace(-0.02,0.02,4),linspace(0.02,0.03,5)]
    # pow_pts = linspace(-15.0,0.0,4)
    # vary_pts2 = linspace(-0.018,0.018,61)
    # vary_pts2 = linspace(-0.01,0.01,41)
    vary_pts1 = linspace(-0.02,0.02,81)

    #12mA out of 14 finished in 11 hours
    # vary_pts2 = concatenate([linspace(-0.011,-0.0093,7),linspace(0.0093,0.011,7)],axis=0)
    # vary_pts3 = linspace(0.0093,0.011,7)
    # vary_pts2 = concatenate(vary_pts2, vary_pts3)
    # print(vary_pts2)

    prefix1 = "nwa_"+vary_param+"_scan_S21"
    # prefix2 = "nwa_"+vary_param+"_scan_S31"
    fname1=get_next_filename(expt_path,prefix1,suffix='.h5')
    # fname2=get_next_filename(expt_path,prefix2,suffix='.h5')
    print(fname1)
    # print(fname2)
    fname1=os.path.join(expt_path,fname1)
    # fname2=os.path.join(expt_path,fname2)

    #lp.clear()
    with SlabFile(fname1) as f:
        f.save_settings(nwa.get_settings())

    # with SlabFile(fname2) as f:
    #     f.save_settings(nwa.get_settings())

    dcflux1.set_output(True)
    # dcflux2.set_output(True)
    # dcflux1.set_output(True)
    # dcflux2.set_output(True)
    # time.sleep(7200)

    # for var1 in vary_pts2:
    for var1 in vary_pts1:
        # print var
            # dcflux.set_volt(var)
        dcflux1.set_current(var1)
        # dcflux2.set_current(var2)
        nwa.clear_traces()
        nwa.setup_measurement("S21")
        data = nwa.take_one_in_mag_phase()
        # dcflux1.set_output(False)
        # dcflux2.set_output(False)
        # time.sleep((abs(var1)**2+abs(var2)**2)*50000)
        # data=nwa.take_one_averaged_trace()
        # lp.plot_xy('Current Trace',data[0],data[1])
        # lp.append_z('mags',data[1],start_step=((vary_pts[0],vary_pts[1]-vary_pts[0]),(data[0][0],data[0][1]-data[0][0])))
        # lp.append_z('phases',data[2],start_step=((vary_pts[0],vary_pts[1]-vary_pts[0]),(data[0][0],data[0][1]-data[0][0])))
        with SlabFile(fname1) as f:
            f.append_pt((vary_param + '_pts1'), var1)
            # f.append_pt((vary_param + '_pts2'), var2)
            # f.append_pt(('power' + '_pts'), pow_var1)
            f.append_line('fpts', data[0])
            f.append_line('mags', data[1])
            f.append_line('phases', data[2])
        # nwa.clear_traces()
        # nwa.setup_measurement("S31")
        # data = nwa.take_one_in_mag_phase()
        # dcflux1.set_output(False)
        # dcflux2.set_output(False)
        # time.sleep((abs(var1)**2+abs(var2)**2)*50000)
        # data=nwa.take_one_averaged_trace()
        # lp.plot_xy('Current Trace',data[0],data[1])
        # lp.append_z('mags',data[1],start_step=((vary_pts[0],vary_pts[1]-vary_pts[0]),(data[0][0],data[0][1]-data[0][0])))
        # lp.append_z('phases',data[2],start_step=((vary_pts[0],vary_pts[1]-vary_pts[0]),(data[0][0],data[0][1]-data[0][0])))
        # with SlabFile(fname2) as f:
        #     f.append_pt((vary_param + '_pts1'), var1)
        #     f.append_pt((vary_param + '_pts2'), var2)
        #     # f.append_pt(('power' + '_pts'), pow_var1)
        #     f.append_line('fpts', data[0])
        #     f.append_line('mags', data[1])
        #     f.append_line('phases', data[2])


           


    #drive.set_output(False)
    #print(fname)

nwa_general_scan()
#nwa_freq_power_scan()
#nwa_flux_power_scan()
#nwa_probe_flux_scan()
#nwa_flux_scan_driving_qubit()
dcflux1.set_current(0)
# dcflux2.set_current(0)
dcflux1.set_output(False)
# dcflux2.set_output(False)
nwa.write(":SOURCE:POWER1 %f" % (-70.0))