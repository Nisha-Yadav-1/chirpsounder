import time
import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .update_tx_code import *
from .plot_ionograms import create_plot_ionograms
from datetime import datetime, timedelta, timezone
import glob
import psycopg2
from django.contrib import messages
from . import filter_ionogram
from .models import Chripsounder, ReceiverInfos, DirectoryInfos
from django.http import HttpResponse
from django.shortcuts import render, redirect
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


# Create your views here.


def homepage(request):
    data = Chripsounder.objects.filter(deleted=False)
    return render(request, 'index.html', {"data": data})


def delete_sounder(request, id):
    data = Chripsounder.objects.get(id=id)
    data.deleted = True
    data.save()
    return redirect('/')


def view_ionograms(request, filename):
    """
    Functions to view filtered ionograms

    """

    lfm_vir = "/home/nishayadav/chirpsounder2_django/chirpsounder/webapp/app/static/lfm_va/*"
    files = glob.glob(lfm_vir)
    h5_files = []
    png_files = []
    for file_name in files:
        if file_name.endswith("h5"):
            h5_files.append(file_name)
        else:
            png_files.append(file_name.split("/")[-1])

    filter_data = []
    for i in h5_files:
        png_file = i.split("/")[-1]

        if f'{png_file[0: -2]}png' in png_files:
            filter_data.append(f'{png_file[0: -2]}png')
    for_previous = []
    for_next = []

    index = filter_data.index(filename)
    for_previous = filter_data[0: index]
    for_next = filter_data[index+1:]
    return render(request, 'view-ionograms.html', {"filename": filename, "for_previous": for_previous, "for_next": for_next})


def timestamp_to_datetime(timestamp):
    """
    This function is used to convert the timestamp to readable date time. 

    """
    timestamp = int(timestamp)
    dt = datetime.utcfromtimestamp(timestamp).replace(
        tzinfo=timezone.utc) + timedelta(hours=5)
    dt = dt.strftime("%Y-%m-%d %I:%M:%S %p")
    return dt


@api_view(['GET'])
def filter_ionograms_api(request, folder_name, id):
    if request.method == 'GET':
        time.sleep(5)
        conn = create_db_connection()
        data = Chripsounder.objects.filter(id=int(id)).values()[0]
        files = list(get_virginia_lfm_ionograms(conn, folder_name))
        if len(files) > 0:
            files = files
        else:
            filter_ionogram.creating_data_file(data, folder_name)
        files = list(get_virginia_lfm_ionograms_api(conn, folder_name))
        json_data = {"data": files}
        if len(json_data):
            return Response(json_data)
        else:
            return Response({"status": 500})


def event_stream():
    for i in range(5):
        time.sleep(3)
        yield 'data: The server time is: %s\n\n' % datetime.datetime.now()


def filter_ionograms(request, folder_name, id):
    conn = create_db_connection()
    data = Chripsounder.objects.filter(id=int(id)).values()[0]
    files = list(get_virginia_lfm_ionograms(conn, folder_name))
    if len(files) > 0:
        files = files
    else:
        filter_ionogram.creating_data_file(data, folder_name)
    files = list(get_virginia_lfm_ionograms(conn, folder_name))
    return render(request, 'filter_ionogram.html', {"data": files, "name": data, "date": folder_name, "id": id, })


def edit_transmitter(request, id):
    data = Chripsounder.objects.filter(id=id)
    context = {}
    if request.method == 'POST':
        name_of_transmitter = request.POST['transmitter_name']
        tx_code = request.POST['tx_code']
        lat = request.POST['lat']
        long = request.POST['long']
        ground_range = request.POST['ground_range']
        first_hop_range_one = request.POST['first_hop_range_one']
        first_hop_range_two = request.POST['first_hop_range_two']
        chriprate = request.POST['chrip_rate']
        second_hop_range_one = request.POST['second_hop_range_one']
        second_hop_range_two = request.POST['second_hop_range_two']
        context.update(
            {
                "name_of_transmitter": name_of_transmitter,
                "tx_code": tx_code,
                "lat": lat,
                "longitude": long,
                "range_zero": ground_range,
                "chriprate": chriprate,
                "first_hop_range_one": first_hop_range_one,
                "first_hop_range_two": first_hop_range_two,
                "second_hop_range_one": second_hop_range_one,
                "second_hop_range_two": second_hop_range_two,
            }
        )
        data.update(**context)
        return redirect('homepage')
    return render(request, 'edit.html', {"data": data[0]})


def receiver_info(request):
    data = ReceiverInfos.objects.filter(deleted=False)
    return render(request, 'admin.html', {'data': data})


def delete_receiver_info(request, id):
    data = ReceiverInfos.objects.get(id=id)
    data.deleted = True
    data.save()
    return redirect('/receiver-info')


