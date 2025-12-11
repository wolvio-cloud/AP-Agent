# Phase 4 UI Visual Mockups

Detailed visual representations of all UI components and pages.

---

## 1. Invoice Detail Page (High Confidence)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  ← Back   │  invoice_2024_001.pdf - Invoice Details                             │
│                                                                                   │
│  [📄 Download]  [⚡ Process with AI]                                             │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│  Status & Confidence                                                              │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│  Status                Processing Tier                          Overall           │
│  ┌────────────────┐   ┌──────────────────────────┐          Confidence          │
│  │ ✓ Extracted    │   │ ● Tier 1: Gemini Flash  │                               │
│  └────────────────┘   └──────────────────────────┘             ┌───────┐         │
│   (Green badge)         (Blue badge with dot)                  │   96  │         │
│                                                                 │   %   │         │
│                                                                 └───────┘         │
│                                                          (Large green ring)       │
│                                                          Overall Confidence       │
└──────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┬────────────────────────────────────────────────────┐
│  LEFT COLUMN                │  RIGHT COLUMN                                      │
│  (40% width)                │  (60% width)                                       │
├─────────────────────────────┼────────────────────────────────────────────────────┤
│                             │                                                    │
│  ┌───────────────────────┐ │  ┌──────────────────────────────────────────────┐ │
│  │  📄 Document Preview  │ │  │  🏢 Vendor Information                       │ │
│  ├───────────────────────┤ │  ├──────────────────────────────────────────────┤ │
│  │                       │ │  │                                              │ │
│  │     ╔═══════════╗     │ │  │  Vendor Name              97% confident      │ │
│  │     ║           ║     │ │  │  Acme Construction Supplies                  │ │
│  │     ║    PDF    ║     │ │  │                                              │ │
│  │     ║  PREVIEW  ║     │ │  │  Address                  95% confident      │ │
│  │     ║           ║     │ │  │  123 Builder St, Mumbai, MH 400001           │ │
│  │     ╚═══════════╝     │ │  │                                              │ │
│  │                       │ │  │  Tax ID / GSTIN           98% confident      │ │
│  │  invoice_2024_001.pdf │ │  │  29ABCDE1234F1Z5                             │ │
│  │                       │ │  │                                              │ │
│  │  Click download to    │ │  └──────────────────────────────────────────────┘ │
│  │  view full document   │ │                                                    │
│  │                       │ │  ┌──────────────────────────────────────────────┐ │
│  │  [📥 Open Document]   │ │  │  # Invoice Details                           │ │
│  │                       │ │  ├──────────────────────────────────────────────┤ │
│  └───────────────────────┘ │  │                                              │ │
│                             │  │  Invoice Number    Currency                  │ │
│  ┌───────────────────────┐ │  │  INV-5678  96%     INR                       │ │
│  │  🕐 Processing History│ │  │                                              │ │
│  ├───────────────────────┤ │  │  Invoice Date      Due Date                  │ │
│  │                       │ │  │  Jan 10, 2024 95%  Feb 09, 2024 93%          │ │
│  │  ● Tier 1 - 96%      │ │  │                                              │ │
│  │    (1250ms)           │ │  │  Payment Terms                               │ │
│  │    ├─ Jan 15, 10:35  │ │  │  Net 30                                      │ │
│  │                       │ │  │                                              │ │
│  │  Green dot            │ │  └──────────────────────────────────────────────┘ │
│  │  Success!             │ │                                                    │
│  │                       │ │  ┌──────────────────────────────────────────────┐ │
│  └───────────────────────┘ │  │  💰 Financial Summary                        │ │
│                             │  ├──────────────────────────────────────────────┤ │
│                             │  │                                              │ │
│                             │  │  Subtotal            ₹125,000.00    (95%)    │ │
│                             │  │  ──────────────────────────────────────────  │ │
│                             │  │  Tax (18%)           ₹22,500.00     (96%)    │ │
│                             │  │  ──────────────────────────────────────────  │ │
│                             │  │  Total               ₹147,500.00    (98%)    │ │
│                             │  │                      ═══════════             │ │
│                             │  │                      (Bold, large)           │ │
│                             │  │                                              │ │
│                             │  └──────────────────────────────────────────────┘ │
│                             │                                                    │
│                             │  ┌──────────────────────────────────────────────┐ │
│                             │  │  Line Items                      92% confident│ │
│                             │  ├──────────────────────────────────────────────┤ │
│                             │  │ Description       Qty  Unit Price   Amount   │ │
│                             │  │ ───────────────────────────────────────────  │ │
│                             │  │ Item 1 - Materials 50  ₹2,500.00   ₹125,000 │ │
│                             │  │                                              │ │
│                             │  └──────────────────────────────────────────────┘ │
│                             │                                                    │
└─────────────────────────────┴────────────────────────────────────────────────────┘
```

---

## 2. Invoice Detail Page (Low Confidence - Needs Review)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  ← Back   │  blurry_invoice.jpg - Invoice Details                               │
│                                                                                   │
│  [📄 Download]                                                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│  Status & Confidence                                                              │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│  Status                Processing Tier               ⚠️ Requires Review          │
│  ┌────────────────┐   ┌──────────────────────────┐                              │
│  │ ⚠ Needs Review │   │ ● Tier 4: Human Review  │     Overall                   │
│  └────────────────┘   └──────────────────────────┘     Confidence               │
│   (Yellow badge)        (Orange badge)                   ┌───────┐              │
│                                                           │   78  │              │
│  ┌────────────────────────────────────────────────┐      │   %   │              │
│  │ ⚠️ Action required: This invoice has very low │      └───────┘              │
│  │    confidence and needs immediate review.      │ (Large red ring)            │
│  │    Priority: HIGH                              │                              │
│  └────────────────────────────────────────────────┘                              │
│   (Yellow warning banner)                                                         │
└──────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┬────────────────────────────────────────────────────┐
│  LEFT COLUMN                │  RIGHT COLUMN                                      │
├─────────────────────────────┼────────────────────────────────────────────────────┤
│                             │                                                    │
│  ┌───────────────────────┐ │  ┌──────────────────────────────────────────────┐ │
│  │  📄 Document Preview  │ │  │  🏢 Vendor Information                       │ │
│  ├───────────────────────┤ │  ├──────────────────────────────────────────────┤ │
│  │                       │ │  │                                              │ │
│  │     ╔═══════════╗     │ │  │  Vendor Name              72% confident      │ │
│  │     ║  Blurry   ║     │ │  │  Unknown Vendor              (Red text)      │ │
│  │     ║   Image   ║     │ │  │                                              │ │
│  │     ║    Low    ║     │ │  │  Address                  65% confident      │ │
│  │     ║  Quality  ║     │ │  │  Partially extracted         (Red text)      │ │
│  │     ╚═══════════╝     │ │  │                                              │ │
│  │                       │ │  │  Tax ID / GSTIN           58% confident      │ │
│  │  blurry_invoice.jpg   │ │  │  —                           (Red text)      │ │
│  │                       │ │  │                                              │ │
│  │  [📥 Open Document]   │ │  └──────────────────────────────────────────────┘ │
│  │                       │ │                                                    │
│  └───────────────────────┘ │  ┌──────────────────────────────────────────────┐ │
│                             │  │  # Invoice Details                           │ │
│  ┌───────────────────────┐ │  ├──────────────────────────────────────────────┤ │
│  │  🕐 Processing History│ │  │                                              │ │
│  ├───────────────────────┤ │  │  Invoice Number    Currency                  │ │
│  │                       │ │  │  —  68%            INR                       │ │
│  │  ● Tier 1 - 76%      │ │  │  (Red text)                                  │ │
│  │    (1250ms)           │ │  │                                              │ │
│  │    ├─ Jan 15, 10:35  │ │  │  Invoice Date      Due Date                  │ │
│  │    Red dot            │ │  │  Jan 10, 2024 70%  —  62%                    │ │
│  │                       │ │  │  (Red text)        (Red text)                │ │
│  │  ● Tier 2 - 79%      │ │  │                                              │ │
│  │    (2500ms)           │ │  └──────────────────────────────────────────────┘ │
│  │    ├─ Jan 15, 10:36  │ │                                                    │
│  │    Red dot            │ │  ┌──────────────────────────────────────────────┐ │
│  │                       │ │  │  💰 Financial Summary                        │ │
│  │  ● Tier 3 - 78%      │ │  ├──────────────────────────────────────────────┤ │
│  │    (3200ms)           │ │  │                                              │ │
│  │    ├─ Jan 15, 10:36  │ │  │  Subtotal            ₹50,000.00     (65%)    │ │
│  │    Red dot            │ │  │  ──────────────────────────────────────────  │ │
│  │                       │ │  │  Tax (18%)           —               (58%)    │ │
│  │  All tiers tried!     │ │  │  ──────────────────────────────────────────  │ │
│  │  Needs human review   │ │  │  Total               ₹59,000.00     (68%)    │ │
│  │                       │ │  │                      ═══════════             │ │
│  └───────────────────────┘ │  │                      (Red color)             │ │
│                             │  │                                              │ │
│                             │  └──────────────────────────────────────────────┘ │
│                             │                                                    │
└─────────────────────────────┴────────────────────────────────────────────────────┘

🔴 Red confidence rings = Low confidence, needs review
🟡 Yellow rings = Medium confidence (85-94%)
🟢 Green rings = High confidence (≥95%)
```

