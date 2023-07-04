from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View
from .models import *
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse, FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
from io import BytesIO
from django.db.models import Q


User =get_user_model()
def is_superuser(user):
    return user.is_superuser


def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['is_customer']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            user = form.save()
            if role:
                Client.objects.create(user=user, username=username, email=email)
            else:
                Supplier.objects.create(user=user, username=username, email=email)
            login(request, user)
            return redirect('login_view')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    msg = None
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                message = 'You have successfully logged in as an admin.'
                return HttpResponse(
                    f'<div style="background-color: #e6f7e9; color: #155724; padding: 10px;">{message}</div>'
                    f'<p>Redirecting to login page...</p>'
                    f'<script>setTimeout(function(){{window.location.href = "/admin2";}}, 1000);</script>')
            elif user is not None and user.is_customer:
                login(request, user)
                message = 'You have successfully logged in as client.'
                return HttpResponse(
                    f'<div style="background-color: #e6f7e9; color: #155724; padding: 10px;">{message}</div>'
                    f'<p>Redirecting to login page...</p>'
                    f'<script>setTimeout(function(){{window.location.href = "/customer";}}, 1000);</script>')
            elif user is not None and user.is_employee:
                login(request, user)
                message = 'You have successfully logged in as a suppplier.'
                return HttpResponse(
                    f'<div style="background-color: #e6f7e9; color: #155724; padding: 10px;">{message}</div>'
                    f'<p>Redirecting to login page...</p>'
                    f'<script>setTimeout(function(){{window.location.href = "/supplier";}}, 1000);</script>')
            else:
                msg = 'Check your credentials'
        else:
            msg = 'error validating form'
    return render(request, 'login.html', {'form': form, 'msg': msg})

@login_required
def logout(request):
    django_logout(request)
    message = 'You have successfully logged out.'
    return HttpResponse(
        f'<div style="background-color: #e6f7e9; color: #155724; padding: 10px;">{message}</div>'
        f'<p>Redirecting to login page...</p>'
        f'<script>setTimeout(function(){{window.location.href = "/login";}}, 1000);</script>')

def update_profile(request):
    if request.user.is_authenticated:
        User = get_user_model()
        current_user = User.objects.get(id=request.user.id)
        form = ProfileUpdateForm(request.POST or None, instance=current_user)
        return render(request, 'update_profile.html', {'form':form})
    else:
        messages.success(request, ("you must be logged in"))
        return redirect('home')

def create_event(request):
    if request.method == 'POST':
        form = EventsForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            decor_package = form.cleaned_data.get('decor_package')
            catering_package = form.cleaned_data.get('catering_package')
            videography_package = form.cleaned_data.get('videography_package')
            venue = form.cleaned_data.get('venue')

            existing_event = Events.objects.filter(
                Q(date=event.date) | Q(venue=venue)
            ).exclude(pk=event.pk).first()
            if existing_event:
                error_message = 'The selected date or venue has already been assigned to another event.'
                return render(request, 'create_event.html', {'form': form, 'error_message': error_message})

            total_price = 0
            if decor_package:
                total_price += decor_package.supplier.price

            if catering_package:
                total_price += catering_package.supplier.price

            if videography_package:
                total_price += videography_package.supplier.price

            if venue:
                total_price += venue.price

            event.total_price = total_price

            event.save()
            message = 'Event creation success'
            return HttpResponse(
                f'<div style="background-color: #e6f7e9; color: #155724; padding: 10px;">{message}</div>'
                f'<script>setTimeout(function(){{window.location.href = "/customer";}}, 1000);</script>')
    else:
        form = EventsForm()
    return render(request, 'create_event.html', {'form': form})

