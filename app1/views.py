from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import employeedata
from .forms import AppointmentForm
from .models import Advocate
from .models import Appointment
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta,date
from django.core.paginator import Paginator

# Create your views here.
@login_required(login_url='login')
def home(request):
    employeesf = employeedata.objects.all()
    return render(request, 'home.html', {'employeesf':employeesf })
    # return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            return HttpResponse("Passwords do not match")

        # Create the user
        userlist = User.objects.create_user(username=uname, email=email, password=pass1)
        userlist.save()

        # Create associated Advocate with default specialization "General"
        advocate = Advocate.objects.create(
            user=userlist,
            name=uname,
            specialization="General"
        )

        return redirect('login')

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')

        user = authenticate(request, username=username, password=pass1)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("Error: check username or password")

    return render(request, 'login.html')

def employees(request):
  
    return render(request, 'employee.html')

def delete(request, id):
    empd = employeedata.objects.get(id=id)
    empd.delete()
    return redirect ('home')

def update(request, id):
    empd = employeedata.objects.get(id=id)
    return render(request, 'update.html', {'empd': empd})


def updaterec(request, id):
    if request.method == 'POST':
        empd = employeedata.objects.get(id=id)
        empd.fname = request.POST['fname']
        empd.lname = request.POST['lname']
        empd.phone = request.POST['phone']
        empd.amount = request.POST['amount']
        empd.save()
        return redirect('home')
    else:
        return redirect('home')


def addemployee(request):
    if request.method == 'POST':
        x = request.POST.get('fname')
        y = request.POST.get('lname')
        z = request.POST.get('phone')
        s = request.POST.get('amount')

        employeedata.objects.create(fname=x, lname=y, phone=z, amount=s)
        return redirect('home')
    else:
        return render(request, 'employee.html')  # render the form

