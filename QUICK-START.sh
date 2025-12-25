#!/bin/bash

# ClarityAP - Quick Start Script
# Run this on your local machine to start integration testing

set -e

echo "========================================="
echo "ClarityAP - Quick Start"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}→${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
print_header "Checking Prerequisites"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python: $PYTHON_VERSION"
else
    print_error "Python 3 not found!"
    exit 1
fi

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js: $NODE_VERSION"
else
    print_error "Node.js not found!"
    exit 1
fi

if command -v psql &> /dev/null; then
    print_success "PostgreSQL client installed"
else
    print_warning "PostgreSQL client not found"
fi

echo ""

# Option selection
print_header "Choose Your Setup Method"
echo ""
echo "1) Docker Compose (Recommended - includes PostgreSQL)"
echo "2) Local PostgreSQL (requires PostgreSQL running)"
echo "3) Cloud Database (Supabase/Railway)"
echo "4) Skip database setup (API testing only)"
echo ""
read -p "Select option [1-4]: " SETUP_OPTION

case $SETUP_OPTION in
    1)
        print_header "Docker Compose Setup"
        if ! command -v docker &> /dev/null; then
            print_error "Docker not found! Please install Docker first."
            print_info "Visit: https://docs.docker.com/get-docker/"
            exit 1
        fi

        print_info "Starting services with Docker Compose..."
        docker-compose up -d

        print_info "Waiting for PostgreSQL to be ready..."
        sleep 5

        print_info "Running database migrations..."
        docker-compose exec backend alembic upgrade head

        print_success "Services started!"
        print_info "Backend: http://localhost:8000"
        print_info "Frontend: http://localhost:3000"
        print_info "API Docs: http://localhost:8000/docs"
        ;;

    2)
        print_header "Local PostgreSQL Setup"

        # Check if PostgreSQL is running
        if pg_isready &> /dev/null; then
            print_success "PostgreSQL is running"
        else
            print_warning "PostgreSQL doesn't seem to be running"
            print_info "Try: sudo service postgresql start"
            read -p "Press Enter when PostgreSQL is running..."
        fi

        # Create database
        print_info "Creating database..."
        createdb -U postgres clarityap 2>/dev/null && print_success "Database created" || print_info "Database already exists"

        # Setup backend
        print_info "Setting up backend..."
        cd clarity-api

        if [ ! -d "venv" ]; then
            python3 -m venv venv
            print_success "Virtual environment created"
        fi

        source venv/bin/activate
        pip install -r requirements.txt > /dev/null 2>&1
        print_success "Dependencies installed"

        # Run migrations
        print_info "Running database migrations..."
        alembic upgrade head
        print_success "Migrations complete"

        cd ..

        # Setup frontend
        print_info "Setting up frontend..."
        cd clarity-web

        if [ ! -d "node_modules" ]; then
            npm install > /dev/null 2>&1
            print_success "Frontend dependencies installed"
        fi

        # Create .env.local if not exists
        if [ ! -f ".env.local" ]; then
            echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
            print_success ".env.local created"
        fi

        cd ..

        print_success "Setup complete!"
        echo ""
        print_header "Next Steps"
        echo ""
        echo "Terminal 1 - Start Backend:"
        echo "  cd clarity-api"
        echo "  source venv/bin/activate"
        echo "  uvicorn app.main:app --reload"
        echo ""
        echo "Terminal 2 - Start Frontend:"
        echo "  cd clarity-web"
        echo "  npm run dev"
        echo ""
        echo "Terminal 3 - Run Tests:"
        echo "  ./run_e2e_tests.sh"
        echo ""
        ;;

    3)
        print_header "Cloud Database Setup"
        echo ""
        print_info "Using cloud database (Supabase/Railway/Neon)"
        echo ""
        echo "Get your database connection string from:"
        echo "  - Supabase: https://supabase.com (Free tier available)"
        echo "  - Railway: https://railway.app"
        echo "  - Neon: https://neon.tech"
        echo ""
        read -p "Enter your DATABASE_URL: " DATABASE_URL

        # Update .env
        cd clarity-api
        if [ -f ".env" ]; then
            sed -i.bak "s|^DATABASE_URL=.*|DATABASE_URL=$DATABASE_URL|" .env
            print_success ".env updated"
        fi

        # Setup and run migrations
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi

        source venv/bin/activate
        pip install -r requirements.txt > /dev/null 2>&1

        print_info "Running migrations on cloud database..."
        alembic upgrade head
        print_success "Cloud database setup complete!"

        cd ..
        ;;

    4)
        print_header "Skipping Database Setup"
        print_warning "Some features will not work without a database"
        print_info "You can test API endpoints documentation at /docs"
        ;;

    *)
        print_error "Invalid option"
        exit 1
        ;;
esac

echo ""
print_header "Integration Testing"
echo ""
print_info "Run automated E2E tests:"
echo "  ./run_e2e_tests.sh"
echo ""
print_info "Manual testing checklist:"
echo "  See INTEGRATION-TESTING-GUIDE.md"
echo ""
print_info "Test with international invoices:"
echo "  test_data/invoice-india-gst.txt"
echo "  test_data/invoice-us-sales-tax.txt"
echo "  test_data/invoice-eu-vat.txt"
echo "  test_data/invoice-uk-vat.txt"
echo ""
print_success "Ready to test! 🚀"
