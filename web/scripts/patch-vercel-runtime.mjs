/**
 * Patches .vc-config.json in .vercel/output/functions to use nodejs20.x.
 * The @astrojs/vercel adapter writes nodejs18.x, which Vercel now rejects for new deployments.
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const functionsDir = join(root, '.vercel', 'output', 'functions');

if (!existsSync(functionsDir)) {
  process.exit(0);
}

for (const name of readdirSync(functionsDir)) {
  if (!name.endsWith('.func')) continue;
  const configPath = join(functionsDir, name, '.vc-config.json');
  if (!existsSync(configPath)) continue;
  const config = JSON.parse(readFileSync(configPath, 'utf8'));
  if (config.runtime && config.runtime.startsWith('nodejs18')) {
    config.runtime = 'nodejs20.x';
    writeFileSync(configPath, JSON.stringify(config, null, 2) + '\n');
    console.log(`Patched ${name} runtime to nodejs20.x`);
  }
}