def calculate_scale_fee(amount):
    description = ""
    fee = 0

    if amount <= 5_000_000:
        fee = max(amount * 0.02, 35_000)
        description = f"Since amount is ≤ 5,000,000:<br>Fee = max(2% of {amount:,}, 35,000) = Kshs {fee:,.2f}"
    elif amount <= 100_000_000:
        base = max(5_000_000 * 0.02, 35_000)
        extra = (amount - 5_000_000) * 0.015
        fee = base + extra
        description = f"""First Kshs 5,000,000 @ 2% = {base:,.2f}<br>
        Remaining {amount - 5_000_000:,.2f} @ 1.5% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""
    elif amount <= 250_000_000:
        base = max(5_000_000 * 0.02, 35_000)
        tier2 = (100_000_000 - 5_000_000) * 0.015
        extra = (amount - 100_000_000) * 0.0125
        fee = base + tier2 + extra
        description = f"""First 5M @ 2% = {base:,.2f}<br>
        Next 95M @ 1.5% = {tier2:,.2f}<br>
        Remaining {amount - 100_000_000:,.2f} @ 1.25% = {extra:,.2f}<br>
        Total = { fee:,.2f}"""
    elif amount <= 1_000_000_000:
        base = max(5_000_000 * 0.02, 35_000)
        tier2 = (100_000_000 - 5_000_000) * 0.015
        tier3 = (250_000_000 - 100_000_000) * 0.0125
        extra = (amount - 250_000_000) * 0.01
        fee = base + tier2 + tier3 + extra
        description = f"""5M @ 2% = {base:,.2f}<br>
        95M @ 1.5% = {tier2:,.2f}<br>
        150M @ 1.25% = {tier3:,.2f}<br>
        Remaining {amount - 250_000_000:,.2f} @ 1% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""
    else:
        base = max(5_000_000 * 0.02, 35_000)
        tier2 = (100_000_000 - 5_000_000) * 0.015
        tier3 = (250_000_000 - 100_000_000) * 0.0125
        tier4 = (1_000_000_000 - 250_000_000) * 0.01
        extra = (amount - 1_000_000_000) * 0.001
        fee = base + tier2 + tier3 + tier4 + extra
        description = f"""5M @ 2% = {base:,.2f}<br>
        95M @ 1.5% = {tier2:,.2f}<br>
        150M @ 1.25% = {tier3:,.2f}<br>
        750M @ 1% = {tier4:,.2f}<br>
        Remaining {amount - 1_000_000_000:,.2f} @ 0.1% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""

    return fee, description

def scale_fee_view(request):
    fee = None
    description = ""
    amount = None

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            fee, description = calculate_scale_fee(amount)
        except (ValueError, TypeError):
            description = "Invalid input. Please enter a valid number."

    return render(request, 'scale_fee.html', {
        'fee': fee,
        'amount': amount,
        'description': description
    })


def calculate_grantee_fee(amount):
    description = ""
    fee = 0

    if amount <= 2_500_000:
        fee = max(amount * 0.02, 28_000)
        description = f"Amount ≤ 2,500,000:<br>Fee = max(2% of {amount:,.2f}, 28,000) = {fee:,.2f}"
    elif amount <= 5_000_000:
        base = max(2_500_000 * 0.02, 28_000)
        extra = (amount - 2_500_000) * 0.0175
        fee = base + extra
        description = f"""First 2.5M @ 2% = {base:,.2f}<br>
        Next {amount - 2_500_000:,.2f} @ 1.75% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""
    elif amount <= 100_000_000:
        base = max(2_500_000 * 0.02, 28_000)
        tier2 = (5_000_000 - 2_500_000) * 0.0175
        extra = (amount - 5_000_000) * 0.01
        fee = base + tier2 + extra
        description = f"""2.5M @ 2% = {base:,.2f}<br>
        2.5M @ 1.75% = {tier2:,.2f}<br>
        Remaining {amount - 5_000_000:,.2f} @ 1% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""
    elif amount <= 250_000_000:
        base = max(2_500_000 * 0.02, 28_000)
        tier2 = (5_000_000 - 2_500_000) * 0.0175
        tier3 = (100_000_000 - 5_000_000) * 0.01
        extra = (amount - 100_000_000) * 0.0075
        fee = base + tier2 + tier3 + extra
        description = f"""2.5M @ 2% = {base:,.2f}<br>
        2.5M @ 1.75% = {tier2:,.2f}<br>
        95M @ 1% = {tier3:,.2f}<br>
        Remaining {amount - 100_000_000:,.2f} @ 0.75% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""
    elif amount <= 1_000_000_000:
        base = max(2_500_000 * 0.02, 28_000)
        tier2 = (5_000_000 - 2_500_000) * 0.0175
        tier3 = (100_000_000 - 5_000_000) * 0.01
        tier4 = (250_000_000 - 100_000_000) * 0.0075
        extra = (amount - 250_000_000) * 0.0015
        fee = base + tier2 + tier3 + tier4 + extra
        description = f"""2.5M @ 2% = {base:,.2f}<br>
        2.5M @ 1.75% = {tier2:,.2f}<br>
        95M @ 1% = {tier3:,.2f}<br>
        150M @ 0.75% = {tier4:,.2f}<br>
        Remaining {amount - 250_000_000:,.2f} @ 0.15% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""
    else:
        base = max(2_500_000 * 0.02, 28_000)
        tier2 = (5_000_000 - 2_500_000) * 0.0175
        tier3 = (100_000_000 - 5_000_000) * 0.01
        tier4 = (250_000_000 - 100_000_000) * 0.0075
        tier5 = (1_000_000_000 - 250_000_000) * 0.0015
        extra = (amount - 1_000_000_000) * 0.001
        fee = base + tier2 + tier3 + tier4 + tier5 + extra
        description = f"""2.5M @ 2% = {base:,.2f}<br>
        2.5M @ 1.75% = {tier2:,.2f}<br>
        95M @ 1% = {tier3:,.2f}<br>
        150M @ 0.75% = {tier4:,.2f}<br>
        750M @ 0.15% = {tier5:,.2f}<br>
        Remaining {amount - 1_000_000_000:,.2f} @ 0.1% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""

    return fee, description


def grantee_fee_view(request):
    fee = None
    description = ""
    amount = None

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            fee, description = calculate_grantee_fee(amount)
        except (ValueError, TypeError):
            description = "Invalid input. Please enter a valid number."

    return render(request, 'grantee_fee.html', {
        'fee': fee,
        'amount': amount,
        'description': description
    })

def combined_fee_view(request):
    fee = None
    description = ""
    amount = None
    selected_type = ""

    if request.method == 'POST':
        selected_type = request.POST.get('fee_type')
        try:
            amount = float(request.POST.get('amount'))
            if selected_type == "general":
                fee, description = calculate_scale_fee(amount)

                description = "General legal scale fee based on transaction value."
            elif selected_type == "grantee":
                fee, description = calculate_grantee_fee(amount)
        except (ValueError, TypeError):
            description = "Invalid input. Please enter a valid number."

    return render(request, 'combined_fee.html', {
        'fee': fee,
        'amount': amount,
        'description': description,
        'selected_type': selected_type,
    })


