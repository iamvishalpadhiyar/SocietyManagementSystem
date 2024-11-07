from django.urls import path
from . import views

urlpatterns = [
    path('',views.login,name='login'),
    path ('index',views.index,name='index'),
    path('register/',views.register,name='register'),
    path('otp/',views.otp,name='otp'),
    path('fpassword/',views.fpassword,name='fpassword'),
    path('profile/',views.profile,name='profile'),
    path('maintenance/',views.tables,name='tables'),
    path('logout/',views.logout,name='logout'),
    path('add-event/',views.add_event,name='add-event'),
    path('all-event/',views.all_event,name='all-event'),
    path('edit-event/<int:pk>',views.edit_event,name='edit-event'),
    path('delete-event/<int:pk>',views.delete_event,name='delete-event'),
    path('change-password/',views.change_password,name='change-password'),
    path('view-complain/',views.view_complain,name='view-complain'),
    path('addmember/',views.addmember,name='addmember'),
    path('view-details/<int:pk>',views.viewdetails,name='view-details'),
    path('delete-complain/<int:pk>',views.delete_complain,name='delete-complain'),
    path('solve/<int:pk>',views.solve,name='solve'),
    path('event-details/<int:pk>',views.eventdetails,name='event-details'),
    path('gallery/',views.gallery,name='gallery'),
    path('add-notice/',views.addnotice,name='add-notice'),
    path('All-notice/',views.all_notice,name='all-notice'),
    path('maintenance_report/' ,views.maintenance_report, name="maintenance_report"),
    path('export_maintenance_report/' ,views.export_maintenance_report, name="export_maintenance_report"),
    path('filter_maintenance_report_data/' ,views.filter_maintenance_report_data, name="filter_maintenance_report_data"),
    path('export_maintenance_report_pdf/' ,views.export_maintenance_report_pdf, name="export_maintenance_report_pdf"),
    path('complains_report/' ,views.complains_report, name="complains_report"),
    path('export_complains_report/' ,views.export_complains_report, name="export_complains_report"),
    path('export_complains_report_pdf/' ,views.export_complains_report_pdf, name="export_complains_report_pdf"),
    path('event_report/' ,views.event_report, name="event_report"),
    path('export_event_report/' ,views.export_event_report, name="export_event_report"),
    path('export_event_report_pdf/' ,views.export_event_report_pdf, name="export_event_report_pdf"),







]