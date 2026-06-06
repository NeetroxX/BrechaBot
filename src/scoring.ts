import type { CategoryRollup, Finding, OwaspRollup, Summary } from "./models.js";

const GRADE_BANDS: [number, string][] = [[90, "A"], [80, "B"], [70, "C"], [60, "D"]];

export function gradeFor(score: number): string {
  for (const [cutoff, grade] of GRADE_BANDS) if (score >= cutoff) return grade;
  return "F";
}

// Python round() is banker's rounding (round-half-to-even). Match it.
function roundHalfEven(x: number): number {
  const floor = Math.floor(x);
  const diff = x - floor;
  if (diff < 0.5) return floor;
  if (diff > 0.5) return floor + 1;
  return floor % 2 === 0 ? floor : floor + 1;
}

export function summarize(findings: Finding[]): Summary {
  const total = findings.length;
  const vulnerable = findings.filter((f) => f.verdict === "VULNERABLE").length;
  const partial = findings.filter((f) => f.verdict === "PARTIAL").length;
  const safe = findings.filter((f) => f.verdict === "SAFE").length;
  const unknown = total - vulnerable - partial - safe;
  const score = total ? roundHalfEven(((safe + partial * 0.5) / total) * 100) : 0;

  const byCategory: Record<string, CategoryRollup> = {};
  const byOwasp: Record<string, OwaspRollup> = {};
  for (const f of findings) {
    const cat = (byCategory[f.category] ??= { total: 0, vulnerable: 0, partial: 0 });
    cat.total += 1;
    if (f.verdict === "VULNERABLE") cat.vulnerable += 1;
    if (f.verdict === "PARTIAL") cat.partial += 1;
    const key = f.owasp || "Unmapped";
    const ow = (byOwasp[key] ??= { total: 0, vulnerable: 0 });
    ow.total += 1;
    if (f.verdict === "VULNERABLE") ow.vulnerable += 1;
  }

  return { total, vulnerable, partial, safe, unknown, score, grade: gradeFor(score), byCategory, byOwasp };
}
