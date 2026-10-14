import { afterAll, describe, expect, test } from 'bun:test';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const SCRIPT = join(import.meta.dir, 'assets-stale.sh');
const REAL_MAP = join(import.meta.dir, '..', 'docs', 'assets', 'map.tsv');
const HEADER = 'id kind chapter path version built_from recipe settings status evidence confirmed'.split(' ');
const dir = mkdtempSync(join(tmpdir(), 'assets-stale-'));
afterAll(() => rmSync(dir, { recursive: true, force: true }));

type Row = Partial<Record<(typeof HEADER)[number], string>> & { id: string };
const row = (r: Row) => ({
  kind: 'plate', chapter: 'x', path: `tmp/${r.id}`, version: 'v1', built_from: '-', recipe: 'unversioned',
  settings: '-', status: 'approved 2026-10-14', evidence: 'docs/x.md', confirmed: 'yes', ...r,
});

let n = 0;
function mapa(rows: Row[], raw?: string[]): string {
  const file = join(dir, `m${n++}.tsv`);
  const lines = rows.map((r) => HEADER.map((h) => (row(r) as Record<string, string>)[h]).join('\t'));
  writeFileSync(file, [HEADER.join('\t'), '# comentario', ...lines, ...(raw ?? [])].join('\n') + '\n');
  return file;
}

function run(file: string, ...args: string[]) {
  const p = Bun.spawnSync(['bash', SCRIPT, ...args], { env: { ...process.env, MAPA: file } });
  return { code: p.exitCode, out: p.stdout.toString(), err: p.stderr.toString() };
}

// plate → loop → transition → entrega; loop2 shares the recipe with loop; one superseded plate nobody builds on.
const CADENA: Row[] = [
  { id: 'plate-a', kind: 'plate', recipe: 'klein-plate@1' },
  { id: 'plate-a-v0', kind: 'plate', status: 'superseded', recipe: 'klein-plate@0' },
  { id: 'loop-a', kind: 'loop', built_from: 'plate-a@v1', recipe: 'loop-vivo@2' },
  { id: 'loop-b', kind: 'loop', built_from: 'plate-a-v0@v1', recipe: 'loop-vivo@2', status: 'superseded' },
  { id: 'trans-ab', kind: 'transition', built_from: 'loop-a@v1;loop-b@v1', recipe: 'transition-fasth3@1' },
  { id: 'ent-ab', kind: 'entrega', built_from: 'trans-ab@v1', path: 'entrega/ab-*.mp4' },
];
const ids = (out: string) => out.trim().split('\n').filter(Boolean).map((l) => l.split('\t')[0]);

