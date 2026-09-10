import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://mafiatumbada.com',
  integrations: [tailwind()],
  vite: {
    server: {
      port: 4321,
      // WSL on /mnt/e: inotify doesn't fire, HMR silently serves stale files.
      watch: { usePolling: true, interval: 400 },
    },
  },
});
