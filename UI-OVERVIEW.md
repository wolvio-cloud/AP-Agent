# ClarityAP - UI Overview & Visual Guide

## 📱 Page-by-Page UI Description

---

## 1. Login Page (`/auth/login`)

### Visual Layout
```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│              [Gradient Background: Blue → White → Gray]      │
│                                                               │
│                    ┌─────────────────┐                       │
│                    │   📄 Icon       │  (Blue rounded box)   │
│                    │   ClarityAP     │                       │
│                    └─────────────────┘                       │
│                                                               │
│                    Welcome Back                              │
│              Sign in to your account                         │
│                                                               │
│         ┌───────────────────────────────────────┐           │
│         │  White Card with Shadow               │           │
│         │                                        │           │
│         │  Email                                 │           │
│         │  [Input field...................]      │           │
│         │                                        │           │
│         │  Password                              │           │
│         │  [Input field...................]  👁  │           │
│         │                                        │           │
│         │  ☑ Remember me    Forgot password?    │           │
│         │                                        │           │
│         │  [     Sign In Button (Blue)     ]    │           │
│         │                                        │           │
│         │  Don't have an account? Sign up       │           │
│         └───────────────────────────────────────┘           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Design Details
- **Background:** Gradient from light blue to white to light gray
- **Logo:** Blue rounded square (16x16) with FileText icon in white
- **Card:** White, rounded-2xl, soft shadow, centered
- **Input Fields:**
  - Light gray border
  - Blue focus ring
  - Smooth transitions
- **Button:** Primary blue (#3b82f6), hover darker, white text
- **Typography:**
  - Heading: Bold, 24px, dark gray
  - Body: Regular, 14px, medium gray
- **Animations:** Fade-in on page load

---

## 2. Register Page (`/auth/register`)

### Visual Layout
```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│              [Gradient Background: Blue → White → Gray]      │
│                                                               │
│                    ┌─────────────────┐                       │
│                    │   📄 Icon       │  (Blue rounded box)   │
│                    │   ClarityAP     │                       │
│                    └─────────────────┘                       │
│                                                               │
│                  Create Your Account                         │
│              Get started with ClarityAP                      │
│                                                               │
│         ┌───────────────────────────────────────┐           │
│         │  White Card with Shadow               │           │
│         │                                        │           │
│         │  First Name        Last Name           │           │
│         │  [Input....]      [Input....]          │           │
│         │                                        │           │
│         │  Email                                 │           │
│         │  [Input field...................]      │           │
│         │                                        │           │
│         │  Company Name                          │           │
│         │  [Input field...................]      │           │
│         │                                        │           │
│         │  Password                              │           │
│         │  [Input field...................]  👁  │           │
│         │  ▓▓▓▓░░░░ Weak                        │           │
│         │                                        │           │
│         │  Confirm Password                      │           │
│         │  [Input field...................]  👁  │           │
│         │                                        │           │
│         │  ☑ I agree to Terms & Conditions      │           │
│         │                                        │           │
│         │  [    Create Account Button (Blue)]   │           │
│         │                                        │           │
│         │  Already have an account? Sign in     │           │
│         └───────────────────────────────────────┘           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Design Details
- **Layout:** Same gradient background as login
- **Multi-field Form:**
  - Two-column for First/Last name
  - Single column for email, company, passwords
- **Password Strength Indicator:**
  - Progress bar showing strength
  - Colors: Red (Weak) → Orange (Medium) → Green (Strong)
  - Real-time validation
- **Validation:** Error messages appear below fields in red
- **Animations:** Slide-in for form, fade-in for page

---

## 3. Dashboard Page (`/dashboard`)