describe('assets-stale.sh', () => {
  test('id: lists every descendant transitively, not itself, with status and path', () => {
    const r = run(mapa(CADENA), 'plate-a');
    expect(r.code).toBe(0);
    expect(ids(r.out)).toEqual(['loop-a', 'trans-ab', 'ent-ab']);
    expect(r.out).toContain('trans-ab\tapproved 2026-10-14\ttmp/trans-ab');
  });

  test('id: a changed intermediate lists only what is below it', () => {
    expect(ids(run(mapa(CADENA), 'loop-a').out)).toEqual(['trans-ab', 'ent-ab']);
  });

  test('id: the version in built_from is ignored; a superseded descendant is still listed', () => {
    expect(ids(run(mapa(CADENA), 'plate-a-v0').out)).toEqual(['loop-b', 'trans-ab', 'ent-ab']);
  });

  test('id without descendants: empty output, exit 0', () => {
    const r = run(mapa(CADENA), 'ent-ab');
    expect(r.code).toBe(0);
    expect(r.out).toBe('');
  });

  test('recipe: the rows using it plus their descendants, once each', () => {
    const r = run(mapa(CADENA), 'loop-vivo@2');
    expect(r.code).toBe(0);
    expect(ids(r.out)).toEqual(['loop-a', 'loop-b', 'trans-ab', 'ent-ab']);
  });

  test('recipe with no other users: just that row and below', () => {
    expect(ids(run(mapa(CADENA), 'transition-fasth3@1').out)).toEqual(['trans-ab', 'ent-ab']);
  });

  test('a cycle terminates', () => {
    const r = run(mapa([{ id: 'p', built_from: 'q' }, { id: 'q', built_from: 'p' }]), 'p');
    expect(r.code).toBe(0);
    expect(ids(r.out)).toEqual(['q']);
  });

  test('no argument: exit 2 with usage', () => {
    const r = run(mapa(CADENA));
    expect(r.code).toBe(2);
    expect(r.err).toContain('uso');
  });

  test('unknown argument: exit 1 naming it', () => {
    const r = run(mapa(CADENA), 'nope');
    expect(r.code).toBe(1);
    expect(r.err).toContain('nope');
  });

  test('unversioned is not queryable', () => {
    const r = run(mapa(CADENA), 'unversioned');
    expect(r.code).toBe(1);
    expect(r.err).toContain('unversioned');
  });

  test('missing map: exit 1', () => {
    const r = run(join(dir, 'no-existe.tsv'), 'x');
    expect(r.code).toBe(1);
    expect(r.err).toContain('no-existe.tsv');
  });

  describe('the map is validated on every read', () => {
    test('wrong column count', () => {
      const r = run(mapa(CADENA, ['solo\tdos']), 'plate-a');
      expect(r.code).toBe(1);
      expect(r.err).toContain('columnas');
    });
    test('duplicate id', () => {
      const r = run(mapa([...CADENA, { id: 'loop-a' }]), 'plate-a');
      expect(r.code).toBe(1);
      expect(r.err).toContain('duplicado');
    });
    test('empty cell', () => {
      const r = run(mapa([{ id: 'a', settings: '' }]), 'a');
      expect(r.code).toBe(1);
      expect(r.err).toContain('vacía');
    });
    test('bad kind', () => {
      const r = run(mapa([{ id: 'a', kind: 'video' }]), 'a');
      expect(r.code).toBe(1);
      expect(r.err).toContain('kind');
    });
    test('bad status', () => {
      const r = run(mapa([{ id: 'a', status: 'approved' }]), 'a');
      expect(r.code).toBe(1);
      expect(r.err).toContain('status');
    });
    test('bad confirmed', () => {
      const r = run(mapa([{ id: 'a', confirmed: 'maybe' }]), 'a');
      expect(r.code).toBe(1);
      expect(r.err).toContain('confirmed');
    });
    test('bad id', () => {
      const r = run(mapa([{ id: 'Bad Id' }]), 'a');
      expect(r.code).toBe(1);
      expect(r.err).toContain('id');
    });
    test('dangling built_from', () => {
      const r = run(mapa([{ id: 'a', built_from: 'ghost@v1' }]), 'a');
      expect(r.code).toBe(1);
      expect(r.err).toContain('ghost');
    });
    test('bad recipe', () => {
      const r = run(mapa([{ id: 'a', recipe: 'sin-version' }]), 'a');
      expect(r.code).toBe(1);
      expect(r.err).toContain('recipe');
    });
  });
});

describe('docs/assets/map.tsv', () => {
  test('passes the same validation', () => {
    const r = run(REAL_MAP, 'id-que-no-existe');
    // exit 1 for "unknown argument" is fine; any validation failure says so on stderr first.
    expect(r.err).not.toMatch(/columnas|duplicado|inválid|colgante|vacía/);
    expect(r.err).toContain('id-que-no-existe');
  });

  // The incident that motivated the map: a transition pointed at the atrio plate v3 instead of v5.
  test('a new atrio plate reaches its loops, the cripta→atrio transitions and what is served, not the vestidor', () => {
    const r = run(REAL_MAP, 'atrio-placa');
    expect(r.code).toBe(0);
    const got = ids(r.out);
    for (const id of ['loop-atrio-esc', 'loop-atrio-movil', 'contratacion-ida-job3', 'contratacion-ida-fasth3-s3', 'entrega-atrio-esc', 'entrega-contratacion-ida'])
      expect(got).toContain(id);
    expect(got.filter((i) => /vestidor|cripta-esc|nave/.test(i))).toEqual([]);
  });

  test('a changed vestidor loop reaches both camarín transitions (graded f0 ends)', () => {
    const got = ids(run(REAL_MAP, 'loop-vestidor-esc').out);
    for (const id of ['grupo-ida-fasth3', 'musica-ida-job4', 'entrega-vestidor-esc']) expect(got).toContain(id);
  });

  test('transition-fasth3@1 lists every FastH3 take', () => {
    expect(ids(run(REAL_MAP, 'transition-fasth3@1').out)).toEqual(
      expect.arrayContaining(['grupo-ida-fasth3', 'contratacion-ida-fasth3-s1', 'contratacion-ida-fasth3-s3']),
    );
  });
});
