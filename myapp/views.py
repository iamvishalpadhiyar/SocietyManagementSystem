from asyncio import events
from urllib import request
from django.http.response import HttpResponse
from django.shortcuts import render,redirect
from .models import *
from random import choices, randrange
from django.conf import settings
from django.core.mail import send_mail
from userapp.models import *
from datetime import datetime
from django.core.mail import send_mail, BadHeaderError
from smtplib import SMTPException# as smtpLibException  # To avoid naming conflict with Django's SMTPException
import pandas as pd
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import render_to_string
from django.db.models import Q

# Create your views here.
def login(request):
    if request.method == 'POST':
        try:
            uid = SecUser.objects.get(email=request.POST['email'])
            if request.POST['password'] == uid.password:
                request.session['email'] = request.POST['email']
                return redirect('index')
            else:
                return render(request,'login.html',{'msg':'Wrong Password'})
        except:
            return render(request,'login.html',{'msg':'Wrong Email'})
    return render(request,'login.html')

def index(request):
    uid = SecUser.objects.get(email=request.session['email'])
    tmember = Addmember.objects.all().count()
    tevent = Event.objects.all().count()
    tcomplain = Complain.objects.all().count()
    tnotice = Notice.objects.all().count()
    complains = Complain.objects.all()[::-1][:4]
    mpay = Pay.objects.all()[::-1][:4]
    return render(request,'index.html',{'uid':uid,'mpay':mpay,'complains':complains,'tmember':tmember,'tevent':tevent,'tcomplain':tcomplain,'tnotice':tnotice})


# def register(request):
#     if request.method == 'POST':
#         try:
#             if SecUser.objects.filter(email=request.POST['email']):#  if SecUser.objects.all(email=request.POST['email']):
#                 return render(request,'register.html',{'msg':'Email is already register'})
#         except:
#             otp = randrange(1111,9999)
#             subject = 'Welcome to Soc Management App'
#             message = f"""Hello {request.POST['name']}!!
#             Your Verification OTP is : {otp}.
#             """
#             email_from = settings.EMAIL_HOST_USER
#             recipient_list = [request.POST['email']]
#             send_mail( subject, message, email_from, recipient_list )
#             global temp
#             temp = {
#                 'name' : request.POST['name'],
#                 'email' : request.POST['email'],
#                 'mobile' : request.POST['mobile'],
#                 'password' : request.POST['password'],
#             }
#             return render(request,'otp.html',{'otp':otp})

#     else:
#         return render(request,'register.html')
def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        existing_user = SecUser.objects.filter(email=email).exists()

        if existing_user:
            # Email already registered
            return render(request, 'register.html', {'msg': 'Email is already registered'})

        try:
            # Generate OTP and send email
            otp = randrange(1111, 9999)
            subject = 'Welcome to Soc Management App'
            message = f"Hello {request.POST['name']}!!\nYour Verification OTP is: {otp}."
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list)

            # Store user data in session instead of a global variable
            request.session['temp_user_data'] = {
                'name': request.POST['name'],
                'email': email,
                'mobile': request.POST['mobile'],
                'password': request.POST['password'],  # Hashing the password
            }
            return render(request, 'otp.html', {'otp': otp})

        # except Exception as e:
        #     # Handle email sending failure or any other exceptions
        #     print(f"Error sending email: {e}")  # Log the exception or handle it as needed
        #     return render(request, 'register.html', {'msg': 'Error in sending OTP. Please try again.'})
        except BadHeaderError:
             # Specific exception for bad email headers
             print("Bad Header Error")
             return render(request, 'register.html', {'msg': 'Invalid header found.'})

        except SMTPException:
            # Handles general email sending errors within Django
            print("SMTPException occurred")
            return render(request, 'register.html', {'msg': 'SMTP error occurred. Please try again.'})

        # except smtpLibException:
        #     # Handles lower-level SMTP errors
        #     print("smtplib SMTPException occurred")
        #     return render(request, 'register.html', {'msg': 'SMTP error occurred. Please try again.'})

        except Exception as e:
            # Catch-all for any other exception
            print(f"Other error: {e}")
            return render(request, 'register.html', {'msg': 'An error occurred. Please try again.'})
    else:
        # Handle GET request
        return render(request, 'register.html')

