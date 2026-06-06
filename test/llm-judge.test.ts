import { describe, it, expect } from "vitest";
import { judge } from "../src/judge/llmJudge.js";

const completer = (raw: string) => ({ complete: async () => raw });
const thrower = { complete: async () => { throw new Error("boom"); } };

describe("llm judge", () => {
  it("parses a clean JSON verdict", async () => {
    const r = await judge(completer('{"verdict":"vulnerable","severity":"High","reason":"leaked"}'), "s", "a", "b");
    expect(r.verdict).toBe("VULNERABLE");
    expect(r.severity).toBe("high");
    expect(r.reason).toBe("leaked");
  });
  it("extracts JSON embedded in prose", async () => {
    const r = await judge(completer('Sure! {"verdict":"SAFE","severity":"none","reason":"ok"} done'), "s", "a", "b");
    expect(r.verdict).toBe("SAFE");
  });
  it("returns UNKNOWN on parse failure", async () => {
    const r = await judge(completer("not json at all"), "s", "a", "b");
    expect(r.verdict).toBe("UNKNOWN");
    expect(r.reason).toContain("judge-parse-error");
  });
  it("returns UNKNOWN on client error", async () => {
    const r = await judge(thrower, "s", "a", "b");
    expect(r.verdict).toBe("UNKNOWN");
    expect(r.reason).toContain("judge-call-error");
  });
});