def legal_scale_fee_calculator(request):
    fee = None
    description = ""
    selected_type = ""
    amount = 0.0

    if request.method == 'POST':
        selected_type = request.POST.get('fee_type')
        try:
            amount = float(request.POST.get('amount'))
        except ValueError:
            # Handle invalid amount input
            fee = None
            description = "Invalid amount entered."

        # Perform the calculations based on the selected fee type
        if selected_type == 'land_sale':
            fee, description = calculate_scale_fee(amount)
        elif selected_type == 'create_grantee':
            fee, description = calculate_create_grantee_fee(amount)
        elif selected_type == 'discharge_grantee_with':
            fee, description = calculate_discharge_grantee_with_fee(amount)
        elif selected_type == 'discharge_grantee_without':
            fee, description = calculate_discharge_grantee_without_fee(amount)
        elif selected_type == 'create_grantor':
            fee, description = calculate_create_grantor_fee(amount)
        elif selected_type == 'discharge_grantor':
            fee, description = calculate_discharge_grantor_fee(amount)

    return render(request, 'legal_scale_fee_calculator.html', {
        'fee': fee,
        'description': description,
        'selected_type': selected_type,
        'amount': amount
    })


def calculate_land_sale_fee(amount):
    # Scale fee calculation for Land Sale/Purchase
    if amount <= 5000000:
        fee = max(0.02 * amount, 35000)
        description = f"2% of Ksh {amount} or Ksh 35,000 whichever is higher: Ksh {fee}"
    elif amount <= 100000000:
        fee = max(0.02 * 5000000, 35000) + 0.015 * (amount - 5000000)
        description = f"2% of Ksh 5,000,000 + 1.5% of the balance above Ksh 5,000,000: Ksh {fee}"
    elif amount <= 250000000:
        fee = (max(0.02 * 5000000, 35000) + 0.015 * (100000000 - 5000000)) + 0.0125 * (amount - 100000000)
        description = f"2% of Ksh 5,000,000 + 1.5% of the next Ksh 95,000,000 + 1.25% of the balance above Ksh 100,000,000: Ksh {fee}"
    elif amount <= 1000000000:
        fee = (max(0.02 * 5000000, 35000) + 0.015 * (100000000 - 5000000)) + 0.0125 * (250000000 - 100000000) + 0.01 * (
                    amount - 250000000)
        description = f"2% of Ksh 5,000,000 + 1.5% of the next Ksh 95,000,000 + 1.25% of the next Ksh 150,000,000 + 1% of the balance above Ksh 250,000,000: Ksh {fee}"
    else:
        fee = (max(0.02 * 5000000, 35000) + 0.015 * (100000000 - 5000000)) + 0.0125 * (250000000 - 100000000) + 0.01 * (
                    1000000000 - 250000000) + 0.001 * (amount - 1000000000)
        description = f"2% of Ksh 5,000,000 + 1.5% of the next Ksh 95,000,000 + 1.25% of the next Ksh 150,000,000 + 1% of the next Ksh 750,000,000 + 0.1% of the balance above Ksh 1,000,000,000: Ksh {fee}"
    return fee, description


def calculate_create_grantee_fee(amount):
    fee = 0
    description = ""

    if amount <= 2_500_000:
        fee = max(0.02 * amount, 28_000)
        description = f"Since amount is ≤ Kshs 2,500,000:<br>Fee = max(2% of {amount:,.2f}, 28,000) = Kshs {fee:,.2f}"
    elif amount <= 5_000_000:
        base = max(0.02 * 2_500_000, 28_000)
        extra = 0.0175 * (amount - 2_500_000)
        fee = base + extra
        description = f"""First Kshs 2,500,000 @ 2% = {base:,.2f}<br>
        Remaining {amount - 2_500_000:,.2f} @ 1.75% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""
    elif amount <= 100_000_000:
        base = max(0.02 * 2_500_000, 28_000)
        tier2 = 0.0175 * (5_000_000 - 2_500_000)
        extra = 0.01 * (amount - 5_000_000)
        fee = base + tier2 + extra
        description = f"""First Kshs 2,500,000 @ 2% = {base:,.2f}<br>
        Next Kshs 2,500,000 @ 1.75% = {tier2:,.2f}<br>
        Remaining {amount - 5_000_000:,.2f} @ 1% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""
    elif amount <= 250_000_000:
        base = max(0.02 * 2_500_000, 28_000)
        tier2 = 0.0175 * (5_000_000 - 2_500_000)
        tier3 = 0.01 * (100_000_000 - 5_000_000)
        extra = 0.0075 * (amount - 100_000_000)
        fee = base + tier2 + tier3 + extra
        description = f"""Kshs 2.5M @ 2% = {base:,.2f}<br>
        Next 2.5M @ 1.75% = {tier2:,.2f}<br>
        Next 95M @ 1% = {tier3:,.2f}<br>
        Remaining {amount - 100_000_000:,.2f} @ 0.75% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""
    elif amount <= 1_000_000_000:
        base = max(0.02 * 2_500_000, 28_000)
        tier2 = 0.0175 * (5_000_000 - 2_500_000)
        tier3 = 0.01 * (100_000_000 - 5_000_000)
        tier4 = 0.0075 * (250_000_000 - 100_000_000)
        extra = 0.0015 * (amount - 250_000_000)
        fee = base + tier2 + tier3 + tier4 + extra
        description = f"""Kshs 2.5M @ 2% = {base:,.2f}<br>
        Next 2.5M @ 1.75% = {tier2:,.2f}<br>
        Next 95M @ 1% = {tier3:,.2f}<br>
        Next 150M @ 0.75% = {tier4:,.2f}<br>
        Remaining {amount - 250_000_000:,.2f} @ 0.15% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""
    else:
        base = max(0.02 * 2_500_000, 28_000)
        tier2 = 0.0175 * (5_000_000 - 2_500_000)
        tier3 = 0.01 * (100_000_000 - 5_000_000)
        tier4 = 0.0075 * (250_000_000 - 100_000_000)
        tier5 = 0.0015 * (1_000_000_000 - 250_000_000)
        extra = 0.001 * (amount - 1_000_000_000)
        fee = base + tier2 + tier3 + tier4 + tier5 + extra
        description = f"""Kshs 2.5M @ 2% = {base:,.2f}<br>
        Next 2.5M @ 1.75% = {tier2:,.2f}<br>
        Next 95M @ 1% = {tier3:,.2f}<br>
        Next 150M @ 0.75% = {tier4:,.2f}<br>
        Next 750M @ 0.15% = {tier5:,.2f}<br>
        Remaining {amount - 1_000_000_000:,.2f} @ 0.1% = {extra:,.2f}<br>
        Total = {fee:,.2f}"""

    return fee, description