### Visual Layout - Upload State
```
┌─────────────────────────────────────────────────────────────┐
│ Header (White, Shadow)                                      │
│  📄 ClarityAP Dashboard           [Upload New] [Export]    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Main Content (Gradient Background)                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📤 Upload Invoice                                     │   │
│  │                                                       │   │
│  │ ╔═══════════════════════════════════════════════╗   │   │
│  │ ║                                               ║   │   │
│  │ ║         📁 Drag & Drop Files Here            ║   │   │
│  │ ║              or click to browse              ║   │   │
│  │ ║                                               ║   │   │
│  │ ║  Supported: PDF, JPG, PNG (Max 10MB)        ║   │   │
│  │ ╚═══════════════════════════════════════════════╝   │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Visual Layout - Invoice Review State
```
┌─────────────────────────────────────────────────────────────┐
│ Main Content (Gradient Background)                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📋 Vendor Information                                │   │
│  │ ─────────────────────────────────────────────────────│   │
│  │                                                       │   │
│  │  Vendor Name                                         │   │
│  │  [ABC Electronics Pvt Ltd........................]   │   │
│  │                                                       │   │
│  │  Invoice Number         Invoice Date                 │   │
│  │  [INV-2024-001..]      [2024-01-15......]           │   │
│  │                                                       │   │
│  │  📍 Region-Specific Fields (Conditional)             │   │
│  │                                                       │   │
│  │  🇮🇳 For India (when GST selected):                  │   │
│  │  GSTIN Number          PAN Number                    │   │
│  │  [29AABCT1332L1Z5]    [AABCT1332L........]          │   │
│  │                                                       │   │
│  │  🇪🇺 For EU/UK (when VAT selected):                  │   │
│  │  VAT Number                                          │   │
│  │  [DE123456789................................]      │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 💰 Financial Details                                 │   │
│  │ ─────────────────────────────────────────────────────│   │
│  │                                                       │   │
│  │  Currency               Tax Type                     │   │
│  │  [INR - ₹  ▼]          [GST (India)  ▼]            │   │
│  │                                                       │   │
│  │  Tax Percentage (%)    Tax Amount                    │   │
│  │  [18.00...........]    [74,250.00........] (Auto)   │   │
│  │                                                       │   │
│  │  Subtotal              Total Amount                  │   │
│  │  [4,12,500.00.....]    [4,86,750.00.....] (Auto)   │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📦 Line Items                     [+ Add Item]       │   │
│  │ ─────────────────────────────────────────────────────│   │
│  │                                                       │   │
│  │  #1  Description          Qty    Rate      Amount    │   │
│  │      [Dell Laptop...]     [5]   [65000]  [325000]   │   │
│  │                                           (Auto) [×] │   │
│  │                                                       │   │
│  │  #2  Description          Qty    Rate      Amount    │   │
│  │      [Wireless Mouse...]  [10]  [4500]   [45000]    │   │
│  │                                           (Auto) [×] │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📝 Additional Notes                                  │   │
│  │ [Textarea for notes.............................    │   │
│  │  .................................................] │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
│  [💾 Save Changes]  [📥 Export to QuickBooks]  [🗑️ Delete] │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Design Details
- **Header:** White background, shadow, with ClarityAP logo and action buttons
- **Upload Zone:**
  - Dashed border (blue when dragging)
  - Large file icon
  - File type badges (PDF, JPG, PNG)
  - Hover effects
- **Invoice Form:**
  - Organized in collapsible sections with colored headers
  - Blue header: Vendor Information
  - Green header: Financial Details
  - Purple header: Line Items
- **Conditional Fields:**
  - GSTIN & PAN show when "GST (India)" selected
  - VAT Number shows when "VAT (EU/UK)" selected
  - Smooth animations when appearing
- **Currency Dropdown:**
  - Shows currency code and symbol (e.g., "INR - ₹")
  - 8 options: USD, EUR, GBP, INR, AUD, CAD, SGD, AED
- **Auto-calculations:**
  - Line item amount = qty × rate (grayed out, read-only)
  - Total = subtotal + tax (grayed out, read-only)
- **Line Items:**
  - Dynamic add/remove
  - Remove button (×) in red on hover
  - Grid layout for mobile responsiveness
