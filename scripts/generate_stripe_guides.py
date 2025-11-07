#!/usr/bin/env python3
"""
Generate organized Stripe guides from the complete documentation.
Consolidates related docs into topic-focused guides for easy LLM access.
"""

import os
from pathlib import Path
from collections import defaultdict

# Base paths
DOCS_DIR = Path("/Users/zach/Documents/cc-skills/docs/stripe")
GUIDES_DIR = Path("/Users/zach/Documents/cc-skills/.claude/skills/stripe/stripe-expert/guides")

# Topic mappings: which source directories map to which guide topics
TOPIC_MAPPINGS = {
    'payments': {
        'dirs': ['payments', 'checkout', 'payment-links', 'payment-authentication', 'elements'],
        'keywords': ['payment_intent', 'checkout', 'payment_method', 'card', 'wallet'],
    },
    'billing': {
        'dirs': ['billing', 'invoicing', 'customer-management', 'products-prices'],
        'keywords': ['subscription', 'invoice', 'billing', 'price', 'product', 'customer'],
    },
    'connect': {
        'dirs': ['connect'],
        'keywords': ['connect', 'account', 'transfer', 'platform', 'marketplace'],
    },
    'webhooks': {
        'dirs': ['webhooks', 'event-destinations'],
        'keywords': ['webhook', 'event', 'signature'],
    },
    'api': {
        'dirs': ['api', 'apis', 'api-v2-overview'],
        'keywords': ['api', 'authentication', 'error', 'pagination', 'rate'],
    },
    'security': {
        'dirs': ['radar', 'disputes'],
        'keywords': ['security', 'fraud', 'dispute', 'radar', 'verification'],
    },
    'testing': {
        'dirs': ['testing', 'cli', 'development'],
        'keywords': ['test', 'cli', 'sandbox', 'development'],
    },
}

def create_guide_structure():
    """Create the guide directory structure."""
    for topic in TOPIC_MAPPINGS.keys():
        (GUIDES_DIR / topic).mkdir(parents=True, exist_ok=True)
    
    # Additional directories
    for dir_name in ['troubleshooting', 'patterns', 'quick-reference']:
        (GUIDES_DIR / dir_name).mkdir(parents=True, exist_ok=True)
    
    print(f"✓ Created guide structure in {GUIDES_DIR}")

