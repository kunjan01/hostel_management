"""
REST API Serializers for Hostel Management System

Provides serialization for all models in JSON format
"""

from rest_framework import serializers

from apps.hostel.models import Block, Room, RoomAllocation, RoomBill
from apps.mess.models import MessBill, MessMenu, MessRegistration
from apps.students.models import Student


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model"""

    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id',
            'enrollment_no',
            'name',
            'email',
            'phone',
            'gender',
            'date_of_birth',
            'blood_group',
            'course',
            'year',
            'branch',
            'city',
            'state',
            'user_details',
            'is_active',
            'joining_date',
        ]
        read_only_fields = ['id', 'joining_date']

    def get_user_details(self, obj):
        """Get user details if available"""
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'email': obj.user.email,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
            }
        return None


class BlockSerializer(serializers.ModelSerializer):
    """Serializer for Block model"""

    room_count = serializers.SerializerMethodField()
    available_rooms = serializers.SerializerMethodField()
    occupancy_rate = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = [
            'id',
            'name',
            'block_type',
            'floors',
            'warden_name',
            'warden_phone',
            'description',
            'is_active',
            'room_count',
            'available_rooms',
            'occupancy_rate',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_room_count(self, obj):
        return obj.total_rooms()

    def get_available_rooms(self, obj):
        return obj.available_rooms()

    def get_occupancy_rate(self, obj):
        total = obj.total_rooms()
        if total == 0:
            return 0
        occupied = obj.occupied_rooms()
        return round((occupied / total) * 100, 2)


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room model"""

    block_name = serializers.CharField(source='block.name', read_only=True)
    current_occupants = serializers.SerializerMethodField()
    available_beds = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'id',
            'block',
            'block_name',
            'room_number',
            'floor',
            'room_type',
            'capacity',
            'monthly_rent',
            'status',
            'has_ac',
            'has_wifi',
            'has_attached_bathroom',
            'description',
            'current_occupants',
            'available_beds',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_current_occupants(self, obj):
        return obj.current_occupants()

    def get_available_beds(self, obj):
        return obj.available_beds()


class RoomAllocationSerializer(serializers.ModelSerializer):
    """Serializer for RoomAllocation model"""

    student_name = serializers.CharField(source='student.name', read_only=True)
    room_details = serializers.SerializerMethodField()
    tenure_days = serializers.SerializerMethodField()

    class Meta:
        model = RoomAllocation
        fields = [
            'id',
            'student',
            'student_name',
            'room',
            'room_details',
            'allocation_date',
            'vacating_date',
            'status',
            'tenure_days',
            'remarks',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_room_details(self, obj):
        return {
            'id': obj.room.id,
            'block': obj.room.block.name,
            'room_number': obj.room.room_number,
            'room_type': obj.room.room_type,
            'capacity': obj.room.capacity,
        }

    def get_tenure_days(self, obj):
        from datetime import date

        if obj.vacating_date:
            return (obj.vacating_date - obj.allocation_date).days
        return (date.today() - obj.allocation_date).days


class MessMenuSerializer(serializers.ModelSerializer):
    """Serializer for MessMenu model"""

    class Meta:
        model = MessMenu
        fields = [
            'id',
            'day',
            'meal',
            'items',
            'timing',
        ]
        read_only_fields = ['id']


class MessRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for MessRegistration model"""

    student_name = serializers.CharField(source='student.name', read_only=True)
    student_enrollment = serializers.CharField(
        source='student.enrollment_no', read_only=True
    )

    class Meta:
        model = MessRegistration
        fields = [
            'id',
            'student',
            'student_name',
            'student_enrollment',
            'plan',
            'monthly_charge',
            'registration_date',
            'is_active',
        ]
        read_only_fields = ['id', 'registration_date']


class RoomBillSerializer(serializers.ModelSerializer):
    """Serializer for RoomBill model"""

    student_name = serializers.CharField(source='student.name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    month_name = serializers.CharField(source='get_month_display', read_only=True)
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = RoomBill
        fields = [
            'id',
            'student',
            'student_name',
            'room',
            'room_number',
            'month',
            'month_name',
            'year',
            'room_rent',
            'status',
            'due_date',
            'paid_date',
            'remarks',
            'days_until_due',
            'is_overdue',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_days_until_due(self, obj):
        from datetime import date

        today = date.today()
        delta = (obj.due_date - today).days
        return delta

    def get_is_overdue(self, obj):
        from datetime import date

        return obj.due_date < date.today() and obj.status != 'Paid'


class MessBillSerializer(serializers.ModelSerializer):
    """Serializer for MessBill model"""

    student_name = serializers.CharField(source='student.name', read_only=True)
    month_name = serializers.CharField(source='get_month_display', read_only=True)
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = MessBill
        fields = [
            'id',
            'student',
            'student_name',
            'month',
            'month_name',
            'year',
            'amount',
            'status',
            'due_date',
            'paid_date',
            'remarks',
            'days_until_due',
            'is_overdue',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_days_until_due(self, obj):
        from datetime import date

        today = date.today()
        delta = (obj.due_date - today).days
        return delta

    def get_is_overdue(self, obj):
        from datetime import date

        return obj.due_date < date.today() and obj.status != 'Paid'


class CombinedBillSerializer(serializers.Serializer):
    """Serializer for combined Mess + Room bills"""

    month = serializers.IntegerField()
    month_name = serializers.CharField()
    year = serializers.IntegerField()
    mess_bill = MessBillSerializer(allow_null=True)
    room_bill = RoomBillSerializer(allow_null=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    combined_status = serializers.CharField()


class StudentBillSummarySerializer(serializers.Serializer):
    """Serializer for student bill summary"""

    student = StudentSerializer()
    mess_bills = serializers.SerializerMethodField()
    room_bills = serializers.SerializerMethodField()
    total_pending_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_paid_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def get_mess_bills(self, obj):
        return {
            'pending': obj.get('mess_pending_count', 0),
            'paid': obj.get('mess_paid_count', 0),
            'total_amount': obj.get('mess_total_amount', 0),
        }

    def get_room_bills(self, obj):
        return {
            'pending': obj.get('room_pending_count', 0),
            'paid': obj.get('room_paid_count', 0),
            'total_amount': obj.get('room_total_amount', 0),
        }