---

## 3. Review Queue Page

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  ← Back   │  ⚠️ Review Queue                                                    │
│                                                                                   │
│  Invoices requiring human review due to low confidence scores                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│  STATISTICS CARDS                                                                 │
├───────────────┬───────────────┬───────────────┬─────────────────────────────────┤
│               │               │               │                                 │
│  Total Reviews│ High Priority │ Med. Priority │ Low Priority                    │
│  ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐                    │
│  │    8     │ │ │    3     │ │ │    3     │ │ │    2     │                    │
│  │          │ │ │  🔴      │ │ │  🟡      │ │ │  🔵      │                    │
│  └──────────┘ │ └──────────┘ │ └──────────┘ │ └──────────┘                    │
│   Gray card   │  Red card    │ Yellow card  │  Blue card                      │
│               │               │               │                                 │
└───────────────┴───────────────┴───────────────┴─────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│  🔍 Filters                                                                       │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│  [ All (8) ]  [ High (3) ]  [ Medium (3) ]  [ Low (2) ]                          │
│    Active      Inactive      Inactive        Inactive                            │
│   (Blue bg)   (Gray bg)     (Gray bg)       (Gray bg)                            │
│                                                                                    │
└──────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│  INVOICE CARD #1 (High Priority)                                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│  📄  blurry_invoice_001.jpg                                    ┌───────┐      >   │
│                                                                │   72  │          │
│      [ ⚠ Needs Review ] [ ● Tier 4 ] [ 🔴 High Priority ]   │   %   │          │
│                                                                └───────┘          │
│      Vendor             Invoice #        Amount               (Red ring)         │
│      Unknown Vendor     —                ₹59,000.00                              │
│                                                                                    │
│      Extracted: 2h ago                                                            │
│                                                                                    │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │ ⚠️ Action required: This invoice has very low confidence and needs        │  │
│  │    immediate review.                                                       │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
│   (Red warning banner)                                                            │
│                                                                                    │
└──────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│  INVOICE CARD #2 (High Priority)                                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│  📄  damaged_scan.pdf                                          ┌───────┐      >   │
│                                                                │   68  │          │
│      [ ⚠ Needs Review ] [ ● Tier 4 ] [ 🔴 High Priority ]   │   %   │          │
│                                                                └───────┘          │
│      Vendor                Invoice #       Amount              (Red ring)         │
│      Partially extracted   INV-123 70%     ₹85,000.00                            │
│                                                                                    │
│      Extracted: 4h ago                                                            │
│                                                                                    │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │ ⚠️ Action required: This invoice has very low confidence and needs        │  │
│  │    immediate review.                                                       │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                    │
└──────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│  INVOICE CARD #3 (Medium Priority)                                                │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│  📄  old_receipt.jpg                                           ┌───────┐      >   │
│                                                                │   75  │          │
│      [ ⚠ Needs Review ] [ ● Tier 3 ] [ 🟡 Medium Priority ] │   %   │          │
│                                                                └───────┘          │
│      Vendor                Invoice #       Amount              (Yellow ring)      │
│      ABC Corp              INV-456 82%     ₹120,000.00                           │
│                                                                                    │
│      Extracted: 1d ago                                                            │
│                                                                                    │
│  (No warning banner for medium priority)                                          │
│                                                                                    │
└──────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│  INVOICE CARD #4 (Low Priority)                                                   │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│  📄  invoice_foreign.pdf                                       ┌───────┐      >   │
│                                                                │   82  │          │
│      [ ⚠ Needs Review ] [ ● Tier 3 ] [ 🔵 Low Priority ]    │   %   │          │
│                                                                └───────┘          │
│      Vendor                Invoice #       Amount              (Yellow ring)      │
│      Global Tech           INV-789 88%     ₹95,000.00                            │
│                                                                                    │
│      Extracted: 2d ago                                                            │
│                                                                                    │
└──────────────────────────────────────────────────────────────────────────────────┘

