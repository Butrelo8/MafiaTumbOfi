import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://mafiatumbada.com',
  integrations: [tailwind()],
  vite: {
    server: {
      port: 4321,
    },
  },
});
