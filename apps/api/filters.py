"""
Django Filter FilterSets for Hostel Management System

Provides advanced filtering capabilities for all model viewsets
"""

import django_filters
from django.db.models import Q
from rest_framework import filters

from apps.hostel.models import Block, Room, RoomAllocation, RoomBill
from apps.mess.models import MessBill, MessMenu, MessRegistration
from apps.students.models import Student


class StudentFilter(django_filters.FilterSet):
    """
    Advanced filters for Student model
    
    Filters:
    - name: Search in student name (case-insensitive)
    - enrollment_no: Exact match or contains
    - department: Filter by department
    - year: Filter by academic year
    - email: Search in email
    - created_after: Filter students created after date
    - created_before: Filter students created before date
    """
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Name (contains)'
    )
    enrollment_no = django_filters.CharFilter(
        field_name='enrollment_no',
        lookup_expr='icontains',
        label='Enrollment Number (contains)'
    )
    department = django_filters.CharFilter(
        field_name='department',
        lookup_expr='iexact',
        label='Department'
    )
    year = django_filters.NumberFilter(
        field_name='year',
        label='Academic Year'
    )
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        label='Email (contains)'
    )
    
    class Meta:
        model = Student
        fields = ['name', 'enrollment_no', 'department', 'year', 'email']


class BlockFilter(django_filters.FilterSet):
    """
    Advanced filters for Block model
    
    Filters:
    - name: Search in block name
    - block_type: Filter by block type (Boys/Girls)
    - warden_name: Search in warden name
    """
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Block Name (contains)'
    )
    block_type = django_filters.ChoiceFilter(
        field_name='block_type',
        choices=[('Boys', 'Boys'), ('Girls', 'Girls')],
        label='Block Type'
    )
    warden_name = django_filters.CharFilter(
        field_name='warden_name',
        lookup_expr='icontains',
        label='Warden Name (contains)'
    )
    
    class Meta:
        model = Block
        fields = ['name', 'block_type', 'warden_name']


class RoomFilter(django_filters.FilterSet):
    """
    Advanced filters for Room model
    
    Filters:
    - room_number: Search in room number
    - block: Filter by block
    - room_type: Filter by room type
    - status: Filter by room status (Available/Occupied)
    - capacity: Filter by room capacity
    - monthly_rent_min: Minimum rental amount
    - monthly_rent_max: Maximum rental amount
    """
    
    room_number = django_filters.CharFilter(
        field_name='room_number',
        lookup_expr='icontains',
        label='Room Number (contains)'
    )
    block = django_filters.ModelChoiceFilter(
        queryset=Block.objects.all(),
        label='Block'
    )
    room_type = django_filters.CharFilter(
        field_name='room_type',
        lookup_expr='icontains',
        label='Room Type (contains)'
    )
    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=[('Available', 'Available'), ('Occupied', 'Occupied')],
        label='Room Status'
    )
    capacity = django_filters.NumberFilter(
        field_name='capacity',
        label='Capacity'
    )
    monthly_rent_min = django_filters.NumberFilter(
        field_name='monthly_rent',
        lookup_expr='gte',
        label='Minimum Monthly Rent'
    )
    monthly_rent_max = django_filters.NumberFilter(
        field_name='monthly_rent',
        lookup_expr='lte',
        label='Maximum Monthly Rent'
    )
    
    class Meta:
        model = Room
        fields = ['room_number', 'block', 'room_type', 'status', 'capacity']


class RoomAllocationFilter(django_filters.FilterSet):
    """
    Advanced filters for RoomAllocation model
    
    Filters:
    - student: Filter by student
    - room: Filter by room
    - status: Filter by allocation status
    - allocation_date_after: Allocations after date
    - allocation_date_before: Allocations before date
    """
    
    student = django_filters.ModelChoiceFilter(
        queryset=Student.objects.all(),
        label='Student'
    )
    room = django_filters.ModelChoiceFilter(
        queryset=Room.objects.all(),
        label='Room'
    )
    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=[('Active', 'Active'), ('Vacated', 'Vacated')],
        label='Allocation Status'
    )
    allocation_date_after = django_filters.DateFilter(
        field_name='allocation_date',
        lookup_expr='gte',
        label='Allocated After Date'
    )
    allocation_date_before = django_filters.DateFilter(
        field_name='allocation_date',
        lookup_expr='lte',
        label='Allocated Before Date'
    )
    
    class Meta:
        model = RoomAllocation
        fields = ['student', 'room', 'status']