(Cards are clickable → Navigate to invoice detail page)
```

---

## 4. Invoice List Page (Updated)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Invoices                                                 [⬆️ Upload Invoice]    │
│  Manage and track your uploaded invoices                                         │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│  🔍 Search & Filters                                                              │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│  [🔍 Search by filename, vendor, or invoice number...]     [🔽 All Status]       │
│                                                                                    │
└──────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│  INVOICES TABLE                                                                   │
├──────────┬───────────┬──────────┬─────────┬───────────┬──────────┬──────────────┤
│ Filename │ Vendor    │ Invoice# │ Amount  │ Status    │ Conf.    │ Uploaded     │
├──────────┼───────────┼──────────┼─────────┼───────────┼──────────┼──────────────┤
│          │           │          │         │           │          │              │
│ 📄 inv_  │ Acme      │ INV-5678 │ ₹147,5K │ ✓ Extract │ 96%🟢   │ Jan 15       │
│ 2024.pdf │ Construct │          │         │ (Green)   │          │              │
│          │           │          │         │           │          │              │
│ 📄 blur  │ Unknown   │ —        │ ₹59,0K  │ ⚠ Review  │ 72%🔴   │ Jan 15       │
│ ry.jpg   │ Vendor    │          │         │ (Yellow)  │          │              │
│          │           │          │         │           │          │              │
│ 📄 rec   │ ABC Corp  │ INV-456  │ ₹120,0K │ ⚠ Review  │ 75%🟡   │ Jan 14       │
│ eipt.jpg │           │          │         │ (Yellow)  │          │              │
│          │           │          │         │           │          │              │
│ 📄 old_  │ Global    │ INV-789  │ ₹95,0K  │ ⚠ Review  │ 82%🟡   │ Jan 13       │
│ inv.pdf  │ Tech      │          │         │ (Yellow)  │          │              │
│          │           │          │         │           │          │              │
│ 📄 new_  │ Premier   │ INV-111  │ ₹210,0K │ ⏳ Upload │ —        │ Jan 15       │
│ file.pdf │ —         │ —        │ —       │ (Gray)    │          │              │
│          │           │          │         │           │          │              │
└──────────┴───────────┴──────────┴─────────┴───────────┴──────────┴──────────────┘

Showing 5 invoices

(Click any row → Navigate to invoice detail page)
```

