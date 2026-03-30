# 📚 API Documentation with Examples

Complete guide to using the Hostel Management System API with curl examples.

---

## 🔐 Authentication

All API endpoints (except token endpoints) require JWT authentication.

### 1️⃣ Get Access Token
```bash
curl -X POST http://localhost/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Save the `access` token for API calls.

### 2️⃣ Refresh Token (when access expires)
```bash
curl -X POST http://localhost/api/v1/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your_refresh_token"
  }'
```

---

## � Pagination

All list endpoints return paginated results (50 items per page by default).

### Get First Page
```bash
curl -X GET http://localhost/api/v1/students/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Specific Page
```bash
# Page 2
curl -X GET http://localhost/api/v1/students/?page=2 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Page 5
curl -X GET http://localhost/api/v1/students/?page=5 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Combine Pagination with Search & Ordering
```bash
# Search for "john" AND order by year AND get page 2
curl -X GET "http://localhost/api/v1/students/?search=john&ordering=year&page=2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response includes:**
```json
{
  "count": 150,
  "next": "http://localhost/api/v1/students/?page=2",
  "previous": null,
  "results": [...]
}
```

📚 **Full Pagination Guide:** [PAGINATION_GUIDE.md](./PAGINATION_GUIDE.md)

---

## �📋 API Endpoints

### Students

#### List All Students
```bash
curl -X GET http://localhost/api/v1/students/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get Single Student
```bash
curl -X GET http://localhost/api/v1/students/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Create Student
```bash
curl -X POST http://localhost/api/v1/students/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_number": "STU001",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "department": "CSE",
    "year": 2
  }'
```

#### Update Student
```bash
curl -X PUT http://localhost/api/v1/students/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "9999999999",
    "year": 3
  }'
```

#### Delete Student
```bash
curl -X DELETE http://localhost/api/v1/students/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### Hostel Blocks

#### List All Blocks
```bash
curl -X GET http://localhost/api/v1/blocks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get Single Block
```bash
curl -X GET http://localhost/api/v1/blocks/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Create Block
```bash
curl -X POST http://localhost/api/v1/blocks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Block A",
    "block_type": "Boys",
    "total_rooms": 50,
    "warden": 1
  }'
```

---

### Rooms

#### List All Rooms
```bash
curl -X GET http://localhost/api/v1/rooms/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get Single Room
```bash
curl -X GET http://localhost/api/v1/rooms/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Create Room
```bash
curl -X POST http://localhost/api/v1/rooms/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "block": 1,
    "room_number": "A101",
    "capacity": 2,
    "occupancy": 0,
    "room_type": "Standard"
  }'
```

---

### Room Allocations

#### List All Allocations
```bash
curl -X GET http://localhost/api/v1/allocations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Allocate Room to Student
```bash
curl -X POST http://localhost/api/v1/allocations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student": 1,
    "room": 1,
    "allocation_date": "2024-01-15"
  }'
```

#### Vacate Room (Mark as vacant)
```bash
curl -X PATCH http://localhost/api/v1/allocations/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false,
    "vacate_date": "2024-12-31"
  }'
```

---

### Mess Menu

#### Get Mess Menu
```bash
curl -X GET http://localhost/api/v1/mess-menu/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Update Mess Menu
```bash
curl -X POST http://localhost/api/v1/mess-menu/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "monday_menu": "Sambar, Rice",
    "tuesday_menu": "Dal, Roti",
    "wednesday_menu": "Curry, Rice",
    "thursday_menu": "Biryani",
    "friday_menu": "Chinese",
    "saturday_menu": "Chaat",
    "sunday_menu": "Paneer Curry"
  }'
```

---

### Mess Registration

#### List Student Mess Registrations
```bash
curl -X GET http://localhost/api/v1/mess-registrations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Register Student for Mess
```bash
curl -X POST http://localhost/api/v1/mess-registrations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student": 1,
    "registration_date": "2024-01-15",
    "status": "Active"
  }'
```

---

### Mess Bills

