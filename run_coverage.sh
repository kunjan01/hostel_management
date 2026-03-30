#!/bin/bash
# Test Coverage Report Script
# Generates coverage report and displays coverage percentage

echo "🧪 Running pytest with coverage..."
python -m pytest --cov=apps --cov-report=html --cov-report=term-missing

# Extract coverage percentage from last output
COVERAGE=$(python -m pytest --cov=apps --cov-report=term-missing -q 2>&1 | grep TOTAL | awk '{print $NF}' | sed 's/%//')

echo ""
echo "=========================================="
echo "📊 Test Coverage Report"
echo "=========================================="
echo "Coverage: ${COVERAGE}%"
echo ""
echo "📁 HTML Report: open htmlcov/index.html"
echo ""
echo "✅ Tests Summary:"
python -m pytest --co -q apps 2>/dev/null | wc -l | xargs echo "Total test files:"

echo ""
echo "💡 Tips:"
echo "  - Full report: open htmlcov/index.html"
echo "  - Run single test: pytest apps/api/tests.py::TestClassName::test_method"
echo "  - Run with verbose: pytest -v"
echo "=========================================="
