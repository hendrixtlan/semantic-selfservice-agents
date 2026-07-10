#!/usr/bin/env node
/**
 * Compile gate: compila todos los .malloy del árbol semántico.
 * Es EL MISMO gate en tres lugares — Validator, CI y pre-deploy de Publisher —
 * lo que garantiza: "compila en validación" == "compila en CI" == "sirve".
 *
 * Uso:
 *   node scripts/compile_gate.mjs semantic/packages     # todo el árbol (CI)
 *   node scripts/compile_gate.mjs --single archivo.malloy  # un archivo (Validator)
 *
 * Emite a stdout el SQL del último query compilado (para el dry-run EUC).
 */
import { readdirSync, statSync } from "node:fs";
import { resolve, join } from "node:path";
import { SingleConnectionRuntime } from "@malloydata/malloy";
import { BigQueryConnection } from "@malloydata/db-bigquery";

const args = process.argv.slice(2);
const single = args[0] === "--single";
const target = resolve(single ? args[1] : args[0]);

const connection = new BigQueryConnection("bigquery"); // solo metadatos de compilación
const runtime = new SingleConnectionRuntime({ connection });

function* malloyFiles(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) yield* malloyFiles(p);
    else if (name.endsWith(".malloy")) yield p;
  }
}

const files = single ? [target] : [...malloyFiles(target)];
let failed = 0;

for (const file of files) {
  try {
    const model = await runtime.getModel(new URL(`file://${file}`));
    const queries = model._modelDef ? Object.keys(model._modelDef.queryList ?? {}) : [];
    console.error(`✔ ${file}`);
    // Emitir SQL del query final si existe (insumo del dry-run del Validator)
    if (single && model.preparedQuery) {
      process.stdout.write(model.preparedQuery.preparedResult.sql);
    }
  } catch (e) {
    failed++;
    console.error(`✘ ${file}\n  ${e.message}`);
  }
}

if (failed > 0) {
  console.error(`\n${failed} archivo(s) no compilan — gate cerrado.`);
  process.exit(1);
}
console.error(`\n${files.length} archivo(s) compilan — gate abierto.`);
