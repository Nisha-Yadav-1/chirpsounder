import time
import json
from .global_url import rootdir
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
from .db import create_db_connection
    


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


def view_ionograms(request, filename, folder_name, id=None):
    """
    Functions to view filtered ionograms

    """
    conn = create_db_connection()
    data = Chripsounder.objects.get(id=id)
    files =  get_files_for_previous_next(conn, folder_name, data.tx_code)   
    files = [i[0] for i in files]
    h5_files = []
    png_files = []
    for file_name in files:
        if file_name.endswith("h5"):
            h5_files.append(file_name)
            png_files.append(f"{'.'.join(file_name.split('.')[0:2])}.png")
 

    filter_data = []
    for i in h5_files:
        
        png_file = i.split(".")[0: 2]
        if f"{'.'.join(png_file[0: 2])}.png" in png_files:
            filter_data.append(f"{'.'.join(png_file[0: 2])}.png")
    for_previous = []
    for_next = []


    index = filter_data.index(f"{'.'.join(filename.split('.')[0: 2])}.png")
    for_previous = filter_data[0: index]
    for_next = filter_data[index+1:]
    return render(request, 'view-ionograms.html', {"filename": filename, "for_previous": for_previous, "for_next": for_next, 'folder_name': folder_name})


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
        files = list(get_lfm_ionograms(conn, folder_name))
        if len(files) > 0:
            files = files
        else:
            filter_ionogram.creating_data_file(data, folder_name)
        files = list(get_lfm_ionograms_api(conn, folder_name))
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
    files = list(get_lfm_ionograms(conn, folder_name))
    if len(files) > 0:
        files = files
    else:
        filter_ionogram.creating_data_file(data, folder_name)
    files = list(get_lfm_ionograms(conn, folder_name))
    return render(request, 'filter_ionogram.html', {"data": files, "name": data, "date": folder_name, "id": id})


def edit_transmitter(request, tx_code, id):
    flag = 'edit_transmitter'
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
        # if flag == 'transmitter':
        return redirect(f'/')
    return render(request, 'edit.html', {"data": data[0], 'tx_code': tx_code, 'flag': flag})

def edit_filter_transmitter(request, tx_code, id):
    data = Chripsounder.objects.filter(id=id)
    context = {}
    flag = 'edit_filter_transmitter'
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
        return redirect(f'/ionograms-summary/{tx_code}/{id}')
    return render(request, 'edit.html', {"data": data[0], 'tx_code': tx_code, })


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




def filter_ionograms_by_tx_code(request, tx_code, id):

    conn = create_db_connection()


    folder = get_folder_date(conn, tx_code)


    flag = 'only_for_tx_code'
    logger.info('Message to display on console and UI')
    return render(request, 'view-filtered_ionogram.html', {"users": folder, 'flag': flag, "tx_code": tx_code, "id": id})




def view_ionograms_by_tx_code(request, tx_code, id):

    conn = create_db_connection()
    data = get_search_data(conn, tx_code, start_date=None, end_date=None)

    filter_data = {}
    if tx_code != 'Choose TX Code':
        filter_data.update(
            {
                "tx_code": tx_code

            }
        )
    return render(request, 'view-unfiltered_ionograms.html', {"data": data, "filtered_data": filter_data, "id": id})


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


def view_selected_data(request):
    conn = create_db_connection()
    st = []
    ed = []
    if request.method == 'POST':
        id = request.POST['id']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        data = view_selected_datas(conn, start_date, end_date)

        request.session['id'] = id
        request.session['start_date'] = start_date
        request.session['end_date'] = end_date

        page = request.GET.get('page', 1)

        paginator = Paginator(data, 400)
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)


        res =  render(request, 'view-filtered_ionogram.html', {"users": users, "id": id})
        res.set_cookie('id', id)
        res.set_cookie('start_date', start_date)
        res.set_cookie('end_date', end_date)

        return res
    

    else:

        id = request.COOKIES['id']
        start_date = request.COOKIES['start_date']
        end_date = request.COOKIES['end_date']

        data = view_selected_datas(conn, start_date, end_date)
        st.append(start_date)
        ed.append(end_date)
        page = request.GET.get('page', 1)

        paginator = Paginator(data, 400)
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        return render(request, 'view-filtered_ionogram.html', {"users": users, "id": id})





def view_unfiltered_ionograms(request, folder_name):
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
    return render(request, 'view-unfiltered_ionograms.html', {"data": data, 'selected_date': folder_name})


def search_by_codes(request):
    if request.method == 'POST':
        tx_code = request.POST['tx_code']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']

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

    return render(request, 'view-unfiltered_ionograms.html', {"data": data, "filtered_data": filter_data})


def loginfo(request):
    f = open(os.path.join(settings.BASE_DIR, 'info.log'), 'r')
    return render(request, 'log.html', {"log_data": f.read()})


def total_number_ionograms(request, tx_code, id):
    # Creating database connection
    conn = create_db_connection()
    data = total_no_ionograms(txcode=tx_code, conn=conn)
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



@api_view(['GET'])
def clear_classification(request):
    try:
        conn = create_db_connection()
        clearClassification(conn)
        return HttpResponse({"status": 200})
    except Exception as e:
        return HttpResponse({"status": 500})
    


def add_transmitter(request):
    flag = 'transmitter'
    transmitter = {}
    if request.method == 'POST':
        name_of_transmitter = request.POST['transmitter_name']
        tx_code = request.POST['tx_code']
        lat = request.POST['lat']
        long = request.POST['long']
        ground_range = request.POST['ground_range']
        receiver_code = request.POST['receiver_code']
        first_hop_range_one = request.POST['first_hop_range_one']
        first_hop_range_two = request.POST['first_hop_range_two']
        chriprate = request.POST['chrip_rate']
        second_hop_range_one = request.POST['second_hop_range_one']
        second_hop_range_two = request.POST['second_hop_range_two']

        if Chripsounder.objects.filter(tx_code=tx_code, deleted=False).exists():
            messages.error(request, "Transmitter already exist..")
            return render(request, 'add_transmitter.html', {"flag": flag})

        else:
            transmitter.update(
                {
                    "name_of_transmitter": name_of_transmitter,
                    "tx_code": tx_code,
                    "receiver_code": receiver_code,
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

            obj = Chripsounder(**transmitter)
            obj.save()
            return redirect('/')
    return render(request, 'add_transmitter.html', {"flag": flag})


def add_receiver(request):
    flag = 'receiver'
    receiver = {}
    if request.method == 'POST':
        receiver_name = request.POST['receiver_name']
        receiver_code = request.POST['receiver_code']
        receiver_location = request.POST['receiver_location']
        receiver_lat = request.POST['receiver_lat']
        receiver_long = request.POST['receiver_long']

        if ReceiverInfos.objects.filter(receiver_code=receiver_code, deleted=False).exists():
            messages.error(request, 'Receiver already exist...')
            return render(request, 'add_transmitter.html', {"flag": flag})

        else:
            messages.success(request, 'Receiver has been created successfully..')
            receiver.update(
                {
                    "receiver_name": receiver_name,
                    "receiver_code": receiver_code,
                    "receiver_location": receiver_location,
                    "receiver_lat": receiver_lat,
                    "receiver_long": receiver_long,
                }
            )
            obj = ReceiverInfos(**receiver)
            obj.save()
            return redirect('/receiver-info')
    return render(request, 'add_transmitter.html', {"flag": flag})


