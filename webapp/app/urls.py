from django.urls import path
from . import views


urlpatterns = [
    path("", views.homepage, name='homepage'),
    path("unfilter_ionograms/", views.unfiltered_ionograms, name='unfiltered_ionograms'),
    path("unfilter_ionograms/<str:tx_code>", views.filter_ionograms_by_tx_code,name='unfiltered_ionograms'),
    path("view_ionograms_by_tx_code/<str:tx_code>", views.view_ionograms_by_tx_code,name='view_ionograms_by_tx_code'),
    path("view_filtered_ionograms/<int:id>", views.view_filtered_ionograms, name='view_filtered_ionograms'),

    # api
    path("api/filter-ionograms/<str:folder_name>/<int:id>", views.filter_ionograms_api, name='ionograms_filter'),

    #url
    path("filter-ionograms/<str:folder_name>/<int:id>", views.filter_ionograms, name='ionograms_filter'),
    path("edit-transmitter/<int:id>", views.edit_transmitter, name='edit-transmitter'),
    path("edit-receiver/<int:id>", views.edit_receiver, name='edit_receiver'),
    path("receiver-info", views.receiver_info, name='receiver-info'),
    path("delete-receiver-info/<int:id>", views.delete_receiver_info, name='delete_receiver_info'),
    path("delete-chirp-sounder/<int:id>", views.delete_sounder, name='delete_sounder'),
    path("log", views.loginfo, name='loginfo'),
    # path("filter_ionograms", views.filter_ionogramss, name='filter_ionograms'),
    path("create_ionograms/<str:filename>", views.create_ionograms, name='create_ionograms'),
    path("view-ionograms/<str:filename>", views.view_ionograms, name='view-ionograms'),
    path("view_unfiltered_ionograms/<str:folder_name>", views.view_unfiltered_ionograms, name='view_unfiltered_ionograms'),
    path("search_by_codes", views.search_by_codes, name='search_by_codes'),

    
    path("ionograms-summary/<str:tx_code>/<int:id>", views.total_no_ionogramss, name='total_no_ionograms'),
    path("total-filtered-ionograms/<str:flag>/<int:id>", views.ionograms_details_from_summary, name='ionograms_details_from_summary'),
    path("total-ionograms/<str:flag>/<int:id>", views.ionograms_details_from_summary, name='ionograms_details_from_summary'),
    path("total-unfiltered-ionograms/<str:flag>/<int:id>", views.ionograms_details_from_summary_unfilltered, name='ionograms_details_from_summary_unfilltered'),
    # path('stream/', views.stream, name='stream')
    
] 
