import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import vercel from '@astrojs/vercel/serverless';
import clerk from '@clerk/astro';

export default defineConfig({
  output: 'server',
  adapter: vercel(),
  integrations: [tailwind(), clerk()],
  vite: {
    server: {
      port: 4321,
    },
  },
});
