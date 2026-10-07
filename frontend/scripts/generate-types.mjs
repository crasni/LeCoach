import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { compile } from 'json-schema-to-typescript';

const schema = JSON.parse(await readFile(new URL('../../contracts/schema.json', import.meta.url)));
const content = await compile(schema, 'ContractSchema', {
  bannerComment: '/* Generated from contracts/schema.json. Run npm run types; do not edit. */',
});
const target = new URL('../src/generated/contracts.ts', import.meta.url);
if (process.argv.includes('--check')) {
  if (await readFile(target, 'utf8') !== content) {
    throw new Error('Generated TypeScript is stale. Run npm run types.');
  }
} else {
  await mkdir(new URL('../src/generated/', import.meta.url), { recursive: true });
  await writeFile(target, content);
}