def generate_quick_reference():
    """Generate quick reference cheat sheets."""
    
    # Error codes quick reference
    error_codes_content = """# Stripe Error Codes - Quick Reference

## Card Errors

| Code | Description | Solution |
|------|-------------|----------|
| `card_declined` | Card declined by issuer | Ask for different payment method |
| `insufficient_funds` | Not enough funds | Request different payment method |
| `lost_card` | Card reported lost | Contact customer |
| `stolen_card` | Card reported stolen | Contact customer |
| `expired_card` | Card has expired | Request updated card |
| `incorrect_cvc` | CVC check failed | Re-enter CVC |
| `processing_error` | Processing error occurred | Retry |
| `incorrect_number` | Card number invalid | Re-enter card number |

## Authentication Errors

| Code | Description | Solution |
|------|-------------|----------|
| `authentication_required` | 3D Secure needed | Use confirmCardPayment() |
| `approve_with_id` | Payment needs approval | Contact card issuer |

## API Errors

| Code | Description | Solution |
|------|-------------|----------|
| `rate_limit_error` | Too many requests | Implement exponential backoff |
| `invalid_request_error` | Invalid parameters | Check request parameters |
| `api_error` | Stripe API error | Retry with backoff |
| `idempotency_error` | Duplicate with different params | Use consistent idempotency keys |

## Common HTTP Status Codes

- **200** - OK
- **400** - Bad Request (invalid parameters)
- **401** - Unauthorized (invalid API key)
- **402** - Request Failed
- **403** - Forbidden
- **404** - Not Found
- **429** - Too Many Requests (rate limit)
- **500/502/503/504** - Server Errors (retry)

## References

Source: `/docs/stripe/error-codes/` and `/docs/stripe/error-handling/`
"""
    
    (GUIDES_DIR / 'quick-reference' / 'error-codes.md').write_text(error_codes_content)
    
    # Test cards quick reference
    test_cards_content = """# Stripe Test Cards - Quick Reference

## Success

| Card Number | Description |
|-------------|-------------|
| `4242 4242 4242 4242` | Visa - Succeeds |
| `5555 5555 5555 4444` | Mastercard - Succeeds |
| `3782 822463 10005` | American Express - Succeeds |
| `6011 1111 1111 1117` | Discover - Succeeds |

## 3D Secure / Authentication

| Card Number | Description |
|-------------|-------------|
| `4000 0027 6000 3184` | Visa - Requires 3D Secure |
| `4000 0025 0000 3155` | Visa - Requires authentication |
| `4000 0082 6000 0000` | Visa - 3DS required on setup |

## Declines

| Card Number | Description |
|-------------|-------------|
| `4000 0000 0000 0002` | Generic decline |
| `4000 0000 0000 9995` | Insufficient funds |
| `4000 0000 0000 9987` | Lost card |
| `4000 0000 0000 9979` | Stolen card |
| `4000 0000 0000 0069` | Expired card |
| `4000 0000 0000 0127` | Incorrect CVC |
| `4000 0000 0000 0119` | Processing error |
| `4242 4242 4242 4241` | Incorrect number |

## Disputes

| Card Number | Description |
|-------------|-------------|
| `4000 0000 0000 0259` | Charge disputed as fraudulent |
| `4000 0000 0000 2685` | Charge disputed (not fraudulent) |
| `4000 0000 0000 8235` | Early fraud warning |

## Other Test Scenarios

| Card Number | Description |
|-------------|-------------|
| `4000 0000 0000 3220` | 3D Secure 2 required |
| `4000 0000 0000 3063` | Always fails risk evaluation |
| `4000 0000 0000 0341` | Charge succeeds, dispute lost |

## Usage

```typescript
// All test cards
- Use any future expiration date (e.g., 12/34)
- Use any 3-digit CVC (4 digits for Amex)
- Use any billing ZIP code
```

## Testing in Different Regions

- **India**: `4000 0035 6000 0008` (India Visa)
- **Mexico**: `4000 0048 4000 0008` (Mexico Visa)  
- **Brazil**: `4000 0007 6000 0002` (Brazil Visa)

## References

Source: `/docs/stripe/testing/`
"""
    
    (GUIDES_DIR / 'quick-reference' / 'test-data.md').write_text(test_cards_content)
    
    # Webhook events quick reference
    webhook_events_content = """# Stripe Webhook Events - Quick Reference

## Payment Events

```typescript
// Payment successful
'payment_intent.succeeded'

// Payment failed
'payment_intent.payment_failed'

// Payment requires action (3D Secure)
'payment_intent.requires_action'

// Charge succeeded (legacy)
'charge.succeeded'

// Charge refunded
'charge.refunded'

// Charge disputed
'charge.dispute.created'
```

## Subscription Events

```typescript
// Subscription created
'customer.subscription.created'

// Subscription updated
'customer.subscription.updated'

// Subscription deleted
'customer.subscription.deleted'

// Trial ending soon (3 days before)
'customer.subscription.trial_will_end'

// Subscription paused
'customer.subscription.paused'

// Subscription resumed
'customer.subscription.resumed'
```

## Invoice Events

```typescript
// Invoice created
'invoice.created'

// Invoice finalized
'invoice.finalized'

// Invoice paid
'invoice.paid'

// Invoice payment failed
'invoice.payment_failed'

// Invoice voided
'invoice.voided'

// Payment requires action
'invoice.payment_action_required'

// Upcoming invoice
'invoice.upcoming'
```

## Customer Events

```typescript
// Customer created
'customer.created'

// Customer updated
'customer.updated'

// Customer deleted
'customer.deleted'

// Payment method attached
'payment_method.attached'

// Payment method detached
'payment_method.detached'
```

## Payout Events

```typescript
// Payout created
'payout.created'

// Payout paid
'payout.paid'

// Payout failed
'payout.failed'

// Payout canceled
'payout.canceled'
```

## Connect Events

```typescript
// Account created
'account.updated'

// Account deactivated
'account.external_account.created'

// Transfer created
'transfer.created'

// Application fee created
'application_fee.created'
```

## Setup Intent Events

```typescript
// Setup successful
'setup_intent.succeeded'

// Setup canceled
'setup_intent.canceled'

// Setup requires action
'setup_intent.requires_action'
```

## Product Events

```typescript
// Product created
'product.created'

// Product updated
'product.updated'

// Price created
'price.created'

// Price updated
'price.updated'
```

## Webhook Handler Template

```typescript
const handler = async (req, res) => {
  const event = req.body

  switch (event.type) {
    case 'payment_intent.succeeded':
      // Handle successful payment
      break
    case 'invoice.paid':
      // Handle paid invoice
      break
    case 'customer.subscription.updated':
      // Handle subscription change
      break
    default:
      console.log(`Unhandled event: ${event.type}`)
  }

  res.json({ received: true })
}
```

## References

Source: `/docs/stripe/webhooks/` and `/docs/stripe/api/events/`
Complete list: 350+ event types available
"""
    
    (GUIDES_DIR / 'quick-reference' / 'webhook-events.md').write_text(webhook_events_content)
    
    print("✓ Generated quick reference guides")

