import { describe, expect, test } from 'bun:test'
import { loadCatalog } from './catalog'
import snapshot from '../data/catalog.json'

const spotifyOptions = {
  spotifyClientId: 'test-client',
  spotifyClientSecret: 'test-secret',
}

const response = (body: unknown) => new Response(JSON.stringify(body))

describe('loadCatalog', () => {
  test('uses snapshot releases when Spotify rejects', async () => {
    const catalog = await loadCatalog({
      ...spotifyOptions,
      fetch: async () => Promise.reject(new Error('Spotify unavailable')),
    })

    expect(catalog.releases).toHaveLength(snapshot.releases.length)
    expect(catalog.releases[0].cover).toBe(snapshot.releases[0].cover)
  })

  test('uses Spotify releases when YouTube rejects', async () => {
    let calls = 0
    const catalog = await loadCatalog({
      ...spotifyOptions,
      fetch: async () => {
        calls += 1
        if (calls === 1) return response({ access_token: 'token' })
        if (calls === 2) return response({ items: [album] })
        throw new Error('YouTube unavailable')
      },
    })

    expect(catalog.releases).toEqual([mappedAlbum])
    expect(catalog.videos).toEqual(snapshot.videos)
  })

  test('uses snapshot releases for malformed Spotify JSON', async () => {
    const catalog = await loadCatalog({
      ...spotifyOptions,
      fetch: async (url) =>
        String(url).includes('/api/token')
          ? response({ access_token: 'token' })
          : new Response('{', { headers: { 'content-type': 'application/json' } }),
    })

    expect(catalog.releases).toHaveLength(snapshot.releases.length)
  })

  test('maps a Spotify album to ShelfItem', async () => {
    let calls = 0
    const catalog = await loadCatalog({
      ...spotifyOptions,
      fetch: async () => {
        calls += 1
        if (calls === 1) return response({ access_token: 'token' })
        if (calls === 2) return response({ items: [album] })
        return response({})
      },
    })

    expect(catalog.releases).toEqual([mappedAlbum])
  })

  test('pairs each YouTube video ID with its title in actual RSS field order', async () => {
    const catalog = await loadCatalog({
      fetch: async () =>
        new Response(
          `<feed>
            <entry>
              <yt:videoId>abc123</yt:videoId>
              <title>Live Session</title>
            </entry>
            <entry>
              <yt:videoId>def456</yt:videoId>
              <title><![CDATA[Second Session]]></title>
            </entry>
          </feed>`,
        ),
    })

    expect(catalog.videos).toEqual([
      {
        title: 'Live Session',
        href: 'https://www.youtube.com/watch?v=abc123',
        thumbnail: 'https://i.ytimg.com/vi/abc123/hqdefault.jpg',
      },
      {
        title: 'Second Session',
        href: 'https://www.youtube.com/watch?v=def456',
        thumbnail: 'https://i.ytimg.com/vi/def456/hqdefault.jpg',
      },
    ])
    expect(catalog.releases).toHaveLength(snapshot.releases.length)
  })

  test('decodes XML entities in RSS titles without altering CDATA', async () => {
    const catalog = await loadCatalog({
      fetch: async () =>
        new Response(
          `<feed>
            <entry><title>Rock &amp; Roll &#39;Live&#39;</title><yt:videoId>encoded</yt:videoId></entry>
            <entry><title><![CDATA[Raw &amp; Title]]></title><yt:videoId>cdata</yt:videoId></entry>
          </feed>`,
        ),
    })

    expect(catalog.videos.map(({ title }) => title)).toEqual(["Rock & Roll 'Live'", 'Raw &amp; Title'])
  })
})

const album = {
  name: 'Nueva Vida',
  release_date: '2025-03-21',
  external_urls: { spotify: 'https://open.spotify.com/album/album-id' },
  images: [
    { url: 'https://images.example/medium.jpg', width: 300 },
    { url: 'https://images.example/large.jpg', width: 640 },
  ],
}

const mappedAlbum = {
  title: 'Nueva Vida',
  subtitle: '2025',
  href: 'https://open.spotify.com/album/album-id',
  label: 'Spotify',
  cover: 'https://images.example/large.jpg',
}