- **Action Buttons:**
  - Save: Blue with disk icon
  - Export: Green with download icon
  - Delete: Red with trash icon
  - Disabled states with opacity

---

## 4. Export Page (`/export`)

### Visual Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Header (White, Shadow)                                      │
│  ← 📦 Export Invoices                        [Upload New]   │
│  Manage and export your invoices to QuickBooks              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Controls Bar (White Card)                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🔍 [Search by vendor, invoice #, currency............] │ │
│ │                                                         │ │
│ │ 🔧 [All Status ▼]  [Select All] [Clear]               │ │
│ │                                                         │ │
│ │ ───────────────────────────────────────────────────────│ │
│ │                                                         │ │
│ │ 5 invoices selected                                     │ │
│ │                                                         │ │
│ │         [📊 Export All CSV] [📥 Export Selected IIF(5)]│ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Invoice Table (White Card)                                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ☑│Vendor      │Invoice#│Date    │Amount  │Tax│Status │ │ │
│ │ ─┼────────────┼────────┼────────┼────────┼───┼───────┼─│ │
│ │ ☑│ABC Elec... │INV-001 │Jan 15  │₹486,750│GST│⏰Extr.│▶│ │
│ │  │🟠GSTIN 🟠PAN│        │        │INR     │   │       │ │ │
│ │ ─┼────────────┼────────┼────────┼────────┼───┼───────┼─│ │
│ │ ☑│TechSupply..│US-0045 │Jan 15  │$15,125 │ST │✅Revw│▶│ │
│ │  │            │        │        │USD     │   │       │ │ │
│ │ ─┼────────────┼────────┼────────┼────────┼───┼───────┼─│ │
│ │ ☑│EuroTech... │EU-0123 │Jan 15  │€22,729 │VAT│📤Exp.│▶│ │
│ │  │🔵VAT       │        │        │EUR     │   │       │ │ │
│ │ ─┼────────────┼────────┼────────┼────────┼───┼───────┼─│ │
│ │ ☑│British IT..│UK-0089 │Jan 15  │£18,124 │VAT│⏰Extr.│▶│ │
│ │  │🔵VAT       │        │        │GBP     │   │       │ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ Actions Column (▶):                                          │
│   👁️ View/Edit  |  📥 Export IIF  |  🗑️ Delete               │
└─────────────────────────────────────────────────────────────┘
```

### Design Details
- **Header:**
  - Back arrow to dashboard
  - Package icon with title
  - Upload New button (blue)
- **Search Bar:**
  - Full-width with search icon
  - Real-time filtering
  - Placeholder hints
- **Filter Controls:**
  - Status dropdown (All, Extracted, Reviewed, Exported)
  - Select All / Clear buttons
  - Selection counter
- **Batch Actions:**
  - Export All CSV (green button)
  - Export Selected IIF (blue button, shows count)
  - Disabled when nothing selected
- **Invoice Table:**
  - Checkboxes for selection
  - Row highlighting on hover (light blue)
  - Selected rows have blue background
  - **Status Badges:**
    - ⏰ Extracted (orange/yellow badge)
    - ✅ Reviewed (blue badge)
    - 📤 Exported (green badge)
  - **Region Badges:**
    - 🟠 Orange pills for GSTIN, PAN (India)
    - 🔵 Blue pills for VAT (EU/UK)
  - **Currency Display:**
    - Symbol + formatted amount (e.g., ₹4,86,750.00)
    - Currency code below
- **Action Icons (hover to reveal):**
  - Eye icon: View/edit (blue hover)
  - Download icon: Export single IIF (green hover)
  - Trash icon: Delete (red hover)
  - Loading spinner when action in progress
- **Empty State:**
  - Large file icon (grayed)
  - "No invoices yet" message
  - "Upload Invoice" button

---

## 🎨 Design System Summary

### Color Palette
```
Primary Blue:
  - 50:  #eff6ff (very light backgrounds)
  - 500: #3b82f6 (buttons, links)
  - 600: #2563eb (hover states)
  - 900: #1e3a8a (text)

Secondary Gray:
  - 50:  #f8fafc (backgrounds)
  - 300: #cbd5e1 (borders)
  - 600: #475569 (text)
  - 900: #0f172a (headings)

Success Green:
  - 50:  #f0fdf4 (backgrounds)
  - 600: #22c55e (buttons, success states)

Warning Orange:
  - 50:  #fff7ed (backgrounds)
  - 600: #f59e0b (warnings)

Danger Red:
  - 50:  #fef2f2 (backgrounds)
  - 600: #ef4444 (delete, errors)
```

### Typography
- **Font:** Inter (sans-serif)
- **Headings:**
  - H1: 24px, bold, secondary-900
  - H2: 20px, semibold, secondary-800
  - H3: 16px, medium, secondary-700
- **Body:** 14px, regular, secondary-600
- **Labels:** 14px, medium, secondary-700
- **Small:** 12px, regular, secondary-500

### Spacing
- Card padding: 24px (p-6)
- Section gaps: 24px (gap-6)
- Input padding: 10px 16px (px-4 py-2.5)
- Button padding: 8px 16px (px-4 py-2)

### Border Radius
- Cards: 16px (rounded-2xl)
- Buttons: 12px (rounded-xl)
- Inputs: 12px (rounded-xl)
- Badges: 8px (rounded-lg)

### Shadows
- Soft: 0 1px 2px rgba(0,0,0,0.05)
- Medium: 0 4px 6px rgba(0,0,0,0.07)
- Hard: 0 10px 15px rgba(0,0,0,0.1)

### Animations
- **fade-in:** 0.3s ease-in-out
  - Used for: Page loads, alerts
- **slide-in:** 0.3s ease-out
  - Used for: Dropdowns, modals
- **scale-in:** 0.2s ease-out
  - Used for: Cards, buttons
- **Transitions:** All interactive elements have 200ms transitions

### Icons
- Library: Lucide React
- Size: 20px (w-5 h-5) for general, 16px (w-4 h-4) for small
- Color: Inherits from parent or specific states

---

## 🌍 International Features

### Currency Support
```
Display Format:
  USD: $15,125.77
  EUR: €22,729.00
  GBP: £18,124.80
  INR: ₹4,86,750.00
  AUD: A$10,500.00
  CAD: C$12,000.00
  SGD: S$8,500.00
  AED: د.إ5,000.00
```

### Tax Types
```
┌────────────────────────────────────────┐
│ Tax Type Dropdown:                     │
├────────────────────────────────────────┤
│ 🇮🇳 GST (India)                         │
│ 🇪🇺 VAT (EU/UK)                         │
│ 🇺🇸 Sales Tax (US)                      │
│ 🌍 Service Tax                          │
│ ⚪ No Tax                               │
└────────────────────────────────────────┘

When GST selected:
  → Shows GSTIN field
  → Shows PAN field
  → Typical rate: 18% (9% CGST + 9% SGST)

When VAT selected:
  → Shows VAT Number field
  → Typical rates: 19% (EU), 20% (UK)

When Sales Tax selected:
  → No special fields
  → Typical rate: 8.25% (varies by state)
```

### Region-Specific Badges
```
India:     [GSTIN] [PAN]      (Orange pills)
EU/UK:     [VAT]              (Blue pill)
US:        No special badges
```

---

## 📱 Responsive Behavior

### Mobile (< 768px)
- Single column layout
- Stacked form fields
- Hamburger menu for navigation
- Touch-friendly buttons (larger)
- Table scrolls horizontally

### Tablet (768px - 1024px)
- Two-column forms where appropriate
- Compact table view
- Side navigation

### Desktop (> 1024px)
- Full multi-column layouts
- Expanded table with all columns
- Hover states active
- Maximum content width: 1280px (centered)

---

## ✨ Interactive Elements

### Buttons
```
Primary (Blue):
  Normal:  bg-primary-600 text-white
  Hover:   bg-primary-700 shadow-medium
  Disabled: opacity-50 cursor-not-allowed

Secondary (Gray outline):
  Normal:  border-secondary-300 text-secondary-700
  Hover:   bg-secondary-50

Danger (Red):
  Normal:  bg-danger-600 text-white
  Hover:   bg-danger-700

Success (Green):
  Normal:  bg-success-600 text-white
  Hover:   bg-success-700
```

### Input Fields
```
Normal:
  - Border: gray-300
  - Background: white
  - Text: gray-900

Focus:
  - Border: primary-500
  - Ring: 2px primary-500
  - Background: white

Error:
  - Border: danger-500
  - Ring: 2px danger-500
  - Help text: danger-600 below field

Disabled:
  - Background: gray-100
  - Text: gray-500
  - Cursor: not-allowed
```

### Hover Effects
- Cards: Slight lift (transform translateY(-2px))
- Buttons: Darker color + shadow
- Table rows: Light blue background
- Links: Underline appears
- Icons: Color change + scale(1.1)

---

## 🔄 Loading States

### Upload Progress
```
┌─────────────────────────────────────┐
│ Uploading invoice...                │
│ ████████████░░░░░░░░ 60%           │
│ ⏳ Processing...                    │
└─────────────────────────────────────┘
```

### AI Extraction
```
┌─────────────────────────────────────┐
│ ⚡ AI Extracting Data...            │
│                                     │
│     [Spinner Animation]             │
│                                     │
│ Please wait 3-5 seconds...          │
└─────────────────────────────────────┘
```

### Button Loading
```
[🔄 Saving...]        (Spinner + text)
[📥 Exporting...]     (Spinner + text)
```

### Table Loading
```
┌─────────────────────────────────────┐
│     [Spinner Animation]             │
│                                     │
│   Loading invoices...               │
└─────────────────────────────────────┘
```

---

## ⚠️ Error States

### Alert Messages
```
Success (Green):
┌─────────────────────────────────────┐
│ ✅ Invoice saved successfully!      │
└─────────────────────────────────────┘

Error (Red):
┌─────────────────────────────────────┐
│ ❌ Failed to upload invoice         │
│ Please check file format and retry  │
└─────────────────────────────────────┘

Warning (Orange):
┌─────────────────────────────────────┐
│ ⚠️  Invoice missing required fields │
│ Please complete all mandatory fields│
└─────────────────────────────────────┘

Info (Blue):
┌─────────────────────────────────────┐
│ ℹ️  Extraction complete - review data│
└─────────────────────────────────────┘
```

### Inline Validation
```
Email field with error:
┌─────────────────────────────────────┐
│ Email                               │
│ [invalid@@@email.com]  (Red border) │
│ ❌ Please enter a valid email       │
└─────────────────────────────────────┘
```

---

## 🎯 User Journey Flow

```
1. Login/Register
   ↓
2. Dashboard (Upload Zone)
   ↓
3. Upload Invoice (PDF/JPG/PNG)
   ↓
4. AI Extraction (3-5 seconds)
   ↓
5. Review & Edit Invoice Form
   ├→ Select Currency (8 options)
   ├→ Select Tax Type (GST/VAT/Sales Tax)
   ├→ Fill Region-Specific Fields
   ├→ Edit Line Items
   └→ Review Calculations
   ↓
6. Save Invoice
   ↓
7. Export Page
   ├→ View All Invoices
   ├→ Search & Filter
   ├→ Select Invoices
   └→ Export Options
       ├→ Single IIF
       ├→ Batch IIF
       └→ All CSV
   ↓
8. Download Files
```

---

**Last Updated:** December 25, 2025
**Status:** Complete UI Design
**Framework:** Next.js 14 + Tailwind CSS
**Icons:** Lucide React
