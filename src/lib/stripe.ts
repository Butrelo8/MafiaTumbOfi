import Stripe from 'stripe'

/** Lazy-init so app can start without STRIPE_SECRET_KEY when Stripe is deferred. */
let _stripe: Stripe | null = null

export function getStripe(): Stripe {
  if (!_stripe) {
    if (!process.env.STRIPE_SECRET_KEY) {
      throw new Error('STRIPE_SECRET_KEY is required when using Stripe')
    }
    _stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
      apiVersion: '2024-12-18.acacia',
    })
  }
  return _stripe
}

/**
 * Verify Stripe webhook signature.
 * Always call this before processing any webhook event.
 */
export const verifyWebhookSignature = (
  payload: string,
  signature: string,
): Stripe.Event => {
  if (!process.env.STRIPE_WEBHOOK_SECRET) {
    throw new Error('STRIPE_WEBHOOK_SECRET is required')
  }

  return getStripe().webhooks.constructEvent(
    payload,
    signature,
    process.env.STRIPE_WEBHOOK_SECRET,
  )
}
