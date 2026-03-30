# API Pagination Guide

The Hostel Management System API implements pagination to handle large datasets efficiently.

## 📋 Pagination Overview

All list endpoints return paginated results with a default page size of **50 items per page**.

### Current Configuration
- **Type:** Page Number Pagination
- **Default Page Size:** 50 items
- **Query Parameter:** `?page=1`

---

## 🔍 Pagination Response Format

When you request a list endpoint, you get a response like:

```json
{
    "count": 150,
    "next": "http://localhost/api/v1/students/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "John Doe",
            ...
        },
        {
            "id": 2,
            "name": "Jane Smith",
            ...
        }
    ]
}
```

### Response Fields
- `count` - Total number of items in the database
- `next` - URL to next page (null if no more pages)
- `previous` - URL to previous page (null if on first page)
- `results` - Array of items for current page

---

## 📑 Pagination Examples

### Get First Page (Default)
```bash
curl -X GET http://localhost/api/v1/students/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Specific Page
```bash
# Get page 2
curl -X GET http://localhost/api/v1/students/?page=2 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get page 5
curl -X GET http://localhost/api/v1/students/?page=5 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Combine Pagination with Search
```bash
# Search for students AND get page 2
curl -X GET "http://localhost/api/v1/students/?search=john&page=2" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Combine Pagination with Ordering
```bash
# Order by name AND get page 3
curl -X GET "http://localhost/api/v1/students/?ordering=name&page=3" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Combine All: Search + Order + Paginate
```bash
# Search for "john", order by year, get page 2
curl -X GET "http://localhost/api/v1/students/?search=john&ordering=year&page=2" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Pagination Across All Endpoints

All these endpoints support pagination:

| Endpoint | URL |
|----------|-----|
| Students | `GET /api/v1/students/?page=1` |
| Blocks | `GET /api/v1/blocks/?page=1` |
| Rooms | `GET /api/v1/rooms/?page=1` |
| Allocations | `GET /api/v1/allocations/?page=1` |
| Mess Registrations | `GET /api/v1/mess-registrations/?page=1` |
| Mess Bills | `GET /api/v1/mess-bills/?page=1` |
| Room Bills | `GET /api/v1/room-bills/?page=1` |
| Mess Menu | `GET /api/v1/mess-menu/?page=1` |

---

## 💻 Working with Pagination in Code

### Python Requests
```python
import requests

TOKEN = "your_jwt_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Fetch first page
response = requests.get(
    "http://localhost/api/v1/students/?page=1",
    headers=headers
)
data = response.json()

print(f"Total items: {data['count']}")
print(f"Items on page: {len(data['results'])}")
print(f"Next page: {data['next']}")

# Process items
for student in data['results']:
    print(f"- {student['name']} ({student['id_number']})")

# Fetch next page if available
if data['next']:
    next_response = requests.get(data['next'], headers=headers)
```

### JavaScript (Node.js)
```javascript
const axios = require('axios');

const TOKEN = 'your_jwt_token';
const headers = { Authorization: `Bearer ${TOKEN}` };

async function fetchAllStudents() {
    let page = 1;
    let allStudents = [];
    let hasMore = true;

    while (hasMore) {
        const response = await axios.get(
            `http://localhost/api/v1/students/?page=${page}`,
            { headers }
        );
        
        const { count, next, results } = response.data;
        allStudents = allStudents.concat(results);
        
        console.log(`Fetched page ${page} - Total: ${count}`);
        
        hasMore = next !== null;
        page++;
    }

    return allStudents;
}

fetchAllStudents().then(students => {
    console.log(`Total students: ${students.length}`);
});
```

### JavaScript (Browser/Fetch)
```javascript
const TOKEN = 'your_jwt_token';
const headers = { Authorization: `Bearer ${TOKEN}` };

async function getPage(pageNumber) {
    const response = await fetch(
        `http://localhost/api/v1/students/?page=${pageNumber}`,
        { headers }
    );
    return response.json();
}

// Get page 1
getPage(1).then(data => {
    console.log(`Total items: ${data.count}`);
    console.log(`Items: ${data.results.length}`);
    console.log('Students:', data.results);
});
```

---

## 🎯 Pagination Best Practices

### ✅ Do's
1. **Always check the response structure** - Look for `count`, `next`, `results`
2. **Use `next` field** - Follow the `next` link instead of manually incrementing pages
3. **Cache results** - Don't re-fetch the same page multiple times
4. **Handle `null` next** - Gracefully stop when `next` is null (end of results)
5. **Show page info to users** - Display "Page 2 of 5" or similar

### ❌ Don'ts
1. **Don't assume page numbers** - Always use the `next` link provided
2. **Don't request page 999** - Returns empty results, waste of API calls
3. **Don't ignore total count** - Use `count` to calculate total pages: `ceil(count / 50)`
4. **Don't modify page size in client** - It's fixed by server (50 items/page)

---

## 📈 Calculate Pagination Info

```python
# From API response
total_items = response['count']  # e.g., 150
items_per_page = 50
current_page = 1  # extracted from URL parameter

# Calculate pagination info
total_pages = (total_items + items_per_page - 1) // items_per_page
has_next = response['next'] is not None
has_previous = response['previous'] is not None

print(f"Page {current_page} of {total_pages}")
print(f"Total items: {total_items}")
print(f"Has next: {has_next}")
print(f"Has previous: {has_previous}")
```

---

## ⚠️ Common Issues

### Problem: Empty Results Page
```bash
curl -X GET http://localhost/api/v1/students/?page=999 \
  -H "Authorization: Bearer YOUR_TOKEN"
```
**Solution:** Check total items and requested page:
```python
total_pages = (data['count'] + 49) // 50  # Round up
if requested_page > total_pages:
    print(f"Page {requested_page} doesn't exist! Max: {total_pages}")
```

### Problem: No Next Link
This means you're on the last page - this is expected behavior, not an error.

### Problem: Status 404 on Next Link
The server may have deleted items. Re-fetch page 1 and continue from there.

---

## 🔗 Integration with UI

### Example: Pagination Navigation
```html
<div class="pagination">
    <button onclick="previousPage()" [disabled]="!data.previous">
        ← Previous
    </button>
    <span>Page {{ currentPage }} of {{ totalPages }}</span>
    <button onclick="nextPage()" [disabled]="!data.next">
        Next →
    </button>
</div>
```

---

## 📚 Related Documentation

- [API Documentation](./API_EXAMPLES.md)
- [Search & Filter Guide](./API_EXAMPLES.md#-complete-example-workflow)
- [Error Handling Guide](./PROJECT_SETUP.md#-troubleshooting)

---

**For more API details, see [PROJECT_SETUP.md](./PROJECT_SETUP.md) or [API_EXAMPLES.md](./API_EXAMPLES.md)**