---

## 5. Component Examples

### ConfidenceRing Component

```
Size: sm (40px)           Size: md (64px)           Size: lg (100px)

   ┌─────┐                   ┌─────────┐               ┌───────────┐
   │ 96% │                   │         │               │           │
   └─────┘                   │   96%   │               │           │
   Green                     │         │               │    96%    │
                             └─────────┘               │           │
                             Green ring                │           │
                                                       └───────────┘
                                                       Green ring
                                                       Overall Confidence


   ┌─────┐                   ┌─────────┐               ┌───────────┐
   │ 88% │                   │         │               │           │
   └─────┘                   │   88%   │               │           │
   Yellow                    │         │               │    88%    │
                             └─────────┘               │           │
                             Yellow ring               │           │
                                                       └───────────┘
                                                       Yellow ring


   ┌─────┐                   ┌─────────┐               ┌───────────┐
   │ 72% │                   │         │               │           │
   └─────┘                   │   72%   │               │           │
   Red                       │         │               │    72%    │
                             └─────────┘               │           │
                             Red ring                  │           │
                                                       └───────────┘
                                                       Red ring
```

### StatusBadge Component

```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ ⏳ Uploaded    │  │ ⏳ Processing  │  │ ✓ Extracted    │  │ ⚠ Needs Review │
└────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘
  Gray              Blue                Green               Yellow

┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ ✓ Approved     │  │ ✗ Rejected     │  │ ✗ Error        │
└────────────────┘  └────────────────┘  └────────────────┘
  Green              Red                 Red
```

### ProcessingTierBadge Component

```
┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
│ ● Tier 1: Gemini Flash  │  │ ● Tier 2: Preprocessed   │  │ ● Tier 3: GPT-4V        │
└──────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘
  Blue dot                      Purple dot                    Indigo dot

┌──────────────────────────┐  ┌──────────────────────────┐
│ ● Tier 4: Human Review  │  │ ● Completed              │
└──────────────────────────┘  └──────────────────────────┘
  Orange dot                    Green dot
```

---

## 6. Mobile View (Invoice Detail)

