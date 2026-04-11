import { describe, expect, test } from 'bun:test'
import {
  BOOKING_THANKS_YOUTUBE_VIDEO_ID,
  bookingThanksYoutubeEmbedUrl,
  bookingThanksYoutubeIframeTitle,
  bookingThanksYoutubeWatchUrl,
} from './bookingThanksPresentation'

describe('bookingThanksPresentation', () => {
  test('embed and watch URLs include stable video id', () => {
    expect(bookingThanksYoutubeEmbedUrl).toContain(BOOKING_THANKS_YOUTUBE_VIDEO_ID)
    expect(bookingThanksYoutubeEmbedUrl).toMatch(/^https:\/\/www\.youtube\.com\/embed\//)
    expect(bookingThanksYoutubeWatchUrl).toContain(BOOKING_THANKS_YOUTUBE_VIDEO_ID)
    expect(bookingThanksYoutubeWatchUrl).toMatch(/^https:\/\/www\.youtube\.com\/watch\?v=/)
  })

  test('iframe title non-empty for accessibility', () => {
    expect(bookingThanksYoutubeIframeTitle.length).toBeGreaterThan(10)
  })
})