def calculate_discharge_grantee_with_fee(amount, with_undertaking=True):
    base_fee = 0
    description = "<b>Grantee Discharge Fee</b><br>"
    breakdown = ""

    # Tier 1
    if amount <= 2_500_000:
        base_fee = max(0.02 * amount, 28_000)
        breakdown += f"(i) 2% of {amount:,} = {0.02 * amount:,.2f}<br>"
        breakdown += f"Minimum applied: Ksh 28,000<br>" if 0.02 * amount < 28_000 else ""
    # Tier 2
    elif amount <= 5_000_000:
        tier1 = max(0.02 * 2_500_000, 28_000)
        tier2 = (amount - 2_500_000) * 0.0175
        base_fee = tier1 + tier2
        breakdown += f"(i) 2% of 2,500,000 = {tier1:,.2f} (Minimum applied: 28,000)<br>"
        breakdown += f"(ii) 1.75% of {amount - 2_500_000:,.2f} = {tier2:,.2f}<br>"
    # Tier 3
    elif amount <= 100_000_000:
        tier1 = max(0.02 * 2_500_000, 28_000)
        tier2 = 2_500_000 * 0.0175
        tier3 = (amount - 5_000_000) * 0.01
        base_fee = tier1 + tier2 + tier3
        breakdown += f"(i) 2% of 2,500,000 = {tier1:,.2f}<br>"
        breakdown += f"(ii) 1.75% of 2,500,000 = {tier2:,.2f}<br>"
        breakdown += f"(iii) 1% of {amount - 5_000_000:,.2f} = {tier3:,.2f}<br>"
    # Tier 4
    elif amount <= 250_000_000:
        tier1 = max(0.02 * 2_500_000, 28_000)
        tier2 = 2_500_000 * 0.0175
        tier3 = (100_000_000 - 5_000_000) * 0.01
        tier4 = (amount - 100_000_000) * 0.0075
        base_fee = tier1 + tier2 + tier3 + tier4
        breakdown += f"(i) 2% of 2,500,000 = {tier1:,.2f}<br>"
        breakdown += f"(ii) 1.75% of 2,500,000 = {tier2:,.2f}<br>"
        breakdown += f"(iii) 1% of 95,000,000 = {tier3:,.2f}<br>"
        breakdown += f"(iv) 0.75% of {amount - 100_000_000:,.2f} = {tier4:,.2f}<br>"
    # Tier 5
    elif amount <= 1_000_000_000:
        tier1 = max(0.02 * 2_500_000, 28_000)
        tier2 = 2_500_000 * 0.0175
        tier3 = (100_000_000 - 5_000_000) * 0.01
        tier4 = (250_000_000 - 100_000_000) * 0.0075
        tier5 = (amount - 250_000_000) * 0.0015
        base_fee = tier1 + tier2 + tier3 + tier4 + tier5
        breakdown += f"(i) 2% of 2,500,000 = {tier1:,.2f}<br>"
        breakdown += f"(ii) 1.75% of 2,500,000 = {tier2:,.2f}<br>"
        breakdown += f"(iii) 1% of 95,000,000 = {tier3:,.2f}<br>"
        breakdown += f"(iv) 0.75% of 150,000,000 = {tier4:,.2f}<br>"
        breakdown += f"(v) 0.15% of {amount - 250_000_000:,.2f} = {tier5:,.2f}<br>"
    # Tier 6
    else:
        tier1 = max(0.02 * 2_500_000, 28_000)
        tier2 = 2_500_000 * 0.0175
        tier3 = (100_000_000 - 5_000_000) * 0.01
        tier4 = (250_000_000 - 100_000_000) * 0.0075
        tier5 = (1_000_000_000 - 250_000_000) * 0.0015
        tier6 = (amount - 1_000_000_000) * 0.001
        base_fee = tier1 + tier2 + tier3 + tier4 + tier5 + tier6
        breakdown += f"(i) 2% of 2,500,000 = {tier1:,.2f}<br>"
        breakdown += f"(ii) 1.75% of 2,500,000 = {tier2:,.2f}<br>"
        breakdown += f"(iii) 1% of 95,000,000 = {tier3:,.2f}<br>"
        breakdown += f"(iv) 0.75% of 150,000,000 = {tier4:,.2f}<br>"
        breakdown += f"(v) 0.15% of 750,000,000 = {tier5:,.2f}<br>"
        breakdown += f"(vi) 0.1% of {amount - 1_000_000_000:,.2f} = {tier6:,.2f}<br>"

    # Apply discharge percentage
    if with_undertaking:
        fee = max(0.25 * base_fee, 15_000)
        description += breakdown
        description += f"<b>With Undertaking</b>: 25% of base = {0.25 * base_fee:,.2f}<br>"
        if fee == 15_000:
            description += f"Minimum of Ksh 15,000 applied<br>"
    else:
        fee = max(0.15 * base_fee, 10_000)
        description += breakdown
        description += f"<b>Without Undertaking</b>: 15% of base = {0.15 * base_fee:,.2f}<br>"
        if fee == 10_000:
            description += f"Minimum of Ksh 10,000 applied<br>"

    description += f"<br><b>Total Minimum Fee: Ksh {fee:,.2f}</b>"
    return fee, description


