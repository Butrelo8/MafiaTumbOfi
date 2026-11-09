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
      // tailnet check from other devices (bun dev --port 3100 --host)
      allowedHosts: ['thiccpc.tail82d42e.ts.net', 'thiccpc-wsl', 'thiccpc-wsl.tail82d42e.ts.net'],
    },
    preview: { allowedHosts: ['thiccpc.tail82d42e.ts.net', 'thiccpc-wsl', 'thiccpc-wsl.tail82d42e.ts.net'] },
  },
});