@login_required()
def event_update(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    if request.method == 'POST':
        form = EventsUpdateForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            message = 'Event Update Successfully!'
            return HttpResponse(
                f'<div style="background-color: #e6f7e9; color: #155724; padding: 10px;">{message}</div>'
                f'<script>setTimeout(function(){{window.location.href = "/customer";}}, 1000);</script>')
    else:
        form = EventsUpdateForm(instance=event)
    context = {'form': form, 'event': event}
    return render(request, 'event_detail_edit.html', context)
@login_required()
def event_delete(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    if request.method == 'POST':
        event.delete()
        message = 'Event delete success'
        return HttpResponse(
            f'<div style="background-color: #e6f7e9; color: #155724; padding: 10px;">{message}</div>'
            f'<script>setTimeout(function(){{window.location.href = "/customer";}}, 1000);</script>')
    context = {'event': event}
    return render(request, 'event_delete.html', context)

def customer(request):
    events = Events.objects.filter(user_id=request.user).order_by('-id')
    p = Paginator(events, 5)
    page = request.GET.get('page')
    pages = p.get_page(page)
    context = {'events': events, 'pages': pages}
    return render(request, 'cus_dashboard.html', context)

def supplier(request):
    return render(request, 'supplier_dashboard.html')
def view_customer(request):
    customers = Client.objects.all()
    context = {'customers': customers}
    return render(request, 'view_customer.html', context)

def customer_detail(request, customer_id):
    customer = get_object_or_404(Client, id=customer_id)
    context = {'customer': customer}
    return render(request, 'customer_detail.html', context)

def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    context = {'supplier': supplier}
    return render(request, 'supplier_detail.html', context)

def view_supplier(request):
    suppliers = Supplier.objects.all()
    context = {'suppliers': suppliers}
    return render(request, 'view_supplier.html', context)

def all_events(request):
    events = Events.objects.all()
    context = {'events':events}
    return render(request, 'all_events.html', context)

@login_required()
@user_passes_test(is_superuser)
def admin2(request):
    suppliers = Supplier.objects.all()
    clients = Client.objects.all()
    events = Events.objects.all()
    event_count = Events.objects.count()
    client_count = User.objects.filter(is_customer=True).count()
    supplier_count = User.objects.filter(is_employee=True).count()
    p = Paginator(events, 5)
    page = request.GET.get('page')
    pages = p.get_page(page)
    context = {'event_count': event_count, 'events': events,
               'client_count': client_count, 'supplier_count': supplier_count, 'pages': pages,
               'suppliers': suppliers, 'clients': clients}
    return render(request, 'admin_dashboard.html', context)

def messages(request):
    return render(request, 'messages.html')

class EventApprovalView(View):
    def post(self, request, event_id):
        event = get_object_or_404(Events, id=event_id)
        action = request.POST.get('action')
        if action == 'approve':
            event.status = 'Approved'
        elif action == 'reject':
            event.status = 'Rejected'
        event.save()
        return redirect('admin2')

def payment_view(request, event_id):
    event = Events.objects.get(pk=event_id)
    venue = event.venue
    packages = []
    venues = []

    if event.decor_package:
        packages.append(event.decor_package)
    if event.catering_package:
        packages.append(event.catering_package)
    if event.videography_package:
        packages.append(event.videography_package)

    if venue:
        venues.append(venue)

    total_price = event.total_price

    context = {
        'event': event,
        'packages': packages,
        'venues': venues,
        'total_price': total_price
    }

    if request.method == 'POST':
        card_number = request.POST.get('cardNumber')
        card_expiry = request.POST.get('cardExpiry')
        card_cvc = request.POST.get('cardCVC')
        payment_success = True

        if payment_success:
            event.status = 'paid'
            event.save()
            return render(request, 'payment_success.html')
        else:
            error_message = "Payment failed. Please try again."
            context['error_message'] = error_message
            return render(request, 'payments.html', context)
    else:
        return render(request, 'payments.html', context)

def reports_view(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)
    events = Events.objects.all()
    lines = []
    for event in events:
        lines.append(str(event.user.username))
        lines.append(event.name)
        if event.venue:
            lines.append(event.venue.name)
            lines.append(event.venue.locality)
        else:
            lines.append("No venue assigned")
            lines.append("")
        lines.append(str(event.attendees_expected))
        lines.append(str(event.total_price))
        lines.append("====================")
    for line in lines:
        textob.textLine(line)
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
    return FileResponse(buf, as_attachment=False, filename='report.pdf')

@login_required
def customer_report_view(request):
    user = request.user  # Get the current user
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)
    events = Events.objects.filter(user=user)
    lines = []
    for event in events:
        lines.append(str(event.user.username))
        lines.append(event.name)
        if event.venue:
            lines.append(event.venue.name)
            lines.append(event.venue.locality)
        else:
            lines.append("No venue assigned")
            lines.append("")
        lines.append(str(event.attendees_expected))
        lines.append(str(event.total_price))
        lines.append("====================")

    for line in lines:
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=False, filename='report.pdf')


