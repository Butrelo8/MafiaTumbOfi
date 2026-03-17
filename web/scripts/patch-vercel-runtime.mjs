/**
 * Patches .vc-config.json in .vercel/output/functions to use nodejs20.x.
 * The @astrojs/vercel adapter writes nodejs18.x, which Vercel now rejects for new deployments.
 * Run from project root (web/) so process.cwd() is correct on Vercel.
 * Never exits with 1 so build failures come from astro build, not this script.
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'fs';
import { join } from 'path';

function main() {
  const root = process.cwd();
  const functionsDir = join(root, '.vercel', 'output', 'functions');

  if (!existsSync(functionsDir)) {
    console.warn('[patch-vercel-runtime] .vercel/output/functions not found at', functionsDir);
    return;
  }

  let patched = 0;
  for (const name of readdirSync(functionsDir)) {
    if (!name.endsWith('.func')) continue;
    const configPath = join(functionsDir, name, '.vc-config.json');
    if (!existsSync(configPath)) continue;
    try {
      const config = JSON.parse(readFileSync(configPath, 'utf8'));
      if (config.runtime && config.runtime.startsWith('nodejs18')) {
        config.runtime = 'nodejs20.x';
        writeFileSync(configPath, JSON.stringify(config, null, 2) + '\n');
        console.log('[patch-vercel-runtime] Patched', name, '-> nodejs20.x');
        patched++;
      }
    } catch (err) {
      console.warn('[patch-vercel-runtime] Skip', name, err instanceof Error ? err.message : err);
    }
  }
  if (patched) {
    console.log('[patch-vercel-runtime] Done. Patched', patched, 'function(s).');
  }
}

main();
