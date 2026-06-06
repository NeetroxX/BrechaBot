import { describe, it, expect } from "vitest";
import {
  AttackSchema, ScanConfigSchema, isMultiTurn, turnList, toVerdict, toSeverity,
} from "../src/models.js";

describe("models", () => {
  it("single-turn attack ok", () => {
    const a = AttackSchema.parse({ id: "PXR-001", category: "Role Hijacking", name: "X", prompt: "hi", markers: ["a"] });
    expect(isMultiTurn(a)).toBe(false);
    expect(turnList(a)).toEqual(["hi"]);
  });
  it("multi-turn attack ok", () => {
    const a = AttackSchema.parse({ id: "PXR-046", category: "Multi-Turn", name: "Y", turns: ["t1", "t2"] });
    expect(isMultiTurn(a)).toBe(true);
    expect(turnList(a)).toEqual(["t1", "t2"]);
  });
  it("requires exactly one prompt form", () => {
    expect(() => AttackSchema.parse({ id: "PXR-X", category: "C", name: "N" })).toThrow();
    expect(() => AttackSchema.parse({ id: "PXR-Y", category: "C", name: "N", prompt: "p", turns: ["t"] })).toThrow();
  });
  it("scan config schema alias", () => {
    const cfg = ScanConfigSchema.parse({ target_url: "https://x", schema: "anthropic" });
    expect(cfg.schema).toBe("anthropic");
  });
  it("coercion helpers", () => {
    expect(toVerdict("VULNERABLE")).toBe("VULNERABLE");
    expect(toVerdict("garbage")).toBe("UNKNOWN");
    expect(toSeverity("high")).toBe("high");
    expect(toSeverity("garbage")).toBe("none");
  });
});
