import { expect, test } from '@playwright/test'

test.describe('public booking flow', () => {
  test('POST /api/booking success redirects to gracias with sent copy (API mocked)', async ({ page }) => {
    await page.route('**/api/booking', async (route) => {
      if (route.request().method() !== 'POST') {
        await route.continue()
        return
      }
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          data: { ok: true, bookingId: 1, confirmation: 'sent' },
        }),
      })
    })

    await page.goto('/contratacion')
    await page.getByLabel(/Nombre/i).fill('Playwright smoke')
    await page.getByLabel(/^Email/i).fill('pw-smoke@example.com')
    await page.getByLabel(/Ciudad \/ Estado/i).fill('Xalapa, Veracruz')
    await page.locator('#eventType').selectOption('boda')
    await page.getByRole('button', { name: /Enviar solicitud/i }).click()

    await page.waitForURL(/\/booking\/gracias/, { timeout: 15_000 })
    await expect(page).toHaveURL(/\/booking\/gracias/)

    await expect(page.locator('#thanks-message')).toContainText('Mensaje enviado. Te contactaremos pronto.')
    await expect(page.locator('.thanks-youtube-frame')).toHaveAttribute(
      'src',
      /youtube\.com\/embed\/HTA31yUX41A/,
    )
  })

  test('POST success with confirmation pending lands on gracias with pending copy (API mocked)', async ({
    page,
  }) => {
    await page.route('**/api/booking', async (route) => {
      if (route.request().method() !== 'POST') {
        await route.continue()
        return
      }
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          data: { ok: true, bookingId: 2, confirmation: 'pending' },
        }),
      })
    })

    await page.goto('/contratacion')
    await page.getByLabel(/Nombre/i).fill('Playwright pending')
    await page.getByLabel(/^Email/i).fill('pw-pending@example.com')
    await page.getByLabel(/Ciudad \/ Estado/i).fill('Xalapa, Veracruz')
    await page.locator('#eventType').selectOption('boda')
    await page.getByRole('button', { name: /Enviar solicitud/i }).click()

    await page.waitForURL(/\/booking\/gracias/, { timeout: 15_000 })
    await expect(page.locator('#thanks-message')).toContainText(
      'la confirmación por correo no pudo enviarse',
    )
  })

  test('thank-you page without sessionStorage redirects to /contratacion', async ({ page }) => {
    await page.goto('/booking/gracias')
    await page.waitForURL((url) => url.pathname === '/contratacion', { timeout: 15_000 })
  })

  test('POST /api/booking 400 shows error status (API mocked)', async ({ page }) => {
    await page.route('**/api/booking', async (route) => {
      if (route.request().method() !== 'POST') {
        await route.continue()
        return
      }
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Correo no válido',
            status: 400,
          },
        }),
      })
    })

    await page.goto('/contratacion')
    await page.getByLabel(/Nombre/i).fill('Playwright smoke')
    await page.getByLabel(/^Email/i).fill('pw-smoke@example.com')
    await page.getByLabel(/Ciudad \/ Estado/i).fill('Xalapa, Veracruz')
    await page.locator('#eventType').selectOption('boda')
    await page.getByRole('button', { name: /Enviar solicitud/i }).click()

    const status = page.locator('#form-status')
    await expect(status).toHaveAttribute('data-state', 'error', { timeout: 15_000 })
    await expect(status).toContainText('Correo no válido')
  })
})