def otp(request):
    if request.method == 'POST':
        if request.POST['otp'] == request.POST['uotp']:
            # Access user data from the session
            user_data = request.session.get('temp_user_data')

            if user_data:
                # Create a new SecUser object using the session data
                SecUser.objects.create(
                    name=user_data['name'],
                    email=user_data['email'],
                    mobile=user_data['mobile'],
                    password=user_data['password']
                )
                # Clear the data from the session after use
                del request.session['temp_user_data']

                msg = 'User created'
                return render(request, 'login.html', {'msg': msg})
            else:
                # Handle cases where session data is not found
                return render(request, 'register.html', {'msg': 'Session expired. Please register again.'})

        else:
            msg = 'Incorrect OTP'
            return render(request, 'otp.html', {'otp': request.POST['otp'], 'msg': msg})
# def otp(request):
#     if request.method == 'POST':
#         if request.POST['otp'] == request.POST['uotp']:
#             global temp
#             SecUser.objects.create(
#                 name = temp['name'],
#                 email = temp['email'],
#                 mobile = temp['mobile'],
#                 password = temp['password']
#             )
#             del temp
#             msg = 'User created'
#             return render(request,'login.html',{'msg':msg})
#         else:
#             msg = 'Incorrect OTP'
#             return render(request,'otp.html',{'otp':request.POST['otp'],'msg':msg})

def fpassword(request):
    if request.method == 'POST':
        try:
            uid = SecUser.objects.get(email=request.POST['email'])
            s = ''.join(choices('abcqwertyuiioplkjhgfdsazxcvbnm9876543321',k=8))
            subject = 'Password has been reset'
            message = f"""Hello user your new password is : {s}
            """
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [request.POST['email']]
            send_mail( subject, message, email_from, recipient_list )
            uid.password = s
            uid.save()
            return render(request,'login.html',{'msg':subject})
        except:
            msg = 'User IS Not Registered'
            return render(request,'login.html',{'msg':msg})
    return render(request,'fpassword.html')

def profile(request):
    uid = SecUser.objects.get(email=request.session['email'])
    if request.method == 'POST':
       uid.name = request.POST['name']
       uid.email = request.POST['email']
       uid.mobile = request.POST['mobile']
       uid.address = request.POST['address']
       uid.city = request.POST['city']
       uid.pincode = request.POST['pincode']
       uid.save()

    return render(request,'profile.html',{'uid':uid})


def tables(request):
    uid = SecUser.objects.get(email=request.session['email'])
    payd = Pay.objects.all()[::-1]

    return render(request,'tables.html',{'uid':uid,'payd':payd})

def maintenance_report(request):
    member = list(Addmember.objects.all().prefetch_related("pay_set").values("id","name","pay__pamount","pay__pdate","pay__ptime"))
    print("member", member)
    return render(request,'maintenance_report.html',{"member":member})

def export_maintenance_report(request):
    member = list(Addmember.objects.all().prefetch_related("pay_set").values("name","pay__pamount","pay__pdate","pay__ptime"))
    new_data = []
    for data in member:
        new_data.append({
            "MEMBER":data["name"],
            "MAINTENANCE MONTH":str(datetime.strptime(str(data["pay__pdate"]), "%Y-%m-%d").strftime("%B %d, %Y")) if data["pay__pdate"] else "",
            "PAY AMOUNT":data["pay__pamount"] if data["pay__pamount"] else "",
            "PAY TIME":str(datetime.strptime(str(data["pay__ptime"]), "%Y-%m-%d %H:%M:%S.%f%z").strftime("%b. %d, %Y, %I:%M %p")) if data["pay__ptime"] else "",
            "STATUS":"Paid" if data["pay__pamount"] else "Unpaid"
        })

    maintenance_report = pd.DataFrame(new_data)
    response = HttpResponse(content_type="application/xlsx")
    response['Content-Disposition'] = 'attachment; filename="Maintenance Report.xlsx"'
    row = 2
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        maintenance_report.to_excel(writer, sheet_name="Maintenance report", index=False, startrow=row, startcol=0)
        workbook = writer.book
        worksheet = writer.sheets['Maintenance report']
        worksheet.merge_range('A1:E1', 'Maintenance Report', workbook.add_format({'align': 'center', 'valign': 'vcenter','bold': True, 'font_size': 16}))

    writer.sheets['Maintenance report'].set_tab_color('green')
    return response

