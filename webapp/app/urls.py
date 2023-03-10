from django.urls import path
from . import views


urlpatterns = [
    path("", views.homepage, name='homepage'),
    path("unfilter_ionograms", views.unfiltered_ionograms, name='unfiltered_ionograms'),
    path("view_filtered_ionograms/<int:id>", views.view_filtered_ionograms, name='view_filtered_ionograms'),
    path("filter-ionograms/<str:folder_name>/<int:id>", views.filter_ionograms, name='ionograms_filter'),
    path("edit-transmitter/<int:id>", views.edit_transmitter, name='edit-transmitter'),
    path("edit-receiver/<int:id>", views.edit_receiver, name='edit_receiver'),
    path("receiver-info", views.receiver_info, name='receiver-info'),
    # path("filter_ionograms", views.filter_ionogramss, name='filter_ionograms'),
    path("create_ionograms/<str:filename>", views.create_ionograms, name='create_ionograms'),
    path("view-ionograms/<str:filename>", views.view_ionograms, name='view-ionograms'),
    path("view_unfiltered_ionograms/<str:folder_name>", views.view_unfiltered_ionograms, name='view_unfiltered_ionograms'),
    path("search_by_codes", views.search_by_codes, name='search_by_codes'),
] 