class RoomBillFilter(django_filters.FilterSet):
    """
    Advanced filters for RoomBill model
    
    Filters:
    - student: Filter by student
    - status: Filter by payment status
    - created_after: Bills created after date
    - created_before: Bills created before date
    - amount_min: Minimum bill amount
    - amount_max: Maximum bill amount
    """
    
    student = django_filters.ModelChoiceFilter(
        queryset=Student.objects.all(),
        label='Student'
    )
    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Overdue', 'Overdue')],
        label='Payment Status'
    )
    created_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created After Date'
    )
    created_before = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created Before Date'
    )
    amount_min = django_filters.NumberFilter(
        field_name='room_rent',
        lookup_expr='gte',
        label='Minimum Amount'
    )
    amount_max = django_filters.NumberFilter(
        field_name='room_rent',
        lookup_expr='lte',
        label='Maximum Amount'
    )
    
    class Meta:
        model = RoomBill
        fields = ['student', 'status']


class MessMenuFilter(django_filters.FilterSet):
    """
    Advanced filters for MessMenu model
    
    Filters:
    - day: Filter by day of week
    - meal: Search in meal content
    """
    
    day = django_filters.ChoiceFilter(
        field_name='day',
        choices=[
            ('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
            ('Saturday', 'Saturday'),
            ('Sunday', 'Sunday'),
        ],
        label='Day of Week'
    )
    meal = django_filters.CharFilter(
        field_name='meal',
        lookup_expr='icontains',
        label='Meal (contains)'
    )
    
    class Meta:
        model = MessMenu
        fields = ['day', 'meal']


class MessRegistrationFilter(django_filters.FilterSet):
    """
    Advanced filters for MessRegistration model
    
    Filters:
    - student: Filter by student
    - plan: Filter by meal plan
    - status: Filter by registration status
    - registration_date_after: Registrations after date
    - registration_date_before: Registrations before date
    """
    
    student = django_filters.ModelChoiceFilter(
        queryset=Student.objects.all(),
        label='Student'
    )
    plan = django_filters.CharFilter(
        field_name='plan',
        lookup_expr='icontains',
        label='Meal Plan (contains)'
    )
    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Suspended', 'Suspended')],
        label='Registration Status'
    )
    registration_date_after = django_filters.DateFilter(
        field_name='registration_date',
        lookup_expr='gte',
        label='Registered After Date'
    )
    registration_date_before = django_filters.DateFilter(
        field_name='registration_date',
        lookup_expr='lte',
        label='Registered Before Date'
    )
    
    class Meta:
        model = MessRegistration
        fields = ['student', 'plan', 'status']


class MessBillFilter(django_filters.FilterSet):
    """
    Advanced filters for MessBill model
    
    Filters:
    - student: Filter by student
    - status: Filter by payment status
    - month: Filter by month
    - year: Filter by year
    - created_after: Bills created after date
    - created_before: Bills created before date
    - amount_min: Minimum bill amount
    - amount_max: Maximum bill amount
    """
    
    student = django_filters.ModelChoiceFilter(
        queryset=Student.objects.all(),
        label='Student'
    )
    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Overdue', 'Overdue')],
        label='Payment Status'
    )
    month = django_filters.NumberFilter(
        field_name='month',
        label='Month (1-12)'
    )
    year = django_filters.NumberFilter(
        field_name='year',
        label='Year'
    )
    created_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created After Date'
    )
    created_before = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created Before Date'
    )
    amount_min = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte',
        label='Minimum Amount'
    )
    amount_max = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte',
        label='Maximum Amount'
    )
    
    class Meta:
        model = MessBill
        fields = ['student', 'status', 'month', 'year']
