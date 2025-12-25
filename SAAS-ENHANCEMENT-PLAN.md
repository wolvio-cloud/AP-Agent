# ClarityAP - SaaS Enhancement Plan

## 🎯 Objective
Transform ClarityAP from a single-user MVP into a full multi-tenant SaaS platform with subscription billing, team collaboration, and enterprise features.

---

## 📋 Phase 1: Multi-Tenancy Foundation

### 1.1 Organization/Tenant Model

**Database Changes:**
```sql
-- Create organizations table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    subdomain VARCHAR(100) UNIQUE,  -- For custom subdomains
    plan_type VARCHAR(50) DEFAULT 'free',  -- free, starter, professional, enterprise
    max_users INT DEFAULT 1,
    max_invoices_per_month INT DEFAULT 10,
    storage_limit_mb INT DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    trial_ends_at TIMESTAMP,
    subscription_id VARCHAR(255),  -- Stripe subscription ID
    billing_email VARCHAR(255),
    billing_address JSONB
);

-- Update users table
ALTER TABLE users ADD COLUMN organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE;
ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'member';  -- owner, admin, member, viewer
ALTER TABLE users ADD COLUMN invited_by UUID REFERENCES users(id);
ALTER TABLE users ADD COLUMN invitation_accepted_at TIMESTAMP;

-- Update invoices table
ALTER TABLE invoices ADD COLUMN organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- Create organization_invitations table
CREATE TABLE organization_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'member',
    invited_by UUID REFERENCES users(id),
    invitation_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    accepted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audit_logs table for compliance
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,  -- created, updated, deleted, exported, etc.
    resource_type VARCHAR(50) NOT NULL,  -- invoice, user, organization
    resource_id VARCHAR(255),
    changes JSONB,  -- What changed
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Backend Changes:**
- Add `OrganizationService` class
- Implement organization context middleware
- Add role-based permissions decorator
- Create invitation system
- Implement audit logging

**Files to Create/Modify:**
```
clarity-api/
├── app/
│   ├── models/
│   │   ├── organization.py (NEW)
│   │   └── audit_log.py (NEW)
│   ├── schemas/
│   │   ├── organization.py (NEW)
│   │   └── audit_log.py (NEW)
│   ├── services/
│   │   ├── organization.py (NEW)
│   │   └── audit.py (NEW)
│   ├── api/v1/
│   │   ├── organizations.py (NEW)
│   │   └── invitations.py (NEW)
│   └── middleware/
│       └── organization_context.py (NEW)
```

### 1.2 Role-Based Access Control (RBAC)

**Roles & Permissions:**
```python
ROLES = {
    'owner': {
        'invoices': ['create', 'read', 'update', 'delete', 'export'],
        'users': ['invite', 'remove', 'change_role'],
        'organization': ['update', 'delete', 'billing'],
        'settings': ['update'],
    },
    'admin': {
        'invoices': ['create', 'read', 'update', 'delete', 'export'],
        'users': ['invite', 'remove'],
        'organization': ['read'],
        'settings': ['read', 'update'],
    },
    'member': {
        'invoices': ['create', 'read', 'update', 'export'],
        'users': ['read'],
        'organization': ['read'],
        'settings': ['read'],
    },
    'viewer': {
        'invoices': ['read', 'export'],
        'users': ['read'],
        'organization': ['read'],
        'settings': ['read'],
    }
}
```

**Implementation:**
```python
# app/utils/permissions.py
def require_permission(resource: str, action: str):
    """Decorator to check user permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user and organization
            user = kwargs.get('current_user')
            if not has_permission(user.role, resource, action):
                raise HTTPException(403, "Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@router.delete("/invoices/{invoice_id}")
@require_permission("invoices", "delete")
async def delete_invoice(invoice_id: str, current_user: User = Depends(get_current_user)):
    pass
```

---

## 📋 Phase 2: Subscription & Billing

### 2.1 Pricing Plans

```python
PRICING_PLANS = {
    'free': {
        'name': 'Free',
        'price_monthly': 0,
        'price_yearly': 0,
        'max_users': 1,
        'max_invoices_per_month': 10,
        'storage_mb': 100,
        'features': [
            'Upload & extract invoices',
            'QuickBooks IIF export',
            'Basic support',
        ],
        'limits': {
            'batch_export': False,
            'api_access': False,
            'custom_branding': False,
        }
    },
    'starter': {
        'name': 'Starter',
        'price_monthly': 29,
        'price_yearly': 290,  # 2 months free
        'max_users': 3,
        'max_invoices_per_month': 100,
        'storage_mb': 1000,
        'features': [
            'Everything in Free',
            'Up to 3 team members',
            'Batch export',
            'Email support',
            '100 invoices/month',
        ],
        'limits': {
            'batch_export': True,
            'api_access': False,
            'custom_branding': False,
        }
    },
    'professional': {
        'name': 'Professional',
        'price_monthly': 99,
        'price_yearly': 990,
        'max_users': 10,
        'max_invoices_per_month': 500,
        'storage_mb': 5000,
        'features': [
            'Everything in Starter',
            'Up to 10 team members',
            'API access',
            'Priority support',
            '500 invoices/month',
            'Advanced search & filters',
        ],
        'limits': {
            'batch_export': True,
            'api_access': True,
            'custom_branding': False,
        }
    },
    'enterprise': {
        'name': 'Enterprise',
        'price_monthly': 299,
        'price_yearly': 2990,
        'max_users': -1,  # Unlimited
        'max_invoices_per_month': -1,  # Unlimited
        'storage_mb': -1,  # Unlimited
        'features': [
            'Everything in Professional',
            'Unlimited users',
            'Unlimited invoices',
            'Custom branding',
            'Dedicated support',
            'SLA guarantee',
            'Custom integrations',
            'SSO / SAML',
        ],
        'limits': {
            'batch_export': True,
            'api_access': True,
            'custom_branding': True,
        }
    }
}
```

### 2.2 Stripe Integration

**Install Stripe:**
```bash
pip install stripe
```

**Database Tables:**
```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE NOT NULL,
    stripe_customer_id VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50) NOT NULL,
    billing_interval VARCHAR(20) NOT NULL,  -- monthly, yearly
    status VARCHAR(50) NOT NULL,  -- active, canceled, past_due, trialing
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    stripe_payment_method_id VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- card, bank_account
    is_default BOOLEAN DEFAULT false,
    card_brand VARCHAR(50),
    card_last4 VARCHAR(4),
    expiry_month INT,
    expiry_year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoices_billing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    stripe_invoice_id VARCHAR(255) UNIQUE NOT NULL,
    amount_due INT NOT NULL,  -- in cents
    amount_paid INT NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL,  -- draft, open, paid, void, uncollectible
    invoice_pdf VARCHAR(500),  -- Stripe invoice PDF URL
    due_date TIMESTAMP,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    invoices_processed INT DEFAULT 0,
    storage_used_mb INT DEFAULT 0,
    api_calls INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Backend Implementation:**
```python
# app/services/stripe_service.py
import stripe
from app.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    @staticmethod
    async def create_customer(organization: Organization, billing_email: str):
        """Create a Stripe customer"""
        customer = stripe.Customer.create(
            email=billing_email,
            metadata={
                'organization_id': str(organization.id),
                'organization_name': organization.name
            }
        )
        return customer

    @staticmethod
    async def create_subscription(customer_id: str, price_id: str):
        """Create a subscription"""
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{'price': price_id}],
            trial_period_days=14,  # 14-day free trial
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent']
        )
        return subscription

    @staticmethod
    async def cancel_subscription(subscription_id: str):
        """Cancel a subscription"""
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        return subscription

    @staticmethod
    async def handle_webhook(payload: bytes, signature: str):
        """Handle Stripe webhooks"""
        event = stripe.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )

        if event['type'] == 'invoice.payment_succeeded':
            # Handle successful payment
            pass
        elif event['type'] == 'invoice.payment_failed':
            # Handle failed payment
            pass
        elif event['type'] == 'customer.subscription.deleted':
            # Handle subscription cancellation
            pass

        return event
```

**API Endpoints:**
```python
# app/api/v1/billing.py
@router.post("/billing/subscribe")
async def subscribe(
    plan: str,
    interval: str,
    current_user: User = Depends(get_current_user)
):
    """Subscribe to a plan"""
    # Create customer if not exists
    # Create subscription
    # Update organization
    pass

@router.post("/billing/cancel")
async def cancel_subscription(current_user: User = Depends(get_current_user)):
    """Cancel subscription"""
    pass

@router.get("/billing/invoices")
async def get_billing_invoices(current_user: User = Depends(get_current_user)):
    """Get billing invoices"""
    pass

@router.post("/billing/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    pass
```

### 2.3 Usage Tracking & Limits

```python
# app/middleware/usage_limiter.py
class UsageLimiter:
    @staticmethod
    async def check_invoice_limit(organization: Organization):
        """Check if organization can process more invoices this month"""
        current_usage = await get_monthly_usage(organization.id)
        plan_limit = PRICING_PLANS[organization.plan_type]['max_invoices_per_month']

        if plan_limit == -1:  # Unlimited
            return True

        if current_usage.invoices_processed >= plan_limit:
            raise HTTPException(
                429,
                f"Monthly invoice limit reached ({plan_limit}). Please upgrade your plan."
            )
        return True

    @staticmethod
    async def track_invoice_processing(organization_id: UUID):
        """Increment invoice processing counter"""
        # Update usage_tracking table
        pass
```

---

## 📋 Phase 3: Frontend SaaS Features

### 3.1 Organization Management UI

**New Pages to Create:**
```
clarity-web/app/
├── settings/
│   ├── organization/page.tsx    # Organization settings
│   ├── billing/page.tsx          # Billing & subscription
│   ├── team/page.tsx             # Team management
│   └── api-keys/page.tsx         # API keys (for Professional+)
├── pricing/page.tsx              # Public pricing page
└── upgrade/page.tsx              # Upgrade/downgrade page
```

**Organization Settings Page:**
```typescript
// clarity-web/app/settings/organization/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'

export default function OrganizationSettings() {
  const [organization, setOrganization] = useState(null)

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Organization Settings</h1>

      {/* Organization Name */}
      <section className="bg-white rounded-2xl shadow-soft p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Organization Details</h2>
        <div className="space-y-4">
          <div>
            <label>Organization Name</label>
            <input type="text" className="w-full" />
          </div>
          <div>
            <label>Subdomain</label>
            <input type="text" className="w-full" />
            <p className="text-sm text-secondary-500 mt-1">
              Access your account at: yourorg.clarityap.com
            </p>
          </div>
        </div>
      </section>

      {/* Danger Zone */}
      <section className="bg-white rounded-2xl shadow-soft border-2 border-danger-200 p-6">
        <h2 className="text-xl font-semibold text-danger-600 mb-4">Danger Zone</h2>
        <button className="btn-danger">Delete Organization</button>
      </section>
    </div>
  )
}
```

**Team Management Page:**
```typescript
// clarity-web/app/settings/team/page.tsx
'use client'

export default function TeamManagement() {
  return (
    <div className="max-w-6xl mx-auto p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Team Members</h1>
        <button className="btn-primary">Invite Member</button>
      </div>

      {/* Team Members Table */}
      <div className="bg-white rounded-2xl shadow-soft overflow-hidden">
        <table className="w-full">
          <thead className="bg-secondary-50">
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {/* Team member rows */}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

**Billing Page:**
```typescript
// clarity-web/app/settings/billing/page.tsx
'use client'

import { loadStripe } from '@stripe/stripe-js'
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js'

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)

export default function Billing() {
  return (
    <div className="max-w-6xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Billing & Subscription</h1>

      {/* Current Plan */}
      <section className="bg-white rounded-2xl shadow-soft p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold">Current Plan: Professional</h2>
            <p className="text-secondary-600">$99/month • Renews on Jan 15, 2025</p>
          </div>
          <button className="btn-secondary">Change Plan</button>
        </div>

        {/* Usage Stats */}
        <div className="mt-6 grid grid-cols-3 gap-4">
          <div className="bg-primary-50 rounded-xl p-4">
            <p className="text-sm text-secondary-600">Invoices This Month</p>
            <p className="text-2xl font-bold text-primary-600">247 / 500</p>
          </div>
          <div className="bg-success-50 rounded-xl p-4">
            <p className="text-sm text-secondary-600">Team Members</p>
            <p className="text-2xl font-bold text-success-600">6 / 10</p>
          </div>
          <div className="bg-warning-50 rounded-xl p-4">
            <p className="text-sm text-secondary-600">Storage Used</p>
            <p className="text-2xl font-bold text-warning-600">2.1 / 5 GB</p>
          </div>
        </div>
      </section>

      {/* Payment Method */}
      <section className="bg-white rounded-2xl shadow-soft p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Payment Method</h2>
        <Elements stripe={stripePromise}>
          <PaymentMethodForm />
        </Elements>
      </section>

      {/* Billing History */}
      <section className="bg-white rounded-2xl shadow-soft p-6">
        <h2 className="text-xl font-semibold mb-4">Billing History</h2>
        <table className="w-full">
          <thead>
            <tr>
              <th>Date</th>
              <th>Description</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Invoice</th>
            </tr>
          </thead>
          <tbody>
            {/* Billing history rows */}
          </tbody>
        </table>
      </section>
    </div>
  )
}
```

**Pricing Page (Public):**
```typescript
// clarity-web/app/pricing/page.tsx
'use client'

export default function Pricing() {
  const plans = [
    {
      name: 'Free',
      price: 0,
      features: ['10 invoices/month', '1 user', 'Basic support'],
      cta: 'Get Started'
    },
    {
      name: 'Starter',
      price: 29,
      features: ['100 invoices/month', '3 users', 'Email support'],
      cta: 'Start Free Trial',
      popular: true
    },
    {
      name: 'Professional',
      price: 99,
      features: ['500 invoices/month', '10 users', 'Priority support', 'API access'],
      cta: 'Start Free Trial'
    },
    {
      name: 'Enterprise',
      price: 299,
      features: ['Unlimited invoices', 'Unlimited users', 'Dedicated support', 'SSO'],
      cta: 'Contact Sales'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white py-20">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-secondary-900 mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-secondary-600">
            Choose the plan that's right for your business
          </p>
        </div>

        <div className="grid md:grid-cols-4 gap-8">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`bg-white rounded-2xl shadow-soft p-8 ${
                plan.popular ? 'ring-2 ring-primary-500' : ''
              }`}
            >
              {plan.popular && (
                <span className="bg-primary-600 text-white px-3 py-1 rounded-full text-sm">
                  Most Popular
                </span>
              )}
              <h3 className="text-2xl font-bold mt-4">{plan.name}</h3>
              <div className="mt-4 mb-6">
                <span className="text-4xl font-bold">${plan.price}</span>
                <span className="text-secondary-600">/month</span>
              </div>
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center">
                    <svg className="w-5 h-5 text-success-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
              <button className={plan.popular ? 'btn-primary w-full' : 'btn-secondary w-full'}>
                {plan.cta}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
```

---

## 📋 Phase 4: Advanced Features

### 4.1 API Keys & Webhooks

**Database:**
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,  -- First few chars for display
    key_hash VARCHAR(255) NOT NULL,   -- Hashed API key
    scopes JSONB NOT NULL,            -- ['invoices:read', 'invoices:write']
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP
);

CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    events JSONB NOT NULL,            -- ['invoice.created', 'invoice.updated']
    secret VARCHAR(255) NOT NULL,     -- For signature verification
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES webhooks(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    response_code INT,
    response_body TEXT,
    delivered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Advanced Search & Filtering

**Elasticsearch Integration:**
```bash
pip install elasticsearch
```

**Implementation:**
```python
# app/services/search_service.py
from elasticsearch import Elasticsearch

class SearchService:
    def __init__(self):
        self.es = Elasticsearch([settings.ELASTICSEARCH_URL])

    async def index_invoice(self, invoice: Invoice):
        """Index an invoice for search"""
        doc = {
            'vendor_name': invoice.vendor_name,
            'invoice_number': invoice.invoice_number,
            'total_amount': invoice.total_amount,
            'currency': invoice.currency,
            'invoice_date': invoice.invoice_date,
            'organization_id': str(invoice.organization_id)
        }
        self.es.index(index='invoices', id=str(invoice.id), document=doc)

    async def search_invoices(self, query: str, organization_id: str, filters: dict):
        """Search invoices with filters"""
        body = {
            'query': {
                'bool': {
                    'must': [
                        {'match': {'organization_id': organization_id}},
                        {'multi_match': {
                            'query': query,
                            'fields': ['vendor_name', 'invoice_number']
                        }}
                    ],
                    'filter': []
                }
            }
        }

        if filters.get('date_from'):
            body['query']['bool']['filter'].append({
                'range': {'invoice_date': {'gte': filters['date_from']}}
            })

        return self.es.search(index='invoices', body=body)
```

### 4.3 SSO / SAML (Enterprise)

```bash
pip install python-saml
```

```python
# app/services/sso_service.py
from onelogin.saml2.auth import OneLogin_Saml2_Auth

class SSOService:
    @staticmethod
    async def initiate_sso_login(organization: Organization):
        """Initiate SSO login"""
        # Configure SAML settings
        # Redirect to IdP
        pass

    @staticmethod
    async def process_sso_response(saml_response: str):
        """Process SAML response from IdP"""
        # Validate SAML response
        # Create or update user
        # Create session
        pass
```

---

## 📋 Phase 5: Deployment & Infrastructure

### 5.1 Production Deployment

**Recommended Stack:**
- **Frontend:** Vercel
- **Backend:** Railway / Render / DigitalOcean App Platform
- **Database:** Supabase / Railway PostgreSQL / AWS RDS
- **File Storage:** AWS S3 / Cloudflare R2
- **Search:** Elasticsearch Cloud / Algolia
- **Cache:** Redis Cloud / Upstash
- **Monitoring:** Sentry + Datadog / New Relic
- **Email:** SendGrid / Postmark
- **Payments:** Stripe

**Docker Configuration:**
```dockerfile
# Dockerfile (Backend)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Dockerfile (Frontend)
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

CMD ["npm", "start"]
```

**docker-compose.yml (Production):**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: clarityap
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  backend:
    build: ./clarity-api
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/clarityap
      REDIS_URL: redis://redis:6379/0
    ports:
      - "8000:8000"

  frontend:
    build: ./clarity-web
    depends_on:
      - backend
    environment:
      NEXT_PUBLIC_API_URL: https://api.clarityap.com
    ports:
      - "3000:3000"

volumes:
  postgres_data:
  redis_data:
```

### 5.2 CI/CD Pipeline

**GitHub Actions:**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd clarity-api
          pip install -r requirements.txt
          pytest

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          railway up

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: |
          vercel --prod
```

### 5.3 Monitoring & Alerts

**Sentry Setup:**
```python
# app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,
    environment=settings.ENVIRONMENT
)
```

**Health Check Endpoint:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_database(),
        "redis": await check_redis(),
        "storage": await check_storage()
    }
```

---

## 📊 Implementation Timeline

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| **Phase 1: Multi-Tenancy** | Database schema, Organization model, RBAC | 1-2 weeks |
| **Phase 2: Billing** | Stripe integration, Plans, Usage tracking | 1-2 weeks |
| **Phase 3: Frontend** | Settings pages, Team management, Billing UI | 1-2 weeks |
| **Phase 4: Advanced** | API keys, Webhooks, Search, SSO | 2-3 weeks |
| **Phase 5: Deployment** | Infrastructure, CI/CD, Monitoring | 1 week |

**Total Estimated Time:** 6-10 weeks for complete SaaS transformation

---

## 💰 Pricing Strategy Recommendations

### Market Positioning
- **Free Plan:** Lead generation, solo users
- **Starter Plan ($29/month):** Small businesses (3-10 employees)
- **Professional Plan ($99/month):** Growing businesses (10-50 employees)
- **Enterprise Plan ($299/month):** Large organizations (50+ employees)

### Revenue Projections (Year 1)
- 1,000 Free users → 0 revenue
- 200 Starter users × $29 = $5,800/month
- 50 Professional users × $99 = $4,950/month
- 10 Enterprise users × $299 = $2,990/month

**Total MRR:** $13,740/month
**Total ARR:** ~$165,000/year

---

## ✅ Next Steps

1. **Run integration tests** to verify current MVP
2. **Implement Phase 1** (Multi-tenancy) - Most critical
3. **Implement Phase 2** (Billing) - Revenue generation
4. **Build Phase 3** (Frontend) - User experience
5. **Add Phase 4** (Advanced features) - Competitive advantage
6. **Deploy Phase 5** (Infrastructure) - Go to market

**Ready to start! Let's begin with integration testing first, then proceed with multi-tenancy implementation.**