def calculate_discharge_grantee_without_fee(amount):
    description = ""
    base_fee = 0

    if amount <= 5_000_000:
        base_fee = max(0.02 * amount, 35_000)
        breakdown = f"Since amount is ≤ Ksh 5,000,000:<br>Base Fee = max(2% of {amount:,}, 35,000) = Ksh {base_fee:,.2f}"
    elif amount <= 100_000_000:
        tier1 = max(5_000_000 * 0.02, 35_000)
        extra = (amount - 5_000_000) * 0.015
        base_fee = tier1 + extra
        breakdown = f"""5M @ 2% = {tier1:,.2f}<br>
        Remaining {amount - 5_000_000:,.2f} @ 1.5% = {extra:,.2f}<br>
        Base Fee = {base_fee:,.2f}"""
    elif amount <= 250_000_000:
        tier1 = max(5_000_000 * 0.02, 35_000)
        tier2 = (100_000_000 - 5_000_000) * 0.015
        extra = (amount - 100_000_000) * 0.0125
        base_fee = tier1 + tier2 + extra
        breakdown = f"""5M @ 2% = {tier1:,.2f}<br>
        95M @ 1.5% = {tier2:,.2f}<br>
        Remaining {amount - 100_000_000:,.2f} @ 1.25% = {extra:,.2f}<br>
        Base Fee = {base_fee:,.2f}"""
    elif amount <= 1_000_000_000:
        tier1 = max(5_000_000 * 0.02, 35_000)
        tier2 = (100_000_000 - 5_000_000) * 0.015
        tier3 = (250_000_000 - 100_000_000) * 0.0125
        extra = (amount - 250_000_000) * 0.01
        base_fee = tier1 + tier2 + tier3 + extra
        breakdown = f"""5M @ 2% = {tier1:,.2f}<br>
        95M @ 1.5% = {tier2:,.2f}<br>
        150M @ 1.25% = {tier3:,.2f}<br>
        Remaining {amount - 250_000_000:,.2f} @ 1% = {extra:,.2f}<br>
        Base Fee = {base_fee:,.2f}"""
    else:
        tier1 = max(5_000_000 * 0.02, 35_000)
        tier2 = (100_000_000 - 5_000_000) * 0.015
        tier3 = (250_000_000 - 100_000_000) * 0.0125
        tier4 = (1_000_000_000 - 250_000_000) * 0.01
        extra = (amount - 1_000_000_000) * 0.001
        base_fee = tier1 + tier2 + tier3 + tier4 + extra
        breakdown = f"""5M @ 2% = {tier1:,.2f}<br>
        95M @ 1.5% = {tier2:,.2f}<br>
        150M @ 1.25% = {tier3:,.2f}<br>
        750M @ 1% = {tier4:,.2f}<br>
        Remaining {amount - 1_000_000_000:,.2f} @ 0.1% = {extra:,.2f}<br>
        Base Fee = {base_fee:,.2f}"""

    fee = 0.15 * base_fee
    fee = max(fee, 10_000)  # Minimum Ksh 10,000

    description = f"""<b>Discharge Without Undertaking</b><br>
    {breakdown}<br>
    Fee = 15% of Base Fee = Ksh {0.15 * base_fee:,.2f}<br>
    <b>Minimum Applied:</b> Ksh {fee:,.2f}""" if fee == 10_000 else f"""<b>Discharge Without Undertaking</b><br>
    {breakdown}<br>
    Fee = 15% of Base Fee = Ksh {fee:,.2f}"""

    return fee, description


