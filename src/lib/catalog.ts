import type { ShelfItem } from '../components/ArtworkShelf.astro'
import snapshot from '../data/catalog.json'

export interface VideoItem {
  title: string
  href: string
  thumbnail: string
}

export interface Catalog {
  releases: ShelfItem[]
  videos: VideoItem[]
}

type LoadCatalogOptions = {
  fetch?: typeof fetch
  spotifyClientId?: string
  spotifyClientSecret?: string
}

const spotifyAlbumsUrl =
  'https://api.spotify.com/v1/artists/3pc90hxACiSUahZmmfYjcI/albums?include_groups=single,album&market=MX'
const youtubeChannelId = 'UCSZnXDUTBZvPYcU-AGZULYA'
// Two accepted forms of the same feed. The uploads-playlist form (UC -> UU) is
// the one that was here; the channel_id form is tried as a fallback because
// YouTube does not serve RSS for every auto-generated uploads playlist.
const youtubeFeedUrls = [
  `https://www.youtube.com/feeds/videos.xml?playlist_id=UU${youtubeChannelId.slice(2)}`,
  `https://www.youtube.com/feeds/videos.xml?channel_id=${youtubeChannelId}`,
]
const xmlEntities = { amp: '&', apos: "'", gt: '>', lt: '<', quot: '"' } as const

export async function loadCatalog(options: LoadCatalogOptions = {}): Promise<Catalog> {
  const fetcher = options.fetch ?? fetch
  // Falling back is correct -- a dead upstream must not break the build -- but it
  // has to say so. A silent catch here hid missing Spotify credentials for weeks:
  // the site kept building green off the snapshot with nobody the wiser.
  const releases = await loadSpotify(fetcher, options).catch((error) => {
    console.warn(`[catalog] Spotify fetch failed, using snapshot: ${error instanceof Error ? error.message : error}`)
    return snapshot.releases
  })
  const videos = await loadYouTube(fetcher).catch((error) => {
    console.warn(`[catalog] YouTube fetch failed, using snapshot: ${error instanceof Error ? error.message : error}`)
    return snapshot.videos
  })

  return { releases: releases.length ? releases : snapshot.releases, videos }
}

async function loadSpotify(fetcher: typeof fetch, options: LoadCatalogOptions): Promise<ShelfItem[]> {
  const clientId = options.spotifyClientId ?? import.meta.env.SPOTIFY_CLIENT_ID
  const clientSecret = options.spotifyClientSecret ?? import.meta.env.SPOTIFY_CLIENT_SECRET
  if (!clientId || !clientSecret) throw new Error('Spotify credentials missing')

  const tokenResponse = await fetcher('https://accounts.spotify.com/api/token', {
    method: 'POST',
    headers: {
      Authorization: `Basic ${btoa(`${clientId}:${clientSecret}`)}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'grant_type=client_credentials',
    signal: AbortSignal.timeout(10_000),
  })
  if (!tokenResponse.ok) throw new Error(`Spotify token failed: HTTP ${tokenResponse.status}`)
  const token = (await tokenResponse.json()).access_token
  if (typeof token !== 'string' || !token) throw new Error('Spotify token missing')

  const albumsResponse = await fetcher(spotifyAlbumsUrl, {
    headers: { Authorization: `Bearer ${token}` },
    signal: AbortSignal.timeout(10_000),
  })
  if (!albumsResponse.ok) {
    const detail = await albumsResponse.text().catch(() => '')
    throw new Error(`Spotify albums failed: HTTP ${albumsResponse.status} ${detail.slice(0, 200)}`)
  }
  const data = await albumsResponse.json()
  if (!Array.isArray(data?.items)) throw new Error('Spotify albums malformed')

  return data.items.map(mapAlbum).filter((item): item is ShelfItem => item !== null)
}

function mapAlbum(album: unknown): ShelfItem | null {
  if (!album || typeof album !== 'object') return null
  const value = album as Record<string, unknown>
  const images = Array.isArray(value.images) ? value.images : []
  const cover = images
    .filter((image): image is Record<string, unknown> => !!image && typeof image === 'object')
    .sort((a, b) => Number(b.width) - Number(a.width))
    .find((image) => typeof image.url === 'string')?.url
  const href = (value.external_urls as Record<string, unknown> | undefined)?.spotify
  const releaseDate = value.release_date
  if (typeof value.name !== 'string' || typeof href !== 'string' || typeof cover !== 'string') return null

  return { title: value.name, subtitle: typeof releaseDate === 'string' ? releaseDate.slice(0, 4) : '', href, label: 'Spotify', cover }
}

function decodeXmlTitle(title: string): string {
  const text = title.trim()
  if (text.startsWith('<![CDATA[') && text.endsWith(']]>')) return text.slice(9, -3).trim()

  return text.replace(/&(?:#(\d+)|#x([\da-f]+)|(amp|apos|gt|lt|quot));/gi, (entity, decimal, hexadecimal, named) => {
    if (named) return xmlEntities[named.toLowerCase() as keyof typeof xmlEntities]
    const codePoint = Number.parseInt(decimal ?? hexadecimal, decimal ? 10 : 16)
    return codePoint <= 0x10ffff ? String.fromCodePoint(codePoint) : entity
  })
}

async function loadYouTube(fetcher: typeof fetch): Promise<VideoItem[]> {
  let xml: string | null = null
  const failures: string[] = []
  for (const url of youtubeFeedUrls) {
    const response = await fetcher(url, { signal: AbortSignal.timeout(10_000) })
    if (response.ok) {
      xml = await response.text()
      break
    }
    failures.push(`HTTP ${response.status} on ${new URL(url).search}`)
  }
  if (xml === null) throw new Error(`YouTube feed failed: ${failures.join('; ')}`)
  const entries = xml.matchAll(/<entry(?:\s[^>]*)?>([\s\S]*?)<\/entry>/g)
  return [...entries].flatMap(([, entry]) => {
    const title = entry.match(/<title(?:\s[^>]*)?>([\s\S]*?)<\/title>/)?.[1]
    const id = entry.match(/<yt:videoId>([\w-]+)<\/yt:videoId>/)?.[1]
    return title && id
      ? [{
          title: decodeXmlTitle(title),
          href: `https://www.youtube.com/watch?v=${id}`,
          thumbnail: `https://i.ytimg.com/vi/${id}/hqdefault.jpg`,
        }]
      : []
  })
}
