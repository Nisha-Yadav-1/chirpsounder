#!/usr/bin/env python3

# Save files in each of the folders using pickle (multi-frequency) and later
# load the files to make the plots through another script.
# The filter can be further improved  - with little more complex approaches so
# that it gets close to perfect. The current filters - isn't perfect and
# sometimes select files which don't seem to be from the transmitter station
# we are looking the signals from. This could be due to -- (i) loss of gps
# lock or other technical issues, (ii) imperfect algorithm which we have now !

##
from django.conf import settings
import logging
import pickle
from numpy import unravel_index
import datetime
import shutil
import time
import sys
import scipy.constants as c
import h5py
import numpy as n

import glob
import os

import matplotlib.pyplot as plt
import pandas as pd
import ipdb
from .update_tx_code import create_db_connection, update_tx_code

# Folder which has lfm files.
rootdir = '/media/nishayadav/Seagate Backup Plus Drive/chirp'


# file to be store all lfm files related to virginia
lfm_vir = "/home/nishayadav/chirpsounder2_django/chirpsounder/webapp/app/static/lfm_va/"
par_vir = "/home/nishayadav/Myprojects/par_va"


# All folders (within the rootdir) named by days of the calendar which has the
# lfm_files
dirs = sorted(os.listdir(rootdir))

# Remove first three undated folders. So, dirs has only dated folders which
# contain lfm files. The rootdir will vary by where the data is stored. And,
# dirs may need to be tweaked to ensure it is taking only into the
#'dated-folders'. dirs = dirs[3:-1]

# folder where I want to save my data
output_dir1 = "/home/nishayadav/Myprojects/virginia"

freqlist = [60, 80, 100, 120, 140, 160]


def k_largest_index_argsort(S, k):
    idx = n.argsort(S.ravel())[:-k-1:-1]
    return n.column_stack(n.unravel_index(idx, S.shape))

# Name               :               Nisha Yadav
# Function Name      :               filter_ionograms
# Functionality      :               Filter ionograms function is applied on the row data, and we are getting filtered data of transmitter.
# Parameters         :               Dirs1, data, files, DataDict


logger = logging.getLogger(__name__)


def filter_ionograms(dirs1, data, f, DataDict, normalize_by_frequency=True):
    file_name = f.split("/")[-1]
    ho = None


    if file_name.startswith("lfm"):
        if not file_name.endswith(".done"):
            # print("File name inside loop", f)
            if file_name.endswith(".h5"):
                ho = h5py.File(f, "r")
                # print("par files ", f.startswith("par"))
                t0 = float(n.copy(ho[("t0")]))
                if not "id" in ho.keys():
                    return
                cid = int(n.copy(ho[("id")]))  # ionosonde id

                out_dir1 = os.path.join(output_dir1, dirs1)

                # Create new output directory
                if not os.path.exists(out_dir1):
                    os.makedirs(out_dir1)

                #print("Reading %s rate %1.2f (kHz/s) t0 %1.5f (unix)" % (f, float(n.copy(ho[("rate")]))/1e3, float(n.copy(ho[("t0")]))))
                S = n.copy(ho[("S")])          # ionogram frequency-range
                freqs = n.copy(ho[("freqs")])  # frequency bins
                ranges = n.copy(ho[("ranges")])  # range gates
                Rate = n.copy(ho[("rate")])/1000  # Rate

                DataDict["freqs"] = freqs

                if normalize_by_frequency:
                    for i in range(S.shape[0]):
                        #noise = n.nanmedian(S[i, :])
                        noise = n.median(S[i, :])
                        #print('i=%d' %(i))
                        if noise != 0:
                            S[i, :] = (S[i, :]-noise)/noise

                    S[S <= 0.0] = 1e-3

                max_range_idx = n.argmax(n.max(S, axis=0))
                # axis 0 is the direction along the rows

                unarg = unravel_index(S.argmax(), S.shape)

                dB = n.transpose(10.0*n.log10(S))
                if normalize_by_frequency == False:
                    dB = dB-n.nanmedian(dB)

                unarg1 = unravel_index(n.nanargmax(dB), dB.shape)

                # Assume that t0 is at the start of a standard unix second therefore,
                # the propagation time is anything added to a full second

                dt = (t0-n.floor(t0))
                dr = dt*c.c/1e3
                range_gates = dr+2*ranges/1e3
                r0 = range_gates[max_range_idx]

                DataDict["range_gates"] = range_gates
                # ipdb.set_trace()

                dBB = {}
                for freq in freqlist:
                    dBB[freqs[freq]/1e6] = dB[:, freq]

                #  I am trying to find positions in dB where positive dB values
                # [for the frequency for which the maximum in dB has occurred]
                #  are greater than a threshold [the threshold being : am - 3*ast]
                dB1a = dB[:, unarg1[1]]
                dB2 = dB1a[dB1a > 0]
                pos = n.argwhere(dB1a > 0)
                rg_2 = range_gates[pos]
                ast = n.std(dB2)
                if len(dB2) == 0:
                    # print('No useful data')
                    return

                am = n.max(dB2)
                apos = n.argwhere(dB2 > (am - 3*ast))
                rg_3 = rg_2[apos]

                arr = []
                for j in rg_3:
                    arr.append(j[0][0])

                arr1 = n.array(arr)
                # Takes a vertical cut and the highest intensity is extracted.
                # filters are applied here.
                pos1 = n.argwhere((arr1 > int(data['chriprate'])) & (
                    arr1 < data['first_hop_range_one']))
                ch1 = DataDict['ch1']

                if ((Rate == int(data['chriprate'])) and (data['first_hop_range_one'] < r0 < data['first_hop_range_two'])) | ((Rate == int(data['chriprate'])) and
                                                                                                                              (data['second_hop_range_one'] < r0 < data['second_hop_range_two']) and (len(pos1) > 0)):
                    
                    ch1 += 1
                    if ch1 == 1:

                        DB3 = {}
                        for freq in freqlist:
                            DB3[freqs[freq]/1e6] = dBB[freqs[freq]/1e6]

                        T01 = n.array([t0])
                        T03 = T01
                        range_gates3 = range_gates
                        DataDict['range_gates2'] = range_gates

                    else:

                        DB3 = {}
                        for freq in freqlist:
                            # This try-except is tried as - very occassionally - the first option fails because of mismatch of dimensions of the variables being
                            # sought to be column_stacked. In that case, for this particular file, nans are padded to the the second variable to match
                            # the equivalent dimension of the first variable. This might need little more work if this situation arises for the first file for a given day ! And it will also need
                            # more work if the second variable is greater than the first variable [the reverse is assumed as this situation has occured only for one day so far I think] !
                            try:
                                DB3[freqs[freq]/1e6] = n.column_stack(
                                    (DataDict['DBall'][freqs[freq]/1e6], dBB[freqs[freq]/1e6]))
                            except:
                                dtest = n.full(
                                    [DataDict['DBall'][freqs[freq]/1e6].shape[0] - dBB[3].shape[0]], None)
                                dtest[:] = n.NaN
                                dtest = n.concatenate(
                                    (dBB[freqs[freq]/1e6], dtest), axis=None)
                                DB3[freqs[freq]/1e6] = n.column_stack(
                                    (DataDict['DBall'][freqs[freq]/1e6], dtest))

                        T03 = n.hstack((DataDict['Time'], n.array([t0])))
                        try:
                            range_gates3 = n.column_stack(
                                (DataDict['range_gates3'], range_gates))
                            DataDict['range_gates2'] = range_gates
                        except:
                            range_gatestest = n.full(
                                DataDict['range_gates3'].shape[0] - range_gates.shape[0], None)
                            range_gatestest[:] = n.NaN
                            range_gatestest = n.concatenate(
                                (range_gates, range_gatestest), axis=None)
                            range_gates3 = n.column_stack(
                                (DataDict['range_gates3'], range_gatestest))
                            DataDict['range_gates2'] = range_gatestest

                    DataDict['DBall'] = DB3
                    DataDict['Time'] = T03
                    DataDict['range_gates3'] = range_gates3
                    DataDict['ch1'] = ch1
                    file_names = f.split("/")[-1]


                    # code to update TX_Code for virgina transmitter
                    connection = create_db_connection()
                    logger.info(file_names)
                    update_tx_code(connection, f, data, True)
                else:
                    update_tx_code(connection, f, data, False)
    return DataDict









