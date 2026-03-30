#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Hostel Management System - Docker Test Suite${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to test service health
test_service() {
    local service=$1
    local test_cmd=$2
    local description=$3
    
    echo -ne "${YELLOW}Testing ${description}...${NC} "
    
    if eval "$test_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Track results
PASSED=0
FAILED=0

echo -e "${BLUE}Step 1: Checking Docker Installation${NC}"
echo "=========================================="

test_service "docker" "docker --version" "Docker version"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

test_service "docker-compose" "docker-compose --version" "Docker Compose version"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

test_service "daemon" "docker ps" "Docker daemon"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

echo ""
echo -e "${BLUE}Step 2: Building Docker Images${NC}"
echo "======================================"

echo "This may take 3-5 minutes..."
if docker-compose build > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Images built successfully${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗ Failed to build images${NC}"
    FAILED=$((FAILED+1))
    exit 1
fi

echo ""
echo -e "${BLUE}Step 3: Starting Docker Containers${NC}"
echo "===================================="

docker-compose up -d > /dev/null 2>&1

echo "Waiting for services to start (30 seconds)..."
sleep 30

test_service "web" "docker-compose ps | grep hostel_web | grep running" "Django web service"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

test_service "db" "docker-compose ps | grep hostel_db | grep running" "PostgreSQL database"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

test_service "redis" "docker-compose ps | grep hostel_redis | grep running" "Redis cache"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

test_service "worker" "docker-compose ps | grep hostel_celery_worker | grep running" "Celery worker"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

test_service "beat" "docker-compose ps | grep hostel_celery_beat | grep running" "Celery beat"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

test_service "nginx" "docker-compose ps | grep hostel_nginx | grep running" "Nginx reverse proxy"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

echo ""
echo -e "${BLUE}Step 4: Testing Services Health${NC}"
echo "=================================="

test_service "postgres" "docker-compose exec db psql -U postgres -c 'SELECT 1' > /dev/null" "PostgreSQL connection"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

test_service "redis" "docker-compose exec redis redis-cli ping | grep -q PONG" "Redis connection"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

test_service "django" "docker-compose exec web python manage.py check > /dev/null" "Django system check"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

echo ""
echo -e "${BLUE}Step 5: Running Migrations${NC}"
echo "==========================="

if docker-compose exec web python manage.py migrate > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Migrations applied successfully${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗ Failed to apply migrations${NC}"
    FAILED=$((FAILED+1))
fi

echo ""
echo -e "${BLUE}Step 6: Creating Test Superuser${NC}"
echo "================================="

# Create superuser if not exists
docker-compose exec web python manage.py shell << EOF > /dev/null 2>&1
from django.contrib.auth.models import User
if not User.objects.filter(username='testadmin').exists():
    User.objects.create_superuser('testadmin', 'test@local.com', 'testpass123')
    print('Superuser created')
else:
    print('Superuser already exists')
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Superuser ready (testadmin/testpass123)${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗ Failed to create superuser${NC}"
    FAILED=$((FAILED+1))
fi

echo ""
echo -e "${BLUE}Step 7: Collecting Static Files${NC}"
echo "================================"

if docker-compose exec web python manage.py collectstatic --noinput > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Static files collected${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗ Failed to collect static files${NC}"
    FAILED=$((FAILED+1))
fi

echo ""
echo -e "${BLUE}Step 8: Testing API Endpoints${NC}"
echo "=============================="

test_service "api_root" "curl -s http://localhost/api/ | grep -q 'api'" "API root endpoint"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

test_service "swagger" "curl -s http://localhost/api/schema/swagger-ui/ | grep -q 'Swagger'" "Swagger UI"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

test_service "admin" "curl -s http://localhost/admin | grep -q 'Django administration'" "Django admin"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

echo ""
echo -e "${BLUE}Step 9: Testing Celery Tasks${NC}"
echo "=============================="

# Test Celery task
TASK_RESULT=$(docker-compose exec web python manage.py shell << EOF
from apps.api.tasks import test_task
result = test_task.delay("Docker test!")
print(result.id)
EOF
)

if [ ! -z "$TASK_RESULT" ]; then
    echo -e "${GREEN}✓ Celery task submitted (ID: $TASK_RESULT)${NC}"
    PASSED=$((PASSED+1))
    
    # Wait for task to process
    sleep 3
    
    test_service "task_result" "docker-compose exec redis redis-cli KEYS \"celery*\" | grep -q celery" "Task result in Redis"
    if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi
else
    echo -e "${RED}✗ Failed to submit Celery task${NC}"
    FAILED=$((FAILED+1))
fi

echo ""
echo -e "${BLUE}Step 10: Checking Logs for Errors${NC}"
echo "=================================="

# Check for critical errors
ERROR_COUNT=$(docker-compose logs | grep -i "error\|exception\|failed" | grep -v "Traceback" | wc -l)

if [ $ERROR_COUNT -lt 5 ]; then
    echo -e "${GREEN}✓ No critical errors found ($ERROR_COUNT warnings)${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗ Found $ERROR_COUNT errors${NC}"
    docker-compose logs | grep -i "error\|exception" | head -10
    FAILED=$((FAILED+1))
fi

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Test Results${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Docker setup is working correctly! 🎉${NC}"
    echo ""
    echo "You can now access:"
    echo "  - Admin Panel: ${BLUE}http://localhost/admin${NC}"
    echo "  - API Root: ${BLUE}http://localhost/api/${NC}"
    echo "  - Swagger UI: ${BLUE}http://localhost/api/schema/swagger-ui/${NC}"
    echo ""
    echo "Credentials:"
    echo "  - Username: testadmin"
    echo "  - Password: testpass123"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Check the output above.${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check service logs: ${YELLOW}docker-compose logs <service>${NC}"
    echo "  2. Restart services: ${YELLOW}docker-compose restart${NC}"
    echo "  3. Rebuild images: ${YELLOW}docker-compose build --no-cache${NC}"
    echo ""
    exit 1
fi
