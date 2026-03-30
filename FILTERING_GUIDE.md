# 🔍 Advanced API Filtering Guide

Complete guide to using advanced filtering on Hostel Management System API endpoints.

## Overview

The API provides powerful filtering capabilities through:
1. **Search Filters** - Full-text search across multiple fields
2. **Exact Filters** - Filter by specific values (dropdowns, choices)
3. **Range Filters** - Filter by minimum/maximum values (dates, amounts)
4. **Ordering** - Sort results by different fields

---

## 🔎 Students Endpoint Filters

**Base URL:** `http://localhost/api/v1/students/`

### Available Filters

| Parameter | Type | Example |
|-----------|------|---------|
| `name` | Text (contains) | `?name=john` |
| `enrollment_no` | Text (contains) | `?enrollment_no=CSE2021` |
| `department` | Exact | `?department=CSE` |
| `year` | Number | `?year=2` |
| `email` | Text (contains) | `?email=@example.com` |
| `ordering` | Choice | `?ordering=name` or `?ordering=-year` |

### Filter Examples

#### Search by Name
```bash
curl -X GET "http://localhost/api/v1/students/?name=john" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Search by Department
```bash
curl -X GET "http://localhost/api/v1/students/?department=CSE" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Search by Academic Year
```bash
curl -X GET "http://localhost/api/v1/students/?year=2" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Combine Multiple Filters
```bash
curl -X GET "http://localhost/api/v1/students/?department=ECE&year=3&ordering=name" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Search + Filter + Paginate
```bash
curl -X GET "http://localhost/api/v1/students/?name=john&department=CSE&page=2" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🏠 Blocks Endpoint Filters

**Base URL:** `http://localhost/api/v1/blocks/`

### Available Filters

| Parameter | Type | Example |
|-----------|------|---------|
| `name` | Text (contains) | `?name=Block%20A` |
| `block_type` | Choice | `?block_type=Boys` or `?block_type=Girls` |
| `warden_name` | Text (contains) | `?warden_name=sharma` |
| `ordering` | Choice | `?ordering=name` |

### Filter Examples

#### Filter by Block Type
```bash
# Get all Boys blocks
curl -X GET "http://localhost/api/v1/blocks/?block_type=Boys" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get all Girls blocks
curl -X GET "http://localhost/api/v1/blocks/?block_type=Girls" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Search by Block Name
```bash
curl -X GET "http://localhost/api/v1/blocks/?name=North" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Search by Warden
```bash
curl -X GET "http://localhost/api/v1/blocks/?warden_name=sharma" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🚪 Rooms Endpoint Filters

**Base URL:** `http://localhost/api/v1/rooms/`

### Available Filters

| Parameter | Type | Example |
|-----------|------|---------|
| `room_number` | Text (contains) | `?room_number=A101` |
| `block` | Choice (ID) | `?block=1` |
| `room_type` | Text (contains) | `?room_type=Standard` |
| `status` | Choice | `?status=Available` or `?status=Occupied` |
| `capacity` | Number | `?capacity=2` |
| `monthly_rent_min` | Number | `?monthly_rent_min=5000` |
| `monthly_rent_max` | Number | `?monthly_rent_max=10000` |
| `ordering` | Choice | `?ordering=monthly_rent` |

### Filter Examples

#### Find Available Rooms
```bash
curl -X GET "http://localhost/api/v1/rooms/?status=Available" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Filter by Block
```bash
# Get all rooms in block 1
curl -X GET "http://localhost/api/v1/rooms/?block=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Filter by Room Capacity
```bash
curl -X GET "http://localhost/api/v1/rooms/?capacity=2" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Filter by Rental Range
```bash
# Rooms between 5000-10000
curl -X GET "http://localhost/api/v1/rooms/?monthly_rent_min=5000&monthly_rent_max=10000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Find Affordable Available Rooms in Block A
```bash
curl -X GET "http://localhost/api/v1/rooms/?status=Available&monthly_rent_max=8000&ordering=monthly_rent" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🛏️ Allocations Endpoint Filters

**Base URL:** `http://localhost/api/v1/allocations/`

### Available Filters

| Parameter | Type | Example |
|-----------|------|---------|
| `student` | Choice (ID) | `?student=5` |
| `room` | Choice (ID) | `?room=10` |
| `status` | Choice | `?status=Active` or `?status=Vacated` |
| `allocation_date_after` | Date | `?allocation_date_after=2024-01-01` |
| `allocation_date_before` | Date | `?allocation_date_before=2024-12-31` |
| `ordering` | Choice | `?ordering=-allocation_date` |

### Filter Examples

#### Find Active Allocations
```bash
curl -X GET "http://localhost/api/v1/allocations/?status=Active" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Find Allocations for Specific Student
```bash
curl -X GET "http://localhost/api/v1/allocations/?student=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Find Allocations in Date Range
```bash
curl -X GET "http://localhost/api/v1/allocations/?allocation_date_after=2024-01-01&allocation_date_before=2024-06-30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Find Recent Allocations Ordered by Date
```bash
curl -X GET "http://localhost/api/v1/allocations/?ordering=-allocation_date&page=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 💰 Bills Filtering

### Room Bills - `http://localhost/api/v1/room-bills/`

| Parameter | Type | Example |
|-----------|------|---------|
| `student` | Choice (ID) | `?student=5` |
| `status` | Choice | `?status=Pending` |
| `created_after` | Date | `?created_after=2024-01-01` |
| `created_before` | Date | `?created_before=2024-12-31` |
| `amount_min` | Number | `?amount_min=5000` |
| `amount_max` | Number | `?amount_max=10000` |

