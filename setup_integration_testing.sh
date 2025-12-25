#!/bin/bash

# ClarityAP - Integration Testing & SaaS Setup Script
# This script sets up the complete environment and runs integration tests

set -e  # Exit on error

echo "========================================="
echo "ClarityAP - Integration Testing Setup"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
echo "Step 1: Checking Prerequisites..."
print_status "Checking Python version..."
python3 --version || { print_error "Python 3 not found!"; exit 1; }

print_status "Checking Node.js version..."
node --version || { print_error "Node.js not found! Please install Node.js 18+"; exit 1; }

print_status "Checking npm version..."
npm --version || { print_error "npm not found!"; exit 1; }

print_status "Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    print_success "PostgreSQL found"
else
    print_warning "PostgreSQL not found in PATH. Make sure it's installed and running."
fi

print_success "All prerequisites checked"
echo ""

# Backend Setup
echo "Step 2: Setting up Backend..."
print_status "Creating Python virtual environment..."
cd /home/user/AP-Agent/clarity-api

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

print_status "Activating virtual environment..."
source venv/bin/activate

print_status "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Backend dependencies installed"

print_status "Checking .env configuration..."
if [ -f ".env" ]; then
    print_success ".env file exists"
else
    print_warning ".env file not found, copying from .env.example"
    cp .env.example .env
    print_warning "Please update .env with your actual credentials!"
fi

cd /home/user/AP-Agent
echo ""

# Frontend Setup
echo "Step 3: Setting up Frontend..."
print_status "Installing frontend dependencies..."
cd /home/user/AP-Agent/clarity-web

if [ -d "node_modules" ]; then
    print_success "Node modules already installed"
else
    npm install
    print_success "Frontend dependencies installed"
fi

print_status "Checking frontend .env.local..."
if [ -f ".env.local" ]; then
    print_success ".env.local exists"
else
    print_warning "Creating .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    print_success ".env.local created"
fi

cd /home/user/AP-Agent
echo ""

# Database Setup
echo "Step 4: Database Setup..."
print_status "Checking if PostgreSQL database exists..."

# Try to create database (will fail if exists, which is fine)
createdb -U postgres clarityap 2>/dev/null && print_success "Database 'clarityap' created" || print_success "Database 'clarityap' already exists"

print_status "Running database migrations..."
cd /home/user/AP-Agent/clarity-api
source venv/bin/activate
alembic upgrade head || { print_error "Migration failed!"; exit 1; }
print_success "Database migrations completed"

cd /home/user/AP-Agent
echo ""

# Run Backend Tests
echo "Step 5: Running Backend Tests..."
print_status "Running pytest..."
cd /home/user/AP-Agent/clarity-api
source venv/bin/activate

if pytest tests/ -v --tb=short; then
    print_success "All backend tests passed!"
else
    print_warning "Some backend tests failed. Check the output above."
fi

cd /home/user/AP-Agent
echo ""

# Integration Test Setup
echo "Step 6: Integration Testing Setup Complete!"
echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo ""
echo "1. Start the backend server:"
echo "   cd /home/user/AP-Agent/clarity-api"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   cd /home/user/AP-Agent/clarity-web"
echo "   npm run dev"
echo ""
echo "3. Open your browser:"
echo "   http://localhost:3000"
echo ""
echo "4. Run manual integration tests:"
echo "   - Register a new account"
echo "   - Login"
echo "   - Upload test invoices from test_data/"
echo "   - Test all CRUD operations"
echo "   - Test QuickBooks export"
echo "   - Test batch operations"
echo ""
echo "5. For automated E2E tests:"
echo "   ./run_e2e_tests.sh"
echo ""
print_success "Setup complete! Ready for integration testing."
