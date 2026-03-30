"""
REST API ViewSets for Hostel Management System

Provides CRUD operations and custom actions for all models
"""

from decimal import Decimal

from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.hostel.models import Block, Room, RoomAllocation, RoomBill
from apps.mess.models import MessBill, MessMenu, MessRegistration
from apps.services.billing_service import (
    BillGenerationService,
    BillPaymentService,
    BillQueryService,
)
from apps.students.models import Student

from .filters import (
    BlockFilter,
    MessBillFilter,
    MessMenuFilter,
    MessRegistrationFilter,
    RoomAllocationFilter,
    RoomBillFilter,
    RoomFilter,
    StudentFilter,
)
from .serializers import (
    BlockSerializer,
    CombinedBillSerializer,
    MessBillSerializer,
    MessMenuSerializer,
    MessRegistrationSerializer,
    RoomAllocationSerializer,
    RoomBillSerializer,
    RoomSerializer,
    StudentBillSummarySerializer,
    StudentSerializer,
)


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Student model
    - GET /api/v1/students/ - List all students with pagination
    - GET /api/v1/students/{id}/ - Get student details
    - POST /api/v1/students/ - Create student (admin only)
    - PUT /api/v1/students/{id}/ - Update student (admin only)
    - DELETE /api/v1/students/{id}/ - Delete student (admin only)
    - GET /api/v1/students/{id}/bills/ - Get student's bills
    - GET /api/v1/students/{id}/bill-summary/ - Get student's bill summary
    
    Pagination: 50 items per page (?page=1)
    Filtering: ?search=name&ordering=year
    """

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_class = StudentFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'enrollment_no', 'email']
    ordering_fields = ['name', 'enrollment_no', 'year']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def bills(self, request, pk=None):
        """Get all bills for a student"""
        student = self.get_object()
        mess_bills = MessBill.objects.filter(student=student).with_related()
        room_bills = RoomBill.objects.filter(student=student).with_related()

        response_data = {
            'mess_bills': MessBillSerializer(mess_bills, many=True).data,
            'room_bills': RoomBillSerializer(room_bills, many=True).data,
            'total_pending': MessBill.objects.filter(
                student=student, status='Pending'
            ).count()
            + RoomBill.objects.filter(student=student, status='Pending').count(),
        }
        return Response(response_data)

    @action(detail=True, methods=['get'])
    def bill_summary(self, request, pk=None):
        """Get bill summary for a student"""
        student = self.get_object()
        mess_bills = MessBill.objects.filter(student=student)
        room_bills = RoomBill.objects.filter(student=student)

        mess_pending = mess_bills.filter(status='Pending').count()
        mess_paid = mess_bills.filter(status='Paid').count()
        mess_total = mess_bills.aggregate(total=Sum('amount'))['total'] or Decimal('0')

        room_pending = room_bills.filter(status='Pending').count()
        room_paid = room_bills.filter(status='Paid').count()
        room_total = room_bills.aggregate(total=Sum('room_rent'))['total'] or Decimal('0')

        total_pending = mess_total + room_total
        total_paid = MessBill.objects.filter(student=student, status='Paid').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        total_paid += (
            RoomBill.objects.filter(student=student, status='Paid').aggregate(
                total=Sum('room_rent')
            )['total']
            or Decimal('0')
        )

        summary = {
            'student': StudentSerializer(student).data,
            'mess_pending_count': mess_pending,
            'mess_paid_count': mess_paid,
            'mess_total_amount': mess_total,
            'room_pending_count': room_pending,
            'room_paid_count': room_paid,
            'room_total_amount': room_total,
            'total_pending_amount': total_pending,
            'total_paid_amount': total_paid,
        }
        return Response(summary)


class BlockViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Block model
    - GET /api/v1/blocks/ - List all blocks with pagination
    - GET /api/v1/blocks/{id}/ - Get block details
    - GET /api/v1/blocks/{id}/rooms/ - Get rooms in block
    - POST /api/v1/blocks/ - Create block (admin only)
    - PUT /api/v1/blocks/{id}/ - Update block (admin only)
    
    Pagination: 50 items per page (?page=1)
    Filtering: ?search=name&ordering=block_type
    """

    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    filter_class = BlockFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'warden_name']
    ordering_fields = ['name', 'block_type']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def rooms(self, request, pk=None):
        """Get all rooms in a block"""
        block = self.get_object()
        rooms = block.room_set.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Room model
    - GET /api/v1/rooms/ - List all rooms with pagination
    - GET /api/v1/rooms/{id}/ - Get room details
    - POST /api/v1/rooms/ - Create room (admin only)
    - PUT /api/v1/rooms/{id}/ - Update room (admin only)
    - GET /api/v1/rooms/{id}/allocations/ - Get allocations for room
    
    Pagination: 50 items per page (?page=1)
    Filtering: ?search=room_number&ordering=monthly_rent
    """

    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_class = RoomFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    search_fields = ['room_number', 'block__name', 'room_type']
    ordering_fields = ['room_number', 'monthly_rent', 'status']
    ordering = ['block', 'room_number']

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def allocations(self, request, pk=None):
        """Get allocations for a room"""
        room = self.get_object()
        allocations = room.roomallocation_set.all()
        serializer = RoomAllocationSerializer(allocations, many=True)
        return Response(serializer.data)


class RoomAllocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RoomAllocation model
    - GET /api/v1/allocations/ - List all allocations with pagination
    - GET /api/v1/allocations/{id}/ - Get allocation details
    - POST /api/v1/allocations/ - Create allocation (admin only)
    - PUT /api/v1/allocations/{id}/ - Update allocation (admin only)
    - POST /api/v1/allocations/{id}/vacate/ - Mark student as vacated
    
    Pagination: 50 items per page (?page=1)
    Filtering: ?ordering=-allocation_date
    """

    queryset = RoomAllocation.objects.all()
    serializer_class = RoomAllocationSerializer
    filter_class = RoomAllocationFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    ordering_fields = ['allocation_date', 'status']
    ordering = ['-allocation_date']

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update', 'vacate']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def vacate(self, request, pk=None):
        """Mark a student as vacated"""
        allocation = self.get_object()
        allocation.status = 'Vacated'
        allocation.vacating_date = timezone.now().date()
        allocation.save()
        return Response(
            {'status': 'Student vacated', 'allocation': RoomAllocationSerializer(allocation).data}
        )


class RoomBillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RoomBill model
    - GET /api/v1/room-bills/ - List room bills with pagination
    - GET /api/v1/room-bills/{id}/ - Get bill details
    - POST /api/v1/room-bills/{id}/mark-paid/ - Mark bill as paid
    - POST /api/v1/room-bills/{id}/mark-pending/ - Mark bill as pending
    
    Pagination: 50 items per page (?page=1)
    Filtering: ?search=student_name&ordering=-due_date
    """

    queryset = RoomBill.objects.all()
    serializer_class = RoomBillSerializer
    filter_class = RoomBillFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    search_fields = ['student__name', 'status']
    ordering_fields = ['due_date', 'created_at', 'status']
    ordering = ['-due_date']

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update', 'mark_paid', 'mark_pending']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a room bill as paid"""
        success, message = BillPaymentService.mark_bill_paid(pk, bill_type='room')
        if success:
            bill = self.get_object()
            return Response({'status': message, 'bill': RoomBillSerializer(bill).data})
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_pending(self, request, pk=None):
        """Mark a room bill as pending"""
        success, message = BillPaymentService.mark_bill_pending(pk, bill_type='room')
        if success:
            bill = self.get_object()
            return Response({'status': message, 'bill': RoomBillSerializer(bill).data})
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)


class MessMenuViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MessMenu model
    - GET /api/v1/mess-menu/ - List menu items with pagination
    - POST /api/v1/mess-menu/ - Create menu item (admin only)
    - PUT /api/v1/mess-menu/{id}/ - Update menu item (admin only)
    
    Pagination: 50 items per page (?page=1)
    Filtering: ?ordering=day
    """

    queryset = MessMenu.objects.all()
    serializer_class = MessMenuSerializer
    filter_class = MessMenuFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    search_fields = ['day', 'meal']
    ordering_fields = ['day', 'meal']
    ordering = ['day', 'meal']

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [IsAdminUser()]
        return super().get_permissions()


class MessRegistrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MessRegistration model
    - GET /api/v1/mess-registrations/ - List registrations with pagination
    - POST /api/v1/mess-registrations/ - Create registration (admin only)
    - PUT /api/v1/mess-registrations/{id}/ - Update registration (admin only)
    
    Pagination: 50 items per page (?page=1)
    Filtering: ?search=student_name&ordering=-registration_date
    """

    queryset = MessRegistration.objects.all()
    serializer_class = MessRegistrationSerializer
    filter_class = MessRegistrationFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    search_fields = ['student__name', 'plan']
    ordering_fields = ['registration_date', 'plan']
    ordering = ['-registration_date']

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [IsAdminUser()]
        return super().get_permissions()


class MessBillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MessBill model
    - GET /api/v1/mess-bills/ - List mess bills with pagination
    - GET /api/v1/mess-bills/{id}/ - Get bill details
    - POST /api/v1/mess-bills/{id}/mark-paid/ - Mark bill as paid
    - POST /api/v1/mess-bills/{id}/mark-pending/ - Mark bill as pending
    - POST /api/v1/mess-bills/generate/ - Generate bills for month/year
    
    Pagination: 50 items per page (?page=1)
    Filtering: ?search=student_name&ordering=-due_date
    """

    queryset = MessBill.objects.all()
    serializer_class = MessBillSerializer
    filter_class = MessBillFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    search_fields = ['student__name', 'status']
    ordering_fields = ['due_date', 'created_at', 'status']
    ordering = ['-due_date']

    def get_permissions(self):
        if self.action in [
            'create',
            'destroy',
            'update',
            'partial_update',
            'mark_paid',
            'mark_pending',
            'generate',
        ]:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a mess bill as paid"""
        success, message = BillPaymentService.mark_bill_paid(pk, bill_type='mess')
        if success:
            bill = self.get_object()
            return Response({'status': message, 'bill': MessBillSerializer(bill).data})
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_pending(self, request, pk=None):
        """Mark a mess bill as pending"""
        success, message = BillPaymentService.mark_bill_pending(pk, bill_type='mess')
        if success:
            bill = self.get_object()
            return Response({'status': message, 'bill': MessBillSerializer(bill).data})
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate bills for a specific month/year"""
        month = request.data.get('month')
        year = request.data.get('year')

        if not month or not year:
            return Response(
                {'error': 'Month and year are required'}, status=status.HTTP_400_BAD_REQUEST
            )

        result = BillGenerationService.generate_all_bills(int(month), int(year))
        return Response(result)