#### Room Bills Examples

```bash
# Get pending bills for student
curl -X GET "http://localhost/api/v1/room-bills/?student=5&status=Pending" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get bills in amount range
curl -X GET "http://localhost/api/v1/room-bills/?amount_min=5000&amount_max=15000" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get overdue bills
curl -X GET "http://localhost/api/v1/room-bills/?status=Overdue" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Mess Bills - `http://localhost/api/v1/mess-bills/`

| Parameter | Type | Example |
|-----------|------|---------|
| `student` | Choice (ID) | `?student=5` |
| `status` | Choice | `?status=Paid` |
| `month` | Number | `?month=1` |
| `year` | Number | `?year=2024` |
| `created_after` | Date | `?created_after=2024-01-01` |
| `amount_min` | Number | `?amount_min=1000` |
| `amount_max` | Number | `?amount_max=3000` |

#### Mess Bills Examples

```bash
# Get bills for January 2024
curl -X GET "http://localhost/api/v1/mess-bills/?month=1&year=2024" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get pending mess bills
curl -X GET "http://localhost/api/v1/mess-bills/?status=Pending" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get student's paid bills
curl -X GET "http://localhost/api/v1/mess-bills/?student=5&status=Paid" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🍽️ Mess Endpoint Filters

### Menu - `http://localhost/api/v1/mess-menu/`

| Parameter | Type | Example |
|-----------|------|---------|
| `day` | Choice | `?day=Monday` |
| `meal` | Text (contains) | `?meal=dal` |

#### Menu Examples

```bash
# Get Monday menu
curl -X GET "http://localhost/api/v1/mess-menu/?day=Monday" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search for meals
curl -X GET "http://localhost/api/v1/mess-menu/?meal=sambar" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Registrations - `http://localhost/api/v1/mess-registrations/`

| Parameter | Type | Example |
|-----------|------|---------|
| `student` | Choice (ID) | `?student=5` |
| `plan` | Text (contains) | `?plan=monthly` |
| `status` | Choice | `?status=Active` |
| `registration_date_after` | Date | `?registration_date_after=2024-01-01` |

#### Registration Examples

```bash
# Get active registrations
curl -X GET "http://localhost/api/v1/mess-registrations/?status=Active" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get student's registrations
curl -X GET "http://localhost/api/v1/mess-registrations/?student=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔗 Complex Filter Examples

### Find All Unpaid Bills for a Student in a Month
```bash
# Mess bills
curl -X GET "http://localhost/api/v1/mess-bills/?student=5&status=Pending&month=3&year=2024" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Room bills
curl -X GET "http://localhost/api/v1/room-bills/?student=5&status=Pending" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Find Available Rooms in a Price Range
```bash
curl -X GET "http://localhost/api/v1/rooms/?status=Available&monthly_rent_min=5000&monthly_rent_max=8000&ordering=monthly_rent" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Find Students Allocated in Last 30 Days
```bash
curl -X GET "http://localhost/api/v1/allocations/?allocation_date_after=2024-02-29&status=Active&ordering=-allocation_date" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Filtering Best Practices

### ✅ Do's
1. **Combine related filters** - Status + date range for better results
2. **Use ordering** - Sort by relevant fields for easier analysis
3. **Test in browser first** - Try URLs in browser before embedding in code
4. **Use pagination** - Always combine filtering with `?page=1`
5. **Cache results** - Don't re-filter same data repeatedly

### ❌ Don'ts
1. **Don't fetch all data** - Always filter when possible
2. **Don't use slow filters** - Avoid text search on large datasets
3. **Don't forget URL encoding** - Spaces → `%20`, special chars properly encoded
4. **Don't assume field names** - Check API documentation for exact names

---

## 💻 Using Filters in Code

### Python
```python
import requests

TOKEN = "your_jwt_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Filter students
response = requests.get(
    "http://localhost/api/v1/students/?department=CSE&year=2&ordering=name",
    headers=headers
)

students = response.json()['results']
for student in students:
    print(f"{student['name']} - {student['id_number']}")
```

### JavaScript
```javascript
const TOKEN = "your_jwt_token";
const headers = { Authorization: `Bearer ${TOKEN}` };

// Filter bills
const response = await fetch(
    "http://localhost/api/v1/mess-bills/?student=5&status=Pending",
    { headers }
);

const data = await response.json();
console.log(`Total pending bills: ${data['count']}`);
data['results'].forEach(bill => {
    console.log(`- Amount: ${bill['amount']}, Month: ${bill['month']}`);
});
```

---

## ⚠️ Common Issues

### Issue: Empty Results
- Check filter values are correct
- Verify you're using exact field names
- Ensure filters match data in database

### Issue: Too Many Results
- Add more specific filters
- Use date ranges to narrow down
- Combine multiple filters

### Issue: Date Format Not Working
- Use ISO format: `YYYY-MM-DD`
- Example: `?created_after=2024-03-01`

### Issue: Special Characters in Search
- URL encode special characters
- Space = `%20`, `&` = `%26`, etc.
- Use `?search=john%20doe`

---

## 📚 Related Documentation

- [API Examples](./API_EXAMPLES.md)
- [Pagination Guide](./PAGINATION_GUIDE.md)
- [Project Setup](./PROJECT_SETUP.md)

---

**For more API details, see [API_EXAMPLES.md](./API_EXAMPLES.md)**