def export_maintenance_report_pdf(request):
    member = list(Addmember.objects.all().prefetch_related("pay_set").values("id","name","pay__pamount","pay__pdate","pay__ptime"))
    html_content =render_to_string("maintenance_report.html", {"member":member},request).split('<div class="table-responsive">')[1].split('<p class="end_of_table"></p>')[0]
    style= """
        .table-flush{ border:1px solid black;}
        .table-flush>thead>tr{ background-color:#5e72e4; color:black; margin-top:2px;}
        .table-flush th, .table-flush td{padding-top: 8px;text-align:center }
    """
    final_html = f"<html><head><style>{style}</style></head><body>{html_content}</body></html>"
    response_html = final_html.replace("₹","Rs.")
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(response_html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(),status=200, content_type='application/pdf')
    return HttpResponse(None, status=500)

import json
def filter_maintenance_report_data(request):
    paid = request.POST.get("paid")
    print("paid", paid)
    unpaid = request.POST.get("unpaid")
    print("unpaid", unpaid)
    query = Q()
    if paid == "true":
        query.add(Q(pay__pamount__isnull=False), query.connector )
    if unpaid == "true":
        query.add(Q(pay__pamount__isnull=True), query.connector )
    if paid == 'true' and unpaid == 'true':
        query = Q()
    print("query", query)
    member = list(Addmember.objects.prefetch_related("pay_set").filter(query).values("name","pay__pamount","pay__pdate","pay__ptime"))
    print("member", member)
    new_data = []
    for data in member:
        new_data.append({
            "name":data["name"],
            "pay__pdate":str(datetime.strptime(str(data["pay__pdate"]), "%Y-%m-%d").strftime("%B %d, %Y")) if data["pay__pdate"] else "",
            "pay__pamount":data["pay__pamount"] if data["pay__pamount"] else "",
            "pay__ptime":str(datetime.strptime(str(data["pay__ptime"]), "%Y-%m-%d %H:%M:%S.%f%z").strftime("%b. %d, %Y, %I:%M %p")) if data["pay__ptime"] else "",
            "status":"Paid" if data["pay__pamount"] else "Unpaid"
        })
    return HttpResponse(json.dumps({"data":new_data}))



def complains_report(request):
    complains = Complain.objects.all()
    return render(request,'complains_report.html',{"complains":complains})

def export_complains_report(request):
    complain = Complain.objects.all()
    new_data = []
    for data in complain:
        new_data.append({
            "COMPLAIN TITLE":data.ctitle,
            "COMPLAIN BY":data.cby.name,
            "COMPLAIN TYPE":data.ctypes,
            "COMPLAIN DATE":str(datetime.strptime(str(data.ctime), "%Y-%m-%d %H:%M:%S.%f%z").strftime("%b. %d, %Y, %I:%M %p")) if data.ctime else "",
            "COMPLAIN STATUS":"Solve" if data.status else "Pending",
        })

    maintenance_report = pd.DataFrame(new_data)
    response = HttpResponse(content_type="application/xlsx")
    response['Content-Disposition'] = 'attachment; filename="Complains Report.xlsx"'
    row = 2
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        maintenance_report.to_excel(writer, sheet_name="Complains report", index=False, startrow=row, startcol=0)
        workbook = writer.book
        worksheet = writer.sheets['Complains report']
        worksheet.merge_range('A1:E1', 'Complains Report', workbook.add_format({'align': 'center', 'valign': 'vcenter','bold': True, 'font_size': 16}))

    writer.sheets['Complains report'].set_tab_color('green')
    return response

