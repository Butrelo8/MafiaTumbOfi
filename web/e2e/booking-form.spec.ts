import { test, expect } from '@playwright/test'

test('empty submit fires no network request', async ({ page }) => {
  const requests: string[] = []
  page.on('request', (req) => {
    if (req.url().includes('/api/booking')) requests.push(req.url())
  })

  await page.goto('/contratacion')
  await page.click('button[type="submit"]')
  await page.waitForTimeout(500)

  expect(requests).toHaveLength(0)
})

test('empty submit shows name error immediately', async ({ page }) => {
  await page.goto('/contratacion')
  await page.click('button[type="submit"]')
  await expect(page.locator('#error-name')).toBeVisible()
  await expect(page.locator('#error-name')).toContainText('obligatorio')
})

test('invalid email shows email error immediately', async ({ page }) => {
  await page.goto('/contratacion')
  await page.fill('#name', 'Juan')
  await page.fill('#email', 'notanemail')
  await page.click('button[type="submit"]')
  await expect(page.locator('#error-email')).toBeVisible()
  await expect(page.locator('#error-email')).toContainText('válido')
})