# Name               :               Nisha Yadav
# Function Name      :               save_var
# Functionality      :               Saving data gettin from the filter ionogram function[Filtered data].
# Parameters         :               Dirs1, DataDict


def save_var(dirs1, DataDict):
    path1 = output_dir1 + '/' + dirs1 + '/' + dirs1[5:10] + 'k.data'
    # print(path1)
    # ipdb.set_trace()ta
    with open(path1, 'wb') as f:
        pickle.dump(DataDict, f)
    with open(path1, 'rb') as f:
        DataDict = pickle.load(f)

# Name               :               Nisha Yadav
# Function Name      :               creating_data_file
# Functionality      :               Creating .data file by using filtered data.
#Parameters         :               data


def creating_data_file(data, folder_name):

    # filter_data = []
    os.remove(os.path.join(settings.BASE_DIR, 'info.log'))

    # filter ionograms for range of entered dates
    # date format "yyyy-mm-dd"
    # 2023-01-27
    # print("Date:- ", folder_name)
    folder_name = folder_name.split("-")
    year = int(folder_name[0])
    month = int(folder_name[1])
    day = int(folder_name[2])
    startDate = datetime.date(year, month, day)
    endDate = datetime.date(year, month, day)
    deltaDate = datetime.timedelta(days=1)

    final_result = False

    # log_file = open("test.log", "w")
    log_file = open("info.log", "w")

    while startDate <= endDate:
        for j in range(0, len(dirs)):
            dirs1 = dirs[j]

            #dtt1 = datetime.datetime.strptime('2021-08-06','%Y-%m-%d').date()
            #dtt2 = datetime.datetime.strptime(dirs1[0:10],'%Y-%m-%d').date()

            # Looking to process data after certain date:
            # if dtt2 > dtt1 :

            # Looking to process data for a certain day:
            if dirs1[0:10] == str(startDate):

                # Looking to process daata for all days for the year of choice : [e.g.: 2021]
                # if dirs1[0:4] == '2021':

                # path goes into each-day-folder within the rootdir
                path = os.path.join(rootdir, dirs1)
                # print(dirs1)
                os.chdir(path)
                fl = glob.glob("%s/*" % (path))
                fl.sort()

                ch1 = 0
                DataDict = {}
                DataDict = {'freqlist': freqlist}
                DataDict['ch1'] = ch1
                # if os.path.exists(lfm_vir):
                #     shutil.rmtree(lfm_vir)
                # else:
                #     os.mkdir(lfm_vir)

                

                if len(fl) > 1:
                    for jf, f in enumerate(fl):
                        # log_file.write('jf=%d\n' % (jf))
                        # log_file.write('ch1=%d\n' %(ch1))


                        filter_ionograms(dirs1, data, f, DataDict)
                        

                    # if DataDict['ch1'] > 1:
                    #     save_var(dirs1, DataDict)

                    
        log_file.close()
                    
        startDate = startDate + deltaDate
    # return final_result