import numpy as n
import argparse
import scipy.signal as ss
import matplotlib.pyplot as plt
import time
import glob
import re
import os
import scipy.fftpack
fftw=False
try:
    fftw=True
    print("using pyfftw")
except:
    print("couldn't load pyfftw, reverting to scipy. performance will suffer")
    fftw=False
    
import h5py
import scipy.constants as c
import datetime

debug_out0=False
def debug0(msg):
    if debug_out0:
        print(msg)
debug_out1=True
def debug1(msg):
    if debug_out1:
        print(msg)

def unix2date(x):
    return datetime.datetime.utcfromtimestamp(float(x))  # ATC bug-fix for python3

def unix2datestr(x):
    return(unix2date(x).strftime('%Y-%m-%d %H:%M:%S'))