def export_complains_report_pdf(request):
    complains = Complain.objects.all()
    html_content =render_to_string("complains_report.html", {"complains":complains},request).split('<div class="table-responsive">')[1].split('<p class="end_of_table"></p>')[0]
    style= """
        .table-flush{ border:1px solid black;}
        .table-flush>thead>tr{ background-color:#5e72e4; color:black; margin-top:2px;}
        .table-flush th, .table-flush td{padding-top: 8px;text-align:center }
    """
    final_html = f"<html><head><style>{style}</style></head><body>{html_content}</body></html>"
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(final_html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(),status=200, content_type='application/pdf')
    return HttpResponse(None, status=500)


def event_report(request):
    events = Event.objects.all()
    return render(request,'event_report.html',{"events":events})

def export_event_report(request):
    events = Event.objects.all()
    new_data = []
    for data in events:
        new_data.append({
            "EVENT TITLE":data.title,
            "EVENT DATE":str(datetime.strptime(str(data.event_at),  "%Y-%m-%d").strftime("%B %d, %Y")) if data.event_at else "",
            "POSTED BY":data.uid.name,
            "DESCRIPTION":data.des,
        })

    maintenance_report = pd.DataFrame(new_data)
    response = HttpResponse(content_type="application/xlsx")
    response['Content-Disposition'] = 'attachment; filename="Event Report.xlsx"'
    row = 2
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        maintenance_report.to_excel(writer, sheet_name="Event report", index=False, startrow=row, startcol=0)
        workbook = writer.book
        worksheet = writer.sheets['Event report']
        worksheet.merge_range('A1:D1', 'Event Report', workbook.add_format({'align': 'center', 'valign': 'vcenter','bold': True, 'font_size': 16}))

    writer.sheets['Event report'].set_tab_color('green')
    return response


def export_event_report_pdf(request):
    events = Event.objects.all()
    html_content =render_to_string("event_report.html", {"events":events},request).split('<div class="table-responsive">')[1].split('<p class="end_of_table"></p>')[0]
    style= """
        .table-flush{ border:1px solid black;}
        .table-flush>thead>tr{ background-color:#5e72e4; color:black; margin-top:2px;}
        .table-flush th, .table-flush td{padding-top: 8px;text-align:center }
    """
    final_html = f"<html><head><style>{style}</style></head><body>{html_content}</body></html>"
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(final_html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(),status=200, content_type='application/pdf')
    return HttpResponse(None, status=500)

def logout(request):
    del request.session['email']
    return redirect('login')

def add_event(request):
    uid = SecUser.objects.get(email=request.session['email'])
    if request.method == 'POST':
        if 'pic' in request.FILES:
            Event.objects.create(
                uid = uid,
                title = request.POST['title'],
                des = request.POST['des'],
                pic = request.FILES['pic'],
                event_at = request.POST['date']
            )
        else:
            Event.objects.create(
                uid = uid,
                title = request.POST['title'],
                des = request.POST['des'],
                event_at = request.POST['date']
            )
        msg = 'Event Created'
        return render(request,'add-event.html',{'uid':uid,'msg':msg})

    return render(request,'add-event.html',{'uid':uid})

def all_event(request):
    uid = SecUser.objects.get(email=request.session['email'])
    events = Event.objects.all()[::-1]
    return render(request,'all-event.html',{'uid':uid,'events':events})

def delete_event(request,pk):
    event = Event.objects.get(id=pk)
    event.delete()
    return redirect('all-event')


