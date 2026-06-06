import { describe, it, expect } from "vitest";
import { loadPack, BUILTIN_PACKS } from "../src/corpus/loader.js";

const APPROVED = new Set(["PXR-003","PXR-007","PXR-010","PXR-014","PXR-022","PXR-025","PXR-029","PXR-035","PXR-044","PXR-048"]);

describe("leak guard", () => {
  it("bundled pack is exactly the starter set", () => {
    const ids = new Set(loadPack("starter").attacks.map((a) => a.id));
    expect(ids).toEqual(APPROVED);
  });
  it("only starter is a builtin pack", () => {
    expect(new Set(Object.keys(BUILTIN_PACKS))).toEqual(new Set(["starter"]));
  });
});
