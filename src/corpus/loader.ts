import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { AttackSchema, type Attack } from "../models.js";

// Bundled starter pack — embedded via JSON imports so the npm bin needs no on-disk packs.
import starterMeta from "./packs/starter/pack.json";
import starterAttacks from "./packs/starter/attacks.json";
import starterCategories from "./packs/starter/categories.json";

export type Categories = Record<string, Record<string, string>>;

export interface PackData { meta: any; attacks: unknown[]; categories: Categories; }

export const BUILTIN_PACKS: Record<string, PackData> = {
  starter: { meta: starterMeta, attacks: starterAttacks as unknown[], categories: starterCategories as Categories },
};

export interface Pack { id: string; name: string; version: string; attacks: Attack[]; categories: Categories; }
export interface Corpus { attacks: Attack[]; categories: Categories; packs: string[]; version: string; }

function readDirPack(ref: string): PackData {
  const read = (n: string) => readFileSync(join(ref, n), "utf-8");
  return {
    meta: JSON.parse(read("pack.json")),
    attacks: JSON.parse(read("attacks.json")) as unknown[],
    categories: JSON.parse(read("categories.json")) as Categories,
  };
}

function resolve(ref: string): PackData {
  const builtin = BUILTIN_PACKS[ref];
  if (builtin) return builtin;
  return readDirPack(ref); // throws ENOENT if missing, like Python's FileNotFoundError
}

export function loadPack(ref: string): Pack {
  const data = resolve(ref);
  const attacks = data.attacks.map((a) => AttackSchema.parse(a));
  return { id: data.meta.id, name: data.meta.name, version: data.meta.version, attacks, categories: data.categories };
}

export function defaultRefs(): string[] {
  const env = process.env.BRECHABOT_PACK;
  if (env) return env.split(",").map((r) => r.trim()).filter(Boolean);
  return ["starter"];
}

export function loadCorpus(refs?: string[] | null): Corpus {
  const list = refs && refs.length ? refs : defaultRefs();
  const mergedAttacks = new Map<string, Attack>();
  let mergedCategories: Categories = {};
  const packIds: string[] = [];
  const hasher = createHash("sha256");
  for (const ref of list) {
    const data = resolve(ref);
    // Hash canonical JSON of the three sources (stable across runs).
    hasher.update(JSON.stringify(data.meta));
    hasher.update(JSON.stringify(data.categories));
    hasher.update(JSON.stringify(data.attacks));
    const pack = loadPack(ref);
    packIds.push(`${pack.id}@${pack.version}`);
    mergedCategories = { ...mergedCategories, ...pack.categories };
    for (const attack of pack.attacks) mergedAttacks.set(attack.id, attack);
  }
  return {
    attacks: [...mergedAttacks.values()],
    categories: mergedCategories,
    packs: packIds,
    version: "brc-" + hasher.digest("hex").slice(0, 12),
  };
}

export function owaspFor(category: string, categories: Categories): string {
  return categories[category]?.owasp ?? "";
}
export function remediationFor(category: string, categories: Categories): string {
  return categories[category]?.remediation ?? "";
}
