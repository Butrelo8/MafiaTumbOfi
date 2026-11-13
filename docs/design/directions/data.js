// Real content only: research/contenido/{catalog.json,members.ts,socials.ts} on the main checkout (2026-11-12).
const P = '/public';
window.MT = {
  links: {
    spotify: 'https://open.spotify.com/intl-es/artist/3pc90hxACiSUahZmmfYjcI',
    apple: 'https://music.apple.com/us/artist/mafia-tumbada/1777597386',
    youtube: 'https://www.youtube.com/@mafiatumbada',
    instagram: 'https://www.instagram.com/mafia_tumbada_oficial/',
    tiktok: 'https://www.tiktok.com/@mafia_tumbada_oficial',
    // [ask: WhatsApp number] socials.ts and SPEC §4 disagree; this is socials.ts
    whatsapp: 'https://wa.me/5212283538827?text=Hola%20Mafia%20Tumbada%2C%20quiero%20informaci%C3%B3n%20para%20contratarlos.%20Mi%20evento%20es%20el%20%5Bfecha%5D%20en%20%5Bciudad%5D.',
  },
  releases: [
    { t: 'PUTIFRESA', s: 'Single', p: 'Spotify', h: 'https://open.spotify.com/album/1w8U5GJbRsYoGl52QlBDdQ', c: `${P}/music/putifresa.webp` },
    { t: 'L.V.', s: 'Corrido tumbado', p: 'Spotify', h: 'https://open.spotify.com/intl-es/album/070MvKHW6m7CV17k0EeYjz', c: `${P}/music/lv.webp` },
    { t: 'Besos', s: 'Single', p: 'YouTube', h: 'https://youtu.be/kAdwJ-0F8mU', c: `${P}/music/besos.webp` },
    { t: 'Tal Vez', s: 'Corrido tumbado', p: 'Spotify', h: 'https://open.spotify.com/intl-es/track/54nPL89TjXqZ2UYRO1PvBD', c: `${P}/music/tal-vez.webp` },
    { t: 'L.A. BUBU', s: 'Single', p: 'Spotify', h: 'https://open.spotify.com/intl-es/track/5djRHmBwycYgJbqtpF8FPN', c: `${P}/music/la-bubu.webp` },
    { t: 'No Te He Olvidado', s: 'Regional', p: 'Apple Music', h: 'https://music.apple.com/es/song/no-te-he-olvidado/1794933904', c: `${P}/music/no-te-he-olvidado.webp` },
    { t: 'SD', s: 'Single', p: 'Spotify', h: 'https://open.spotify.com/album/6PDeUBPHPutSjOU7mJCMZC', c: `${P}/music/sd.webp` },
    { t: 'Mírame', s: 'Single', p: 'Spotify', h: 'https://open.spotify.com/album/4ha0Wnd1upezqhIsVmWkQ6', c: `${P}/music/mirame.webp` },
    { t: 'Corazón', s: 'Regional', p: 'Apple Music', h: 'https://music.apple.com/es/album/coraz%C3%B3n-single/1779090777', c: `${P}/music/corazon.webp` },
  ],
  videos: [
    { t: 'En vivo en Plaza Lerdo, Xalapa', id: 'XxhXFo-hm-I' },
    { t: 'L.V. (video oficial)', id: 'CDO9iJdIkQk' },
    { t: 'Corazón (video oficial)', id: 'I9BXC3LPlx8' },
    { t: 'Tal Vez, Good Luck Sessions', id: '7Sx0yDjGoq0' },
    { t: 'La Bubu (video oficial)', id: 'h8ZPVsgpAfo' },
  ],
  members: [
    { n: 'Héctor Báez', r: 'Vocal principal', ig: 'hector_baezzzmt_', img: `${P}/members/hector-baez.webp` },
    { n: 'Alexandro Montal', r: 'Requintista y vocal', ig: 'alexandromontal', img: `${P}/members/alexandro-montal.webp` },
    { n: 'Diego Cerecer', r: 'Guitarra y coros', ig: 'diegocerecer', img: `${P}/members/diego-cerecer.webp` },
  ],
};
window.MT.thumb = (id, big) => `https://i.ytimg.com/vi/${id}/${big ? 'maxresdefault' : 'hqdefault'}.jpg`;
window.MT.yt = (id) => `https://www.youtube.com/watch?v=${id}`;
