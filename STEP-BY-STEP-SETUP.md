# ClarityAP - Step-by-Step Setup & Testing Guide

## 🎯 Complete Guide from GitHub to Running Tests

Follow these steps **exactly** to get ClarityAP running and test it.

---

## 📋 Prerequisites Check

Before starting, verify you have these installed:

### Check What You Have:

**1. Check Python:**
```bash
python3 --version
```
✅ Need: Python 3.9 or higher
❌ Don't have it? Install from: https://www.python.org/downloads/

**2. Check Node.js:**
```bash
node --version
```
✅ Need: Node.js 18 or higher
❌ Don't have it? Install from: https://nodejs.org/

**3. Check Git:**
```bash
git --version
```
✅ Should see: git version 2.x.x
❌ Don't have it? Install from: https://git-scm.com/downloads

**4. Check PostgreSQL (Optional - we'll help you install):**
```bash
psql --version
```
✅ Great if you have it!
❌ Don't worry, we'll set it up in Step 3

**5. Check Docker (Optional but recommended):**
```bash
docker --version
docker-compose --version
```
✅ Best option if you have both!
❌ Don't have it? We'll use PostgreSQL instead

---

## 🚀 Step 1: Download from GitHub

### Option A: If you have the repository URL

```bash
# 1. Open Terminal (Mac/Linux) or Command Prompt (Windows)

# 2. Navigate to where you want the project
cd ~/Documents  # or any folder you prefer

# 3. Clone the repository
git clone https://github.com/YOUR-USERNAME/AP-Agent.git

# 4. Enter the project folder
cd AP-Agent

# 5. Checkout the correct branch
git checkout claude/setup-backend-dev-01FwJmG2Rkv27vt6YY3mWUs1

# 6. Verify you have all files
ls -la
```

### Option B: If you're already in the project

```bash
# 1. Make sure you're in the project folder
cd /path/to/AP-Agent

# 2. Pull latest changes
git pull origin claude/setup-backend-dev-01FwJmG2Rkv27vt6YY3mWUs1

# 3. Verify you're on the right branch
git branch

# Should show: * claude/setup-backend-dev-01FwJmG2Rkv27vt6YY3mWUs1
```

---

## 🔧 Step 2: Choose Your Setup Method

You have 3 options. **Pick the one that matches your system:**

### 🎯 OPTION A: Docker (Easiest - Recommended if you have Docker)

**Why this is best:**
- Everything works automatically
- PostgreSQL included
- No complex setup needed
- Works the same on Mac, Windows, Linux

**Requirements:**
- Docker Desktop installed
- Docker Compose installed

**Go to:** [Step 3A - Docker Setup](#step-3a-docker-setup)

---

### 🎯 OPTION B: Local PostgreSQL (If you have or can install PostgreSQL)

**Why choose this:**
- Full control over database
- Good for development
- Faster than Docker

**Requirements:**
- PostgreSQL installed
- Can start PostgreSQL service

**Go to:** [Step 3B - Local PostgreSQL Setup](#step-3b-local-postgresql-setup)

---

### 🎯 OPTION C: Cloud Database (No local database needed)

**Why choose this:**
- No PostgreSQL installation needed
- Works on any computer
- Free tier available

**Requirements:**
- Internet connection
- 5 minutes to set up free database

**Go to:** [Step 3C - Cloud Database Setup](#step-3c-cloud-database-setup)

---

## 📦 Step 3A: Docker Setup

### 3A.1: Verify Docker is Running

```bash
# Check Docker is running
docker ps

# If you get an error, start Docker Desktop application
```

### 3A.2: Start All Services

```bash
# This starts PostgreSQL, Backend, and Frontend
docker-compose up -d

# Wait for services to start (about 30 seconds)
```

### 3A.3: Check Services are Running

```bash
docker-compose ps

# You should see:
# - postgres (running)
# - backend (running)
# - frontend (running)
```

### 3A.4: Run Database Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 3A.5: Verify Everything Works

```bash
# Check backend is responding
curl http://localhost:8000/health

# Should see: {"status":"ok"} or similar
```

**✅ Success! Go to:** [Step 4 - Run Tests](#step-4-run-tests)

---

## 📦 Step 3B: Local PostgreSQL Setup

### 3B.1: Install PostgreSQL (if needed)

**On Mac:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**On Ubuntu/Debian Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

**On Windows:**
Download from: https://www.postgresql.org/download/windows/
Then run the installer

### 3B.2: Start PostgreSQL

**On Mac:**
```bash
brew services start postgresql@15
```

**On Ubuntu/Debian:**
```bash
sudo service postgresql start
```

**On Windows:**
```bash
# PostgreSQL should auto-start
# Or: net start postgresql-x64-15
```

### 3B.3: Verify PostgreSQL is Running

```bash
psql --version
pg_isready

# Should see: "accepting connections"
```

### 3B.4: Run the Setup Script

```bash
# Make script executable
chmod +x QUICK-START.sh

# Run it
./QUICK-START.sh

# When prompted, select option [2] Local PostgreSQL
```

The script will:
- ✅ Create Python virtual environment
- ✅ Install all backend dependencies
- ✅ Create database
- ✅ Run migrations
- ✅ Install frontend dependencies
- ✅ Configure environment files

### 3B.5: Start the Servers

**Terminal 1 - Backend:**
```bash
cd clarity-api
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd clarity-web
npm run dev
```

**Wait for both to start (about 30 seconds)**

### 3B.6: Verify Everything Works

Open browser:
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs

**✅ Success! Go to:** [Step 4 - Run Tests](#step-4-run-tests)

---

## ☁️ Step 3C: Cloud Database Setup

### 3C.1: Create Free PostgreSQL Database

**Option 1: Supabase (Recommended)**
1. Go to: https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub
4. Click "New Project"
5. Fill in:
   - Name: `clarityap`
   - Database Password: (create a strong password - SAVE THIS!)
   - Region: Choose closest to you
6. Click "Create new project"
7. Wait 2-3 minutes for database to be ready

**Option 2: Railway**
1. Go to: https://railway.app
2. Sign up with GitHub
3. Click "New Project"
4. Click "Provision PostgreSQL"
5. Copy connection string

**Option 3: Neon**
1. Go to: https://neon.tech
2. Sign up with GitHub
3. Create new project
4. Copy connection string

### 3C.2: Get Your Connection String

**For Supabase:**
1. Go to Project Settings (gear icon)
2. Click "Database"
3. Scroll to "Connection string"
4. Select "URI" tab
5. Copy the connection string
6. It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres`

**For Railway/Neon:**
- Copy the connection string from the dashboard

### 3C.3: Configure the Backend

```bash
# Edit the .env file
cd clarity-api
nano .env  # or use any text editor

# Replace the DATABASE_URL line with your connection string:
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@your-host.supabase.co:5432/postgres
```

### 3C.4: Run Setup

```bash
# Go back to project root
cd ..

# Run setup script
./QUICK-START.sh

# When prompted, select option [3] Cloud Database
# Paste your connection string when asked
```

### 3C.5: Start Servers

**Terminal 1 - Backend:**
```bash
cd clarity-api
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd clarity-web
npm run dev
```

**✅ Success! Go to:** [Step 4 - Run Tests](#step-4-run-tests)

---

## 🧪 Step 4: Run Tests

Now that everything is running, let's test it!

### 4.1: Automated API Tests

**Open a new terminal (Terminal 3):**

```bash
# Make sure you're in the project root
cd /path/to/AP-Agent

# Make the test script executable
chmod +x run_e2e_tests.sh

# Run the tests
./run_e2e_tests.sh
```

**What you should see:**
```
[TEST] Checking if API server is running...
[PASS] API server is running at http://localhost:8000
[TEST] Registering new user...
[PASS] User registration successful
[TEST] Logging in user...
[PASS] Login successful, token obtained
... (12 tests total)
```

**Expected Results:**
- ✅ All 12 tests should PASS
- ✅ Files exported: IIF and CSV files in `/tmp/`
- ✅ No errors

**If tests fail:**
1. Check backend is running (Terminal 1)
2. Check frontend is running (Terminal 2)
3. Check backend logs for errors
4. Make sure ports 3000 and 8000 are not blocked

---

### 4.2: Manual UI Tests

**Open your browser:** http://localhost:3000

#### Test 1: Registration

1. Click "Sign Up" or "Register"
2. Fill in the form:
   - First Name: `Test`
   - Last Name: `User`
   - Email: `test@example.com`
   - Company: `Test Company`
   - Password: `TestPassword123!`
   - Confirm Password: `TestPassword123!`
3. Check "I agree to Terms & Conditions"
4. Click "Create Account"

**✅ Should see:** Welcome message or redirect to dashboard

#### Test 2: Login

1. If redirected to dashboard, logout first
2. Go back to login page
3. Enter:
   - Email: `test@example.com`
   - Password: `TestPassword123!`
4. Click "Sign In"

**✅ Should see:** Dashboard page

#### Test 3: Upload Invoice (India)

1. On Dashboard, find the upload zone
2. Drag and drop: `test_data/invoice-india-gst.txt`
   OR click to browse and select it
3. Wait 3-5 seconds for AI extraction

**✅ Should see:**
- Upload successful message
- Invoice form populated with data
- GSTIN field: `29AABCT1332L1Z5`
- PAN field: `AABCT1332L`
- Currency: INR (₹)
- Total: ₹4,86,750

#### Test 4: Edit Invoice

1. Change Vendor Name to: `ABC Electronics Updated`
2. Click on line item #1
3. Change quantity from 5 to 6
4. **✅ Should see:** Amount auto-calculate to ₹3,90,000

#### Test 5: Save Invoice

1. Click "Save Changes" button
2. **✅ Should see:** Success message
3. Refresh page
4. **✅ Should see:** Changes are saved

#### Test 6: Export to QuickBooks

1. Click "Export to QuickBooks" button
2. **✅ Should see:** File downloads (invoice_XXX.iif)
3. Open the file in a text editor
4. **✅ Should see:** Properly formatted IIF content

#### Test 7: Go to Export Page

1. Click "Export" in navigation
2. **✅ Should see:**
   - Table with your invoice
   - Currency symbol: ₹
   - GSTIN and PAN badges
   - Status badge

#### Test 8: Test Search

1. Type "ABC" in search box
2. **✅ Should see:** Your invoice appears
3. Type "XYZ"
4. **✅ Should see:** No results

#### Test 9: Batch Export

1. Select checkbox next to your invoice
2. Click "Export Selected IIF"
3. **✅ Should see:** Batch IIF file downloads

#### Test 10: Test Other Countries

Upload and verify each test invoice:

**US Invoice:**
```bash
test_data/invoice-us-sales-tax.txt
```
✅ Currency: $ (USD)
✅ Tax type: Sales Tax
✅ No GSTIN/PAN fields

**EU Invoice:**
```bash
test_data/invoice-eu-vat.txt
```
✅ Currency: € (EUR)
✅ Tax type: VAT
✅ VAT Number field populated

**UK Invoice:**
```bash
test_data/invoice-uk-vat.txt
```
✅ Currency: £ (GBP)
✅ Tax type: VAT
✅ VAT Number field populated

---

## 📊 Step 5: Verify All Features

### Checklist - Mark as you test:

**Authentication:**
- [ ] Can register new account
- [ ] Password strength indicator works
- [ ] Can login with correct credentials
- [ ] Cannot login with wrong credentials
- [ ] Can logout

**Dashboard - Upload:**
- [ ] Drag and drop works
- [ ] Click to browse works
- [ ] File validation (only PDF, JPG, PNG)
- [ ] Size limit (10MB max)
- [ ] Upload progress shows
- [ ] AI extraction works (3-5 seconds)

**Dashboard - Invoice Form:**
- [ ] All fields editable
- [ ] Currency dropdown shows 8 currencies
- [ ] Tax type dropdown works
- [ ] Conditional fields appear:
  - [ ] GST → Shows GSTIN & PAN
  - [ ] VAT → Shows VAT Number
- [ ] Line items can be added
- [ ] Line items can be removed
- [ ] Auto-calculation works:
  - [ ] Line amount = qty × rate
  - [ ] Total = subtotal + tax

**Dashboard - Actions:**
- [ ] Save button works
- [ ] Export to QuickBooks works
- [ ] Delete button works (with confirmation)

**Export Page:**
- [ ] All invoices listed
- [ ] Search works
- [ ] Filter by status works
- [ ] Select all / Deselect all works
- [ ] Currency symbols correct (₹, $, €, £)
- [ ] Region badges show (GSTIN, PAN, VAT)
- [ ] Status badges show
- [ ] Single export works
- [ ] Batch export works
- [ ] CSV export works
- [ ] View button goes to dashboard
- [ ] Delete button works

**International Support:**
- [ ] Indian invoice: GSTIN, PAN, ₹ symbol
- [ ] US invoice: $ symbol, Sales Tax
- [ ] EU invoice: € symbol, VAT number
- [ ] UK invoice: £ symbol, VAT number

**Responsive Design:**
- [ ] Works on desktop (1920px)
- [ ] Works on laptop (1366px)
- [ ] Works on tablet (768px)
- [ ] Works on mobile (375px)

---

## ✅ Step 6: Success! What's Next?

If all tests pass, you have a **fully functional international invoice processing system!**

### What You've Achieved:
✅ Backend API running with authentication
✅ Frontend UI with modern design
✅ International invoice support (4 countries)
✅ Multi-currency handling (8 currencies)
✅ QuickBooks integration (IIF export)
✅ Batch operations
✅ Search & filter

### Next Steps:

**Immediate:**
1. Test with your own real invoices
2. Show it to potential users
3. Gather feedback

**This Week:**
1. Deploy to production (if ready)
2. Start Phase 1: Multi-Tenancy
3. Add team collaboration

**Next 2-3 Months:**
1. Implement SaaS features
2. Add subscription billing
3. Launch to public
4. Target: $165K ARR in Year 1

---

## 🐛 Troubleshooting

### Problem: "Port 3000 already in use"

```bash
# Find what's using port 3000
lsof -ti:3000

# Kill it
kill -9 $(lsof -ti:3000)

# Try again
cd clarity-web && npm run dev
```

### Problem: "Port 8000 already in use"

```bash
# Find what's using port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Try again
cd clarity-api && uvicorn app.main:app --reload
```

### Problem: "Module not found" errors

**Backend:**
```bash
cd clarity-api
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd clarity-web
rm -rf node_modules package-lock.json
npm install
```

### Problem: Database connection errors

```bash
# Check PostgreSQL is running
pg_isready

# If not running, start it:
# Mac:
brew services start postgresql@15

# Linux:
sudo service postgresql start

# Windows:
net start postgresql-x64-15
```

### Problem: Tests fail

1. **Check backend logs** (Terminal 1)
2. **Check frontend logs** (Terminal 2)
3. **Check browser console** (F12 → Console tab)
4. **Verify database** is running and migrated:
   ```bash
   cd clarity-api
   source venv/bin/activate
   alembic current  # Should show migration version
   ```

### Problem: Can't download from GitHub

**Check your access:**
```bash
# Test SSH connection
ssh -T git@github.com

# Or use HTTPS instead
git clone https://github.com/YOUR-USERNAME/AP-Agent.git
```

---

## 📞 Need Help?

**Documentation:**
- `PROJECT-SUMMARY.md` - Complete overview
- `INTEGRATION-TESTING-GUIDE.md` - Detailed testing guide
- `SAAS-ENHANCEMENT-PLAN.md` - SaaS roadmap
- `UI-OVERVIEW.md` - UI descriptions

**Quick Commands:**
```bash
# View backend logs
cd clarity-api && tail -f app.log

# View frontend logs
cd clarity-web && npm run dev

# Re-run setup
./QUICK-START.sh

# Re-run tests
./run_e2e_tests.sh
```

---

## 🎉 Congratulations!

If you've made it here and all tests pass, you now have a **production-ready international invoice processing system** that:

- 🌍 Supports 4 countries (India, US, EU, UK)
- 💱 Handles 8 currencies
- 📤 Exports to QuickBooks
- 🔍 Has search & filter
- 📱 Works on all devices
- 🎨 Looks professional and modern

**Ready to transform it into a full SaaS platform!**

Next milestone: Implement multi-tenancy and start generating revenue! 💰