```
┌─────────────────────────┐
│ ← Invoice Detail        │
├─────────────────────────┤
│                         │
│ invoice_2024_001.pdf    │
│                         │
│ [📄 Download]          │
│ [⚡ Process with AI]   │
│                         │
├─────────────────────────┤
│ Status: ✓ Extracted     │
│ Tier: Gemini Flash      │
│                         │
│       ┌───────┐         │
│       │  96%  │         │
│       └───────┘         │
│    Overall Confidence   │
│      (Green ring)       │
│                         │
├─────────────────────────┤
│ 📄 Document            │
│ ┌───────────────────┐  │
│ │                   │  │
│ │   PDF Preview     │  │
│ │                   │  │
│ └───────────────────┘  │
│                         │
├─────────────────────────┤
│ 🏢 Vendor Info         │
│                         │
│ Vendor Name      97%    │
│ Acme Construction       │
│                         │
│ Address          95%    │
│ 123 Builder St          │
│                         │
│ GSTIN            98%    │
│ 29ABCDE1234F1Z5         │
│                         │
├─────────────────────────┤
│ # Invoice Details       │
│                         │
│ Invoice#         96%    │
│ INV-5678                │
│                         │
│ Date             95%    │
│ Jan 10, 2024            │
│                         │
│ Due Date         93%    │
│ Feb 09, 2024            │
│                         │
├─────────────────────────┤
│ 💰 Financial Summary   │
│                         │
│ Subtotal    ₹125,000    │
│ Tax (18%)   ₹22,500     │
│ ─────────────────────   │
│ Total       ₹147,500    │
│             ═══════     │
│                         │
└─────────────────────────┘

(Stack vertically on mobile)
```

---

## 7. Color System Visual Guide

### Confidence Color Coding

```
🟢 GREEN (≥95%)
   ━━━━━━━━━━━━━━━
   High Confidence
   Auto-approved
   #22c55e

🟡 YELLOW (85-94%)
   ━━━━━━━━━━━━━━━
   Medium Confidence
   Extracted but flag
   #eab308

🔴 RED (<85%)
   ━━━━━━━━━━━━━━━
   Low Confidence
   Needs review
   #ef4444
```

### Status Colors

```
⚫ GRAY
   Uploaded, neutral
   #6b7280

🔵 BLUE
   Processing
   #3b82f6

🟢 GREEN
   Success, approved
   #22c55e

🟡 YELLOW
   Needs attention
   #eab308

🔴 RED
   Error, rejected
   #ef4444

🟠 ORANGE
   Human review
   #f97316
```

---

## 8. Typography & Spacing

```
Headings:
┌─────────────────────────┐
│ Vendor Information      │  ← 18px, bold (600), gray-900
└─────────────────────────┘

Labels:
Vendor Name               ← 14px, medium (500), gray-700

Values:
Acme Construction         ← 16px, regular (400), gray-900

Confidence:
97% confident             ← 12px, medium (500), green/yellow/red

Amounts:
₹147,500.00               ← 24px, bold (700), blue-600
```

### Spacing (8px grid)

```
Card padding:     24px (3 units)
Section spacing:  24px (3 units)
Field spacing:    16px (2 units)
Label spacing:    4px  (0.5 units)
```

---

## 9. Interactive States

### Button States

```
Normal:
┌────────────────────┐
│ ⚡ Process with AI │  Blue (#3b82f6), hover: darker
└────────────────────┘

Hover:
┌────────────────────┐
│ ⚡ Process with AI │  Darker blue (#2563eb)
└────────────────────┘

Loading:
┌────────────────────┐
│ ⏳ Processing...   │  Opacity 50%, spinner animation
└────────────────────┘

Disabled:
┌────────────────────┐
│ ⚡ Process with AI │  Gray, opacity 50%, cursor not-allowed
└────────────────────┘
```

### Card Hover State

```
Normal:
┌──────────────────────────────────────┐
│ Invoice Card                         │  Border: gray-200
└──────────────────────────────────────┘

Hover:
┌══════════════════════════════════════┐
│ Invoice Card                         │  Border: blue-300, shadow-md
└══════════════════════════════════════┘
```

---

## Summary

All UI components follow these principles:

✅ **Clean & Modern**: Plenty of whitespace, clear hierarchy
✅ **Color-Coded**: Instant visual feedback via colors
✅ **Responsive**: Works on desktop, tablet, and mobile
✅ **Accessible**: Proper contrast, keyboard navigation
✅ **Consistent**: Same patterns throughout
✅ **Professional**: Enterprise-grade design

The UI is built with:
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Next.js 14** for routing
- **TypeScript** for type safety

**To see the actual UI:**
1. Start backend: `cd clarity-api && python -m uvicorn app.main:app --reload`
2. Start frontend: `cd clarity-web && npm run dev`
3. Open: http://localhost:3000