def edit_event(request,pk):
    event = Event.objects.get(id=pk)
    event_at = str(event.event_at)
    uid = SecUser.objects.get(email=request.session['email'])
    if request.method == 'POST':
        event.uid = uid
        event.title = request.POST['title']
        event.des = request.POST['des']
        event.event_at = request.POST['date']
        if 'pic' in request.FILES:
            event.pic = request.FILES['pic']
        event.save()

        return redirect('all-event')
    return render(request,'edit-event.html',{'uid':uid, 'event':event,'event_at':event_at})


def change_password(request):
    uid = SecUser.objects.get(email=request.session['email'])
    if request.method == 'POST':
        if request.POST['oldpassword'] == uid.password:
            if request.POST['newpassword'] == request.POST['cpassword']:
                uid.password = request.POST['newpassword']
                uid.save()

                return render(request,'changepassword.html',{'msg':'Password Has been Changed'})
            return render(request,'changepassword.html',{'Both new passwords are not same'})
        return render(request,'changepassword.html',{'msg':'Old password is wrong'})
    return render(request,'changepassword.html',{'uid':uid})

def view_complain(request):
    uid = SecUser.objects.get(email=request.session['email'])
    complains = Complain.objects.all()[::-1]
    return render(request,'view-complain.html',{'complains':complains,'uid':uid})


def addmember(request):
    uid = SecUser.objects.get(email=request.session['email'])
    if request.method == 'POST':
        try:
            if 'pic' in request.FILES:
                Addmember.objects.create(

                    name = request.POST['name'],
                    email = request.POST['email'],
                    mobile = request.POST['mobile no'],
                    password = request.POST['password'],
                    flat= request.POST['flat'],
                    address = request.POST['address'],
                    adharcard = request.POST['adharcard'],
                    pic = request.FILES['pic'],
                )
            else:
                    Addmember.objects.create(
                    name = request.POST['name'],
                    email = request.POST['email'],
                    mobile = request.POST['mobile no'],
                    password = request.POST['password'],
                    flat= request.POST['flat'],
                    address = request.POST['address'],
                    adharcard = request.POST['adharcard'],
                )

            msg = 'Member Added'
        except:
            msg = 'Member is already register this email'
        return render(request,'addmember.html',{'msg':msg,'uid':uid})
    return render(request,'addmember.html',{'uid':uid})


def viewdetails(request,pk):
    uid = SecUser.objects.get(email=request.session['email'])
    complains = Complain.objects.get(id=pk)
    return render(request,'view-details.html',{'uid':uid,'complains':complains})


def delete_complain(request,pk):
    complains = Complain.objects.get(id=pk)
    complains.delete()
    return redirect('view-complain')


def solve(request,pk):
    complain = Complain.objects.get(id=pk)
    uid = SecUser.objects.get(email=request.session['email'])
    complain.status = True
    complain.solveby = uid
    complain.solvetime = datetime.now()
    complain.save()
    return redirect('view-complain')


def eventdetails(request,pk):
    uid = SecUser.objects.get(email=request.session['email'])
    events = Event.objects.get(id=pk)
    return render(request,'event-details.html',{'uid':uid,'event':events})


def gallery(request):
    uid = SecUser.objects.get(email=request.session['email'])
    if request.method == 'POST':
        Gallery.objects.create(
            gby = uid,
            gtype = request.POST['gtype'],
            gpic = request.FILES['gpic'],
        )

        msg = 'Image Added'
        return render(request,'gallery.html',{'msg':msg,'uid':uid})
    return render(request,'gallery.html',{'uid':uid})


def addnotice(request):
    uid = SecUser.objects.get(email=request.session['email'])
    if request.method == 'POST':
            Notice.objects.create(
                ntype = request.POST['ntype'],
                ntitle = request.POST['ntitle'],
                ndes = request.POST['ndes'],
                nsendby = uid
            )
            msg = 'Notice Created'
            return render(request,'add-notice.html',{'uid':uid,'msg':msg})
    return render(request,'add-notice.html',{'uid':uid})

def all_notice(request):
    uid = SecUser.objects.get(email=request.session['email'])
    notices = Notice.objects.all()[::-1]
    return render(request,'all-notice.html',{'uid':uid,'notices':notices})