def generate_pattern_guides():
    """Generate code pattern guides."""
    
    # TypeScript setup
    typescript_content = """# TypeScript Setup for Stripe

## Installation

```bash
npm install stripe @stripe/stripe-js
npm install -D @types/stripe @types/node
```

## Server-Side Setup

```typescript
// lib/stripe.ts
import Stripe from 'stripe'

if (!process.env.STRIPE_SECRET_KEY) {
  throw new Error('Missing STRIPE_SECRET_KEY')
}

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2023-10-16',
  typescript: true,
})

// Type-safe helper
export type StripeCustomer = Stripe.Customer
export type StripeSubscription = Stripe.Subscription
export type StripeInvoice = Stripe.Invoice
```

## Client-Side Setup

```typescript
// lib/stripe-client.ts
import { loadStripe, Stripe } from '@stripe/stripe-js'

let stripePromise: Promise<Stripe | null>

export const getStripe = () => {
  if (!stripePromise) {
    stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)
  }
  return stripePromise
}
```

## Type-Safe API Route

```typescript
// pages/api/create-payment-intent.ts
import type { NextApiRequest, NextApiResponse } from 'next'
import { stripe } from '@/lib/stripe'
import Stripe from 'stripe'

type Data = {
  clientSecret?: string
  error?: string
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<Data>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { amount } = req.body

    const paymentIntent: Stripe.PaymentIntent = await stripe.paymentIntents.create({
      amount,
      currency: 'usd',
      automatic_payment_methods: {
        enabled: true,
      },
    })

    res.status(200).json({ clientSecret: paymentIntent.client_secret! })
  } catch (err) {
    const error = err as Stripe.errors.StripeError
    res.status(500).json({ error: error.message })
  }
}
```

## Environment Variables

```env
# .env.local
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Type Guards

```typescript
// lib/stripe-helpers.ts
import Stripe from 'stripe'

export function isStripeCustomer(
  obj: unknown
): obj is Stripe.Customer {
  return typeof obj === 'object' && obj !== null && 'object' in obj && obj.object === 'customer'
}

export function isStripeError(
  err: unknown
): err is Stripe.errors.StripeError {
  return err instanceof Error && 'type' in err && 'code' in err
}
```

## References

- TypeScript docs: https://github.com/stripe/stripe-node#typescript-support
- API types: https://stripe.com/docs/api
"""
    
    (GUIDES_DIR / 'patterns' / 'typescript-setup.md').write_text(typescript_content)
    
    # Next.js integration
    nextjs_content = """# Next.js Integration Patterns

## App Router (Next.js 13+)

### Server Component Payment Intent

```typescript
// app/checkout/page.tsx
import { stripe } from '@/lib/stripe'
import CheckoutForm from './CheckoutForm'

export default async function CheckoutPage() {
  const paymentIntent = await stripe.paymentIntents.create({
    amount: 2000,
    currency: 'usd',
    automatic_payment_methods: { enabled: true },
  })

  return <CheckoutForm clientSecret={paymentIntent.client_secret!} />
}
```

### Client Component

```typescript
// app/checkout/CheckoutForm.tsx
'use client'

import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { loadStripe } from '@stripe/stripe-js'

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)

export default function CheckoutForm({ clientSecret }: { clientSecret: string }) {
  return (
    <Elements stripe={stripePromise} options={{ clientSecret }}>
      <CheckoutFormInner />
    </Elements>
  )
}

function CheckoutFormInner() {
  const stripe = useStripe()
  const elements = useElements()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!stripe || !elements) return

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/success`,
      },
    })

    if (error) {
      console.error(error.message)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      <button type="submit" disabled={!stripe}>
        Pay
      </button>
    </form>
  )
}
```

### API Route Webhook Handler

```typescript
// app/api/webhooks/stripe/route.ts
import { headers } from 'next/headers'
import { stripe } from '@/lib/stripe'
import Stripe from 'stripe'

export async function POST(req: Request) {
  const body = await req.text()
  const signature = headers().get('stripe-signature')!

  let event: Stripe.Event

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    )
  } catch (err) {
    return new Response(`Webhook Error: ${err.message}`, { status: 400 })
  }

  // Handle event
  switch (event.type) {
    case 'payment_intent.succeeded':
      const paymentIntent = event.data.object as Stripe.PaymentIntent
      // Handle successful payment
      break
    default:
      console.log(`Unhandled event: ${event.type}`)
  }

  return new Response(JSON.stringify({ received: true }), { status: 200 })
}
```

## Pages Router (Next.js 12)

### API Route

```typescript
// pages/api/create-checkout-session.ts
import { NextApiRequest, NextApiResponse } from 'next'
import { stripe } from '@/lib/stripe'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    try {
      const session = await stripe.checkout.sessions.create({
        mode: 'payment',
        line_items: [{
          price: 'price_xxx',
          quantity: 1,
        }],
        success_url: `${req.headers.origin}/success`,
        cancel_url: `${req.headers.origin}/cancel`,
      })

      res.redirect(303, session.url!)
    } catch (err) {
      res.status(500).json({ error: err.message })
    }
  } else {
    res.setHeader('Allow', 'POST')
    res.status(405).end('Method Not Allowed')
  }
}
```

## Server Actions (Experimental)

```typescript
// app/actions/stripe.ts
'use server'

import { stripe } from '@/lib/stripe'
import { redirect } from 'next/navigation'

export async function createCheckoutSession(formData: FormData) {
  const priceId = formData.get('priceId') as string

  const session = await stripe.checkout.sessions.create({
    mode: 'payment',
    line_items: [{
      price: priceId,
      quantity: 1,
    }],
    success_url: `${process.env.NEXT_PUBLIC_URL}/success`,
    cancel_url: `${process.env.NEXT_PUBLIC_URL}/cancel`,
  })

  redirect(session.url!)
}
```

## Environment Configuration

```typescript
// next.config.js
module.exports = {
  env: {
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY,
  },
}
```

## References

- Next.js docs: https://nextjs.org/docs
- Stripe Next.js example: https://github.com/stripe-samples/nextjs-typescript-react-stripe-js
"""
    
    (GUIDES_DIR / 'patterns' / 'nextjs-integration.md').write_text(nextjs_content)
    
    print("✓ Generated pattern guides")

def main():
    print("Generating Stripe Guide Structure...")
    print("=" * 60)
    
    create_guide_structure()
    generate_quick_reference()
    generate_pattern_guides()
    
    print("\n" + "=" * 60)
    print("✓ Guide generation complete!")
    print(f"\nGuides location: {GUIDES_DIR}")
    print("\nNext steps:")
    print("1. Review INDEX.md for guide structure")
    print("2. Check quick-reference/ for cheat sheets")
    print("3. Review patterns/ for code examples")

if __name__ == '__main__':
    main()
