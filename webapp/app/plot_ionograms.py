#!/usr/bin/env python
import matplotlib
matplotlib.use('Agg')
import numpy as n
import matplotlib.pyplot as plt
import glob
import h5py
import scipy.constants as c
from .chirp_det import *
import sys
import os
import time
import traceback
import re

"""
"station_name":"station_name",
"max_range_extent":"2000e3",
"min_range":"200e3",
"max_range":"1500e3",
"max_range_extent":"2000e3",
"manual_range_extent":"false",
"minimum_analysis_frequency":"0.0", 
"copy_to_server":"false",
"copy_destination":"none",
"""

def plot_ionogram(output_dir,max_range_extent ,min_range,max_range,manual_range_extent,minimum_analysis_frequency,manual_freq_extent,copy_to_server,copy_destination,station_name,min_freq,max_freq,maximum_analysis_frequency,f,normalize_by_frequency=True):
    ho=h5py.File(f,"r")
    t0=float(n.copy(ho[("t0")]))
    if not "id" in ho.keys():
        return
    cid=int(n.copy(ho[("id")]))  # ionosonde id
    
    img_fname="%s/lfm_ionogram-%03d-%1.2f.png"%(output_dir,cid,t0)
    if os.path.exists(img_fname):
        #print("Ionogram plot %s already exists. Skipping"%(img_fname))
        ho.close()
        return
    
    # print("Plotting %s rate %1.2f (kHz/s) t0 %1.5f (unix)"%(f,float(n.copy(ho[("rate")]))/1e3,float(n.copy(ho[("t0")]))))
    S=n.copy(n.array(ho[("S")],dtype=n.float64))          # ionogram frequency-range
    freqs=n.copy(ho[("freqs")])  # frequency bins
    ranges=n.copy(ho[("ranges")])  # range gates


    if normalize_by_frequency:
        for i in range(S.shape[0]):
            noise=n.nanmedian(S[i,:])
            S[i,:]=(S[i,:]-noise)/noise
        S[S<=0.0]=1e-3
            
    max_range_idx=n.argmax(n.max(S,axis=0))
    
    dB=n.transpose(10.0*n.log10(S))
    if normalize_by_frequency == False:
        dB=dB-n.nanmedian(dB)

    dB[n.isnan(dB)]=0.0
    dB[n.isfinite(dB)!=True]=0.0    
    
    # assume that t0 is at the start of a standard unix second
    # therefore, the propagation time is anything added to a full second

    dt=(t0-n.floor(t0))
    dr=dt*c.c/1e3
    # converted to one-way travel time
    range_gates=dr+ranges/1e3
    r0=range_gates[max_range_idx]
    fig=plt.figure(figsize=(1.5*8,1.5*6))
    plt.pcolormesh(freqs/1e6,range_gates,dB,vmin=-3,vmax=30.0,cmap="inferno")
    cb=plt.colorbar()
    cb.set_label("SNR (dB)")
    plt.title("Chirp-rate %1.2f kHz/s t0=%1.5f (unix s)\n%s %s (UTC)"%(float(n.copy(ho[("rate")]))/1e3,float(n.copy(ho[("t0")])),station_name,unix2datestr(float(n.copy(ho[("t0")])))))
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("One-way range offset (km)")
    if manual_range_extent:
        plt.ylim([min_range/1e3,max_range/1e3])
    else:
        plt.ylim([dr-max_range_extent/1e3,dr+max_range_extent/1e3])
#    plt.ylim([dr-1000.0,dr+1000.0])
    if manual_freq_extent:
        plt.xlim([min_freq/1e6,max_freq/1e6])
    else:
        plt.xlim([0,maximum_analysis_frequency/1e6])
    plt.tight_layout()
    plt.savefig(img_fname)
    fig.clf()
    plt.clf()
    plt.close("all")
    import gc
    gc.collect()
    ho.close()
    sys.stdout.flush()
    if copy_to_server:
        os.system("rsync -av %s %s/latest_%s.png"%(img_fname,copy_destination,station_name))


def create_plot_ionograms(filename):
    station_name="station_name"
    max_range_extent=2000000.0
    min_range=200000.0
    max_range=1500000.0
    manual_range_extent=False
    minimum_analysis_frequency=0.0
    copy_to_server=False
    copy_destination=None
    manual_freq_extent=False
    maximum_analysis_frequency=25000000.0
    output_dir="/home/nishayadav/chirpsounder2_django/chirpsounder/webapp/app/static/lfm_va"
    min_freq=0
    max_freq=25000000.0


    filename = f"{output_dir}/{filename}"
    plot_ionogram(output_dir,max_range_extent ,min_range,max_range,manual_range_extent,minimum_analysis_frequency,manual_freq_extent,copy_to_server,copy_destination,station_name,min_freq,max_freq,maximum_analysis_frequency,filename)
                
      