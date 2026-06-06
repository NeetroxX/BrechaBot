import { describe, it, expect } from "vitest";
import { loadCorpus, owaspFor, remediationFor } from "../src/corpus/loader.js";
import { isMultiTurn } from "../src/models.js";

const STARTER_IDS = new Set(["PXR-003","PXR-007","PXR-010","PXR-014","PXR-022","PXR-025","PXR-029","PXR-035","PXR-044","PXR-048"]);

describe("corpus", () => {
  it("starter loads", () => {
    const c = loadCorpus();
    expect(c.attacks.length).toBe(10);
    expect(new Set(c.attacks.map((a) => a.id))).toEqual(STARTER_IDS);
  });
  it("has the multilingual + multi-turn members", () => {
    const byId = Object.fromEntries(loadCorpus().attacks.map((a) => [a.id, a]));
    expect(byId["PXR-044"]!.lang).toBe("hi");
    expect(isMultiTurn(byId["PXR-048"]!)).toBe(true);
  });
  it("every attack resolves owasp + remediation", () => {
    const c = loadCorpus();
    for (const a of c.attacks) {
      expect(a.category in c.categories).toBe(true);
      expect(owaspFor(a.category, c.categories)).not.toBe("");
      expect(remediationFor(a.category, c.categories)).not.toBe("");
    }
  });
  it("version is prefixed", () => {
    expect(loadCorpus().version.startsWith("brc-")).toBe(true);
  });
});