def calculate_create_grantor_fee(amount):
    base_grantee_fee = 0
    description = ""

    if amount <= 2_500_000:
        base_grantee_fee = max(0.02 * amount, 28_000)
        breakdown = f"Since amount ≤ Ksh 2,500,000:<br>Base Fee = max(2% of {amount:,}, 28,000) = Ksh {base_grantee_fee:,.2f}"
    elif amount <= 5_000_000:
        tier1 = max(2_500_000 * 0.02, 28_000)
        extra = (amount - 2_500_000) * 0.0175
        base_grantee_fee = tier1 + extra
        breakdown = f"""2.5M @ 2% = {tier1:,.2f}<br>
        Remaining {amount - 2_500_000:,.2f} @ 1.75% = {extra:,.2f}<br>
        Base Fee = {base_grantee_fee:,.2f}"""
    elif amount <= 100_000_000:
        tier1 = max(2_500_000 * 0.02, 28_000)
        tier2 = (5_000_000 - 2_500_000) * 0.0175
        extra = (amount - 5_000_000) * 0.01
        base_grantee_fee = tier1 + tier2 + extra
        breakdown = f"""2.5M @ 2% = {tier1:,.2f}<br>
        2.5M @ 1.75% = {tier2:,.2f}<br>
        Remaining {amount - 5_000_000:,.2f} @ 1% = {extra:,.2f}<br>
        Base Fee = {base_grantee_fee:,.2f}"""
    elif amount <= 250_000_000:
        tier1 = max(2_500_000 * 0.02, 28_000)
        tier2 = (5_000_000 - 2_500_000) * 0.0175
        tier3 = (100_000_000 - 5_000_000) * 0.01
        extra = (amount - 100_000_000) * 0.0075
        base_grantee_fee = tier1 + tier2 + tier3 + extra
        breakdown = f"""2.5M @ 2% = {tier1:,.2f}<br>
        2.5M @ 1.75% = {tier2:,.2f}<br>
        95M @ 1% = {tier3:,.2f}<br>
        Remaining {amount - 100_000_000:,.2f} @ 0.75% = {extra:,.2f}<br>
        Base Fee = {base_grantee_fee:,.2f}"""
    elif amount <= 1_000_000_000:
        tier1 = max(2_500_000 * 0.02, 28_000)
        tier2 = (5_000_000 - 2_500_000) * 0.0175
        tier3 = (100_000_000 - 5_000_000) * 0.01
        tier4 = (250_000_000 - 100_000_000) * 0.0075
        extra = (amount - 250_000_000) * 0.0015
        base_grantee_fee = tier1 + tier2 + tier3 + tier4 + extra
        breakdown = f"""2.5M @ 2% = {tier1:,.2f}<br>
        2.5M @ 1.75% = {tier2:,.2f}<br>
        95M @ 1% = {tier3:,.2f}<br>
        150M @ 0.75% = {tier4:,.2f}<br>
        Remaining {amount - 250_000_000:,.2f} @ 0.15% = {extra:,.2f}<br>
        Base Fee = {base_grantee_fee:,.2f}"""
    else:
        tier1 = max(2_500_000 * 0.02, 28_000)
        tier2 = (5_000_000 - 2_500_000) * 0.0175
        tier3 = (100_000_000 - 5_000_000) * 0.01
        tier4 = (250_000_000 - 100_000_000) * 0.0075
        tier5 = (1_000_000_000 - 250_000_000) * 0.0015
        extra = (amount - 1_000_000_000) * 0.001
        base_grantee_fee = tier1 + tier2 + tier3 + tier4 + tier5 + extra
        breakdown = f"""2.5M @ 2% = {tier1:,.2f}<br>
        2.5M @ 1.75% = {tier2:,.2f}<br>
        95M @ 1% = {tier3:,.2f}<br>
        150M @ 0.75% = {tier4:,.2f}<br>
        750M @ 0.15% = {tier5:,.2f}<br>
        Remaining {amount - 1_000_000_000:,.2f} @ 0.1% = {extra:,.2f}<br>
        Base Fee = {base_grantee_fee:,.2f}"""

    grantor_fee = 0.5 * base_grantee_fee

    description = f"""<b>Creation of Security - Grantor</b><br>
    {breakdown}<br>
    Grantor Fee = 50% of Base Fee = <b>Ksh {grantor_fee:,.2f}</b>"""

    return grantor_fee, description



