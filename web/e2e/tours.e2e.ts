import { expect, test } from '@playwright/test'

test.describe('homepage tour dates', () => {
  test('#fechas tour table visible', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('#fechas .tour-table')).toBeVisible()
    await expect(page.locator('#fechas .tour-table tbody tr').first()).toBeVisible()
  })

  test('hydration: empty API shows empty-state copy', async ({ page }) => {
    await page.route('**/api/tours/upcoming', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ data: [] as unknown[] }),
      })
    })
    await page.goto('/')
    await expect(page.locator('#fechas .tour-table__empty td')).toContainText(
      'No hay fechas anunciadas por ahora.',
      { timeout: 15_000 },
    )
  })

  test('hydration: sold-out row shows SOLD OUT tag', async ({ page }) => {
    await page.route('**/api/tours/upcoming', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: [
            {
              date: '2030-06-15',
              city: 'Xalapa',
              venue: 'Foro PW',
              soldOut: true,
              cta: { label: 'Boletos', href: 'https://example.com/t' },
            },
          ],
        }),
      })
    })
    await page.goto('/')
    await expect(page.locator('#fechas .tour-tag-soldout')).toHaveText('SOLD OUT', { timeout: 15_000 })
  })

  test('hydration: API row replaces tbody (unique venue)', async ({ page }) => {
    await page.route('**/api/tours/upcoming', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: [
            {
              date: '2031-03-01',
              city: 'Veracruz',
              venue: 'PW Hydration Venue',
              cta: { label: 'Boletos', href: 'https://example.com/x' },
            },
          ],
        }),
      })
    })
    await page.goto('/')
    await expect(page.locator('#fechas .tour-table tbody')).toContainText('PW Hydration Venue', {
      timeout: 15_000,
    })
    await expect(page.locator('#fechas .tour-table__empty')).toHaveCount(0)
  })
})