def edit_receiver(request, id):
    data = ReceiverInfos.objects.filter(id=id)
    context = {}
    if request.method == 'POST':
        receiver_name = request.POST['receiver_name']
        receiver_code = request.POST['receiver_code']
        receiver_location = request.POST['receiver_location']
        receiver_lat = request.POST['receiver_lat']
        receiver_long = request.POST['receiver_long']

        context.update(
            {
                "receiver_name": receiver_name,
                "receiver_code": receiver_code,
                "receiver_location": receiver_location,
                "receiver_lat": receiver_lat,
                "receiver_long": receiver_long,
            }
        )
        data.update(**context)
        return redirect('receiver-info')
    return render(request, 'edit-receiver.html', {"data": data[0]})


def create_ionograms(request, filename):
    create_plot_ionograms(filename)
    return redirect('/filter-ionograms/3')


def get_folder_name(path):
    return {"folder_name": path.split("/")[-1]}


rootdir = '/media/nishayadav/Seagate Backup Plus Drive/chirp/*'


def unfiltered_ionograms(request):
    lst = glob.glob(rootdir)
    lst = list(map(get_folder_name, lst))
    page = request.GET.get('page', 1)

    paginator = Paginator(lst, 40)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)


    return render(request, 'all-ionograms.html', {"users": users})




def filter_ionograms_by_tx_code(request, tx_code):
    base_url = "/home/nishayadav/Myprojects/lfm_va"

    conn = create_db_connection()


    folder = get_folder_date(conn, tx_code)


    flag = 'only_for_tx_code'
    logger.info('Message to display on console and UI')
    return render(request, 'view-filtered_ionogram.html', {"users": folder, "base_url": base_url, 'flag': flag, "tx_code": tx_code})




def view_ionograms_by_tx_code(request, tx_code):
    base_url = "/home/nishayadav/Myprojects/lfm_va"
    print(tx_code)

    conn = create_db_connection()
    data = get_search_data(conn, tx_code, start_date=None, end_date=None)

    filter_data = {}
    if tx_code != 'Choose TX Code':
        filter_data.update(
            {
                "tx_code": tx_code

            }
        )
    return render(request, 'view-unfiltered_ionograms.html', {"data": data, "base_url": base_url, "filtered_data": filter_data})


def view_filtered_ionograms(request, id):
    lst = glob.glob(rootdir)
    lst = list(map(get_folder_name, lst))
    page = request.GET.get('page', 1)

    paginator = Paginator(lst, 40)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return render(request, 'view-filtered_ionogram.html', {"users": users, "id": id})


def view_unfiltered_ionograms(request, folder_name):
    base_url = "/home/nishayadav/Myprojects/lfm_va"
    conn = create_db_connection()
    data = get_unfiltered_ionograms(conn, folder_name)
    page = request.GET.get('page', 1)
    paginator = Paginator(data, 40)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    return render(request, 'view-unfiltered_ionograms.html', {"data": data, "base_url": base_url, 'selected_date': folder_name})


def search_by_codes(request):
    if request.method == 'POST':
        tx_code = request.POST['tx_code']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']

        base_url = "/home/nishayadav/Myprojects/lfm_va"

        conn = create_db_connection()
        data = get_search_data(conn, tx_code, start_date, end_date)
        filter_data = {}
        if tx_code != 'Choose TX Code' and start_date and end_date:
            filter_data.update(
                {
                    "tx_code": tx_code,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )

        elif start_date and end_date:
            filter_data.update(
                {
                    "start_date": start_date,
                    "end_date": end_date
                }
            )

        elif tx_code != 'Choose TX Code':
            filter_data.update(
                {
                    "tx_code": tx_code
                }
            )

    return render(request, 'view-unfiltered_ionograms.html', {"data": data, "base_url": base_url, "filtered_data": filter_data})


def loginfo(request):
    f = open(os.path.join(settings.BASE_DIR, 'info.log'), 'r')
    return render(request, 'log.html', {"log_data": f.read()})


def total_no_ionogramss(request, tx_code, id):
    conn = create_db_connection()
    data = total_no_ionograms(txcode=tx_code, conn=conn)
    print(data)
    return render(request, 'summary_of_all_ionograms.html', {"data": data, "tx_code": tx_code, "id": id})


def ionograms_details_from_summary(request, flag, id):
    conn = create_db_connection()
    data = Chripsounder.objects.filter(id=int(id)).values()[0]
    files = list(get_ionograms_after_summary(conn, flag))
    page = request.GET.get('page', 1)

    paginator = Paginator(files, 70)
    try:
        files = paginator.page(page)
    except PageNotAnInteger:
        files = paginator.page(1)
    except EmptyPage:
        files = paginator.page(paginator.num_pages)

    return render(request, 'ionograms-details.html', {"data": files, "id": id, "name": data})


def ionograms_details_from_summary_unfilltered(request, flag, id):
    conn = create_db_connection()
    data = Chripsounder.objects.filter(id=int(id)).values()[0]
    files = list(get_ionograms_after_summary(conn, flag, data['tx_code']))

    page = request.GET.get('page', 1)

    paginator = Paginator(files, 70)
    try:
        files = paginator.page(page)
    except PageNotAnInteger:
        files = paginator.page(1)
    except EmptyPage:
        files = paginator.page(paginator.num_pages)

    return render(request, 'ionograms_details_from_summary_unfilltered.html', {"data": files})