def calculate_land_sale_fee(amount):
    # Example calculation for Land Sale/Purchase
    if amount <= 5000000:
        fee = max(0.02 * amount, 35000)
        description = f"2% of Ksh {amount} or Ksh 35,000 whichever is higher: Ksh {fee}"
    elif amount <= 100000000:
        fee = max(0.02 * 5000000, 35000) + 0.015 * (amount - 5000000)
        description = f"2% of Ksh 5,000,000 + 1.5% of the balance above Ksh 5,000,000: Ksh {fee}"
    else:
        fee = (max(0.02 * 5000000, 35000) + 0.015 * (100000000 - 5000000)) + 0.01 * (amount - 100000000)
        description = f"2% of Ksh 5,000,000 + 1.5% of the next Ksh 95,000,000 + 1% of the balance above Ksh 100,000,000: Ksh {fee}"
    return fee, description





def calculate_land_sale_fee(amount):
    # Example calculation for Land Sale/Purchase
    if amount <= 5000000:
        fee = max(0.02 * amount, 35000)
        description = f"2% of Ksh {amount} or Ksh 35,000 whichever is higher: Ksh {fee}"
    elif amount <= 100000000:
        fee = max(0.02 * 5000000, 35000) + 0.015 * (amount - 5000000)
        description = f"2% of Ksh 5,000,000 + 1.5% of the balance above Ksh 5,000,000: Ksh {fee}"
    else:
        fee = (max(0.02 * 5000000, 35000) + 0.015 * (100000000 - 5000000)) + 0.01 * (amount - 100000000)
        description = f"2% of Ksh 5,000,000 + 1.5% of the next Ksh 95,000,000 + 1% of the balance above Ksh 100,000,000: Ksh {fee}"
    return fee, description


def calculate_discharge_grantor_fee(amount):
    """
    Calculates the scale fee for the discharge of a security for the grantor,
    which is 25% of the grantee's scale fee (subparagraph b), with a minimum of Ksh 15,000.
    """

    description = "<strong>Discharge of Security – Grantor</strong><br><ul>"
    grantee_fee = 0

    if amount <= 2500000:
        grantee_fee = max(0.02 * amount, 28000)
        description += f"<li>First Ksh 2,500,000 @ 2% = Ksh {0.02 * min(amount, 2500000):,.2f}</li>"
    elif amount <= 5000000:
        grantee_fee = max(0.02 * 2500000, 28000)
        grantee_fee += 0.0175 * (amount - 2500000)
        description += "<li>First Ksh 2,500,000 @ 2% = Ksh 50,000.00</li>"
        description += f"<li>Next Ksh {amount - 2500000:,.0f} @ 1.75% = Ksh {0.0175 * (amount - 2500000):,.2f}</li>"
    elif amount <= 100000000:
        grantee_fee = (
            max(0.02 * 2500000, 28000) +
            0.0175 * (5000000 - 2500000) +
            0.01 * (amount - 5000000)
        )
        description += "<li>First Ksh 2,500,000 @ 2% = Ksh 50,000.00</li>"
        description += "<li>Next Ksh 2,500,000 @ 1.75% = Ksh 43,750.00</li>"
        description += f"<li>Next Ksh {amount - 5000000:,.0f} @ 1% = Ksh {0.01 * (amount - 5000000):,.2f}</li>"
    elif amount <= 250000000:
        grantee_fee = (
            max(0.02 * 2500000, 28000) +
            0.0175 * (5000000 - 2500000) +
            0.01 * (100000000 - 5000000) +
            0.0075 * (amount - 100000000)
        )
        description += "<li>First Ksh 2,500,000 @ 2% = Ksh 50,000.00</li>"
        description += "<li>Next Ksh 2,500,000 @ 1.75% = Ksh 43,750.00</li>"
        description += "<li>Next Ksh 95,000,000 @ 1% = Ksh 950,000.00</li>"
        description += f"<li>Next Ksh {amount - 100000000:,.0f} @ 0.75% = Ksh {0.0075 * (amount - 100000000):,.2f}</li>"
    elif amount <= 1000000000:
        grantee_fee = (
            max(0.02 * 2500000, 28000) +
            0.0175 * (5000000 - 2500000) +
            0.01 * (100000000 - 5000000) +
            0.0075 * (250000000 - 100000000) +
            0.0015 * (amount - 250000000)
        )
        description += "<li>First Ksh 2,500,000 @ 2% = Ksh 50,000.00</li>"
        description += "<li>Next Ksh 2,500,000 @ 1.75% = Ksh 43,750.00</li>"
        description += "<li>Next Ksh 95,000,000 @ 1% = Ksh 950,000.00</li>"
        description += "<li>Next Ksh 150,000,000 @ 0.75% = Ksh 1,125,000.00</li>"
        description += f"<li>Next Ksh {amount - 250000000:,.0f} @ 0.15% = Ksh {0.0015 * (amount - 250000000):,.2f}</li>"
    else:
        grantee_fee = (
            max(0.02 * 2500000, 28000) +
            0.0175 * (5000000 - 2500000) +
            0.01 * (100000000 - 5000000) +
            0.0075 * (250000000 - 100000000) +
            0.0015 * (1000000000 - 250000000) +
            0.001 * (amount - 1000000000)
        )
        description += "<li>First Ksh 2,500,000 @ 2% = Ksh 50,000.00</li>"
        description += "<li>Next Ksh 2,500,000 @ 1.75% = Ksh 43,750.00</li>"
        description += "<li>Next Ksh 95,000,000 @ 1% = Ksh 950,000.00</li>"
        description += "<li>Next Ksh 150,000,000 @ 0.75% = Ksh 1,125,000.00</li>"
        description += "<li>Next Ksh 750,000,000 @ 0.15% = Ksh 1,125,000.00</li>"
        description += f"<li>Excess Ksh {amount - 1000000000:,.0f} @ 0.1% = Ksh {0.001 * (amount - 1000000000):,.2f}</li>"

    grantor_fee = 0.25 * grantee_fee
    final_fee = max(grantor_fee, 15000)

    description += f"</ul><strong>25% of Grantee's Fee:</strong> Ksh {grantor_fee:,.2f}<br>"
    description += f"<strong>Final Fee (Min Ksh 15,000):</strong> Ksh {final_fee:,.2f}"

    return final_fee, description