#### List All Mess Bills
```bash
curl -X GET http://localhost/api/v1/mess-bills/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get Single Mess Bill
```bash
curl -X GET http://localhost/api/v1/mess-bills/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Generate Mess Bill (Admin Only)
```bash
curl -X POST http://localhost/api/v1/mess-bills/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student": 1,
    "month": "January",
    "year": 2024,
    "total_days": 25,
    "per_day_charge": 100,
    "total_amount": 2500
  }'
```

---

### Room Bills

#### List All Room Bills
```bash
curl -X GET http://localhost/api/v1/room-bills/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get Single Room Bill
```bash
curl -X GET http://localhost/api/v1/room-bills/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📊 Complete Example Workflow

### Step 1: Login
```bash
# Get token
curl -X POST http://localhost/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}' > token.json

# Extract token (Linux/Mac)
TOKEN=$(cat token.json | grep -o '"access":"[^"]*' | cut -d'"' -f4)
echo $TOKEN
```

### Step 2: Create a Block
```bash
curl -X POST http://localhost/api/v1/blocks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Block B",
    "block_type": "Girls",
    "total_rooms": 40
  }' > block.json
```

### Step 3: Create Rooms in Block
```bash
BLOCK_ID=$(cat block.json | grep -o '"id":[0-9]*' | cut -d':' -f2)

for i in {1..40}; do
  curl -X POST http://localhost/api/v1/rooms/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"block\": $BLOCK_ID,
      \"room_number\": \"B$((100 + $i))\",
      \"capacity\": 2,
      \"occupancy\": 0
    }"
done
```

### Step 4: Create Student
```bash
curl -X POST http://localhost/api/v1/students/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_number": "STU0001",
    "name": "Alice Smith",
    "email": "alice@example.com",
    "phone": "9876543210",
    "department": "EEE",
    "year": 1
  }' > student.json

STUDENT_ID=$(cat student.json | grep -o '"id":[0-9]*' | cut -d':' -f2)
```

### Step 5: Allocate Room to Student
```bash
curl -X POST http://localhost/api/v1/allocations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"student\": $STUDENT_ID,
    \"room\": 1,
    \"allocation_date\": \"2024-01-15\"
  }"
```

---

## 🚀 Using with Postman

1. **Create New Request** → POST
2. **URL:** `http://localhost/api/v1/token/`
3. **Body (JSON):**
   ```json
   {
     "username": "admin",
     "password": "your_password"
   }
   ```
4. **Send** → Copy `access` token
5. **For subsequent requests:**
   - Add header: `Authorization: Bearer <your_access_token>`
   - Use the URLs from examples above

---

## 📖 Interactive API Documentation

Visit these URLs in your browser:
- **Swagger UI:** `http://localhost/api/v1/docs/`
- **ReDoc:** `http://localhost/api/v1/redoc/`
- **Schema:** `http://localhost/api/v1/schema/`

These provide interactive API documentation with try-it-out functionality.

---

## ⚠️ Common Issues

### 401 Unauthorized
**Problem:** Missing or invalid token
```bash
# Solution: Get new token and add to header
Authorization: Bearer YOUR_VALID_TOKEN
```

### 403 Forbidden
**Problem:** User doesn't have permission for this action
- Students can only view/edit their own data
- Admins have full access
- Wardens can manage their assigned blocks

### 404 Not Found
**Problem:** Resource doesn't exist
```bash
# Solution: Check the ID
curl -X GET http://localhost/api/v1/students/ \
  -H "Authorization: Bearer YOUR_TOKEN"
# Use a valid ID from the response
```

### 400 Bad Request
**Problem:** Invalid data format
```bash
# Solution: Check required fields and data types
curl -X POST http://localhost/api/v1/students/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_number": "STU0001",
    "name": "John",
    "email": "john@example.com",
    "phone": "9876543210",
    "department": "CSE",
    "year": 1
  }'
```

---

## 💡 Tips

- Always include `Authorization` header with `Bearer TOKEN`
- Use `-H "Content-Type: application/json"` for POST/PUT/PATCH
- Test with `-v` flag for verbose output: `curl -v ...`
- Save responses to files: `curl ... > response.json`
- Use pipes to extract data: `curl ... | grep "id"`

---

**For more details, see [PROJECT_SETUP.md](./PROJECT_SETUP.md#-api-endpoints)**