def admin_users_report(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    logo_path = 'https://www.xpartsent.com/wp-content/uploads/2023/05/xparts-LOGO-1.png'
    logo = Image(logo_path, width=2 * inch, height=2 * inch)
    elements.append(logo)
    users = User.objects.all()
    data = [['Username', 'Roles']]
    for user in users:
        roles = ', '.join([role for role, value in user.__dict__.items() if value and role.startswith('is_')])
        data.append([user.username, roles])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table = Table(data)
    table.setStyle(style)
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='users_report.pdf')

def get_packages(event):
    packages = []
    if event.decor_package:
        packages.append(event.decor_package)
    if event.catering_package:
        packages.append(event.catering_package)
    if event.videography_package:
        packages.append(event.videography_package)
    return packages

def get_venues(event):
    venues = []
    if event.venue:
        venues.append(event.venue)
    return venues


def receipts_view(request, event_id):
    event = Events.objects.get(pk=event_id)
    venue = event.venue
    packages = []
    venues = []
    if event.decor_package:
        packages.append(event.decor_package)
    if event.catering_package:
        packages.append(event.catering_package)
    if event.videography_package:
        packages.append(event.videography_package)

    if venue:
        venues.append(venue)
    total_price = event.total_price
    context = {
        'event': event,
        'packages': packages,
        'venues': venues,
        'total_price': total_price
    }
    return render(request, 'receipt.html', context)


def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            return render(request, 'feedback_success.html')
    else:
        form = FeedbackForm()

    return render(request, 'feedback.html', {'form': form})

@login_required()
def venues(request):
    venues = Venue.objects.all()
    p = Paginator(venues, 8)
    page = request.GET.get('page')
    pages = p.get_page(page)
    template = 'venues.html'
    if request.user.is_superuser:
        template = 'admin_venues.html'
    context = {'venues': venues, 'pages': pages}
    return render(request, template, context)

def create_user(request):
    User = get_user_model()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = User(username=form.cleaned_data['username'])
            user.set_password(form.cleaned_data['password1'])
            user.save()
            user_type = form.cleaned_data['user_type']
            if user_type == 'customer':
                Client.objects.create(user=user)
            elif user_type == 'supplier':
                Supplier.objects.create(user=user)
            return redirect('admin2')
    else:
        form = UserCreationForm()
    client_count = User.objects.filter(is_customer=True).count()
    return render(request, 'create_user.html', {'form': form, 'client_count': client_count})

def delete_user(request, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('admin2')
    return render(request, 'user_delete.html', {'user': user})

def create_venue(request):
    if request.method == 'POST':
        form = VenueCreationForm(request.POST)
        if form.is_valid():
            event = form.save
            event.save()
            message = 'Event creation success'
            return HttpResponse(
                f'<div style="background-color: #e6f7e9; color: #155724; padding: 10px;">{message}</div>'
                f'<script>setTimeout(function(){{window.location.href = "/customer";}}, 1000);</script>')
    else:
        form = VenueCreationForm()
    return render(request, 'add_venue.html', {'form': form})

def view_feedback(request):
    feedbacks = Feedback.objects.all()
    context = {'feedbacks': feedbacks}
    return render(request, 'view_feedback.html', context)