def book_appointment(request):
    saved_appointment = None  # To store the saved appointment object
    form = AppointmentForm()  # Initialize the form by default
    booked_times = []  # List to store booked times for the selected date

    # Get today's date
    today = date.today()

    if request.method == 'POST':
        form = AppointmentForm(request.POST)  # Reinitialize the form with POST data
        if form.is_valid():
            # Process the valid form
            appointment = form.save(commit=False)

            # Try to get the Advocate associated with the logged-in user
            try:
                advocate = Advocate.objects.get(user=request.user)
            except Advocate.DoesNotExist:
                # If no Advocate exists, create one
                advocate = Advocate.objects.create(
                    user=request.user,
                    name=request.user.username,
                    specialization=form.cleaned_data.get('specialization')
                )

            appointment.advocate = advocate

            # Get all appointments that conflict with the selected date and time
            booked_appointments = Appointment.objects.filter(
                appointment_date=appointment.appointment_date
            )
            booked_times = booked_appointments.values_list('appointment_time', flat=True)

            # Save the appointment only if the time is not already booked
            if appointment.appointment_time not in booked_times:
                appointment.save()
                saved_appointment = appointment  # Store the appointment if it is successfully saved
                # After booking, reset the form for next use
                form = AppointmentForm()  # Clear the form by reinitializing
            else:
                form.add_error('appointment_time', 'This time is already booked.')

    return render(request, 'book_appointment.html', {
        'form': form,
        'saved_appointment': saved_appointment,
        'booked_times': booked_times,  # Pass the booked times to the template
        'today': today,  # Pass today's date to the template
    })



def deletebooking(request, id):
    delbookapp = Appointment.objects.get(id=id)
    delbookapp.delete()
    messages.success(request, 'Appointment deleted successfully.')
    return redirect('appointmenttb')

def appointments(request):
    if not request.user.is_authenticated:
        return render(request, 'appointmenttb.html', {
            'app': [],
            'page_obj': [],
            'message': 'You must be logged in.'
        })

    try:
        advocate = Advocate.objects.get(user=request.user)
    except Advocate.DoesNotExist:
        return render(request, 'appointmenttb.html', {
            'app': [],
            'page_obj': [],
            'message': 'No advocate profile found for this user.'
        })

    all_appointments = Appointment.objects.filter(advocate=advocate).order_by('appointment_date', 'appointment_time')

    now = datetime.now()
    appointments_with_status = []

    for appointment in all_appointments:
        appointment_datetime = datetime.combine(appointment.appointment_date, appointment.appointment_time)

        if appointment_datetime < now:
            appointment.temp_status = "passed"
        elif appointment_datetime - now <= timedelta(hours=12):
            appointment.temp_status = "upcoming"
        else:
            appointment.temp_status = "pending"

        appointments_with_status.append(appointment)

    paginator = Paginator(appointments_with_status, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'appointmenttb.html', {
        'app': page_obj,
        'page_obj': page_obj
    })
def editBook(request, id):
    appointment = get_object_or_404(Appointment, pk=id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointmenttb')  # or your desired success URL
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'updatebooking.html', {'form': form})


