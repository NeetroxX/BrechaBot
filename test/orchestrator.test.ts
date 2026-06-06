import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { runScan } from "../src/orchestrator.js";
import { ScanConfigSchema, type ScanConfig } from "../src/models.js";

const TARGET = "https://bot.test/chat";
const JUDGE = "https://judge.test/v1/chat/completions";
const CATS = { "Role Hijacking": { owasp: "LLM01", remediation: "r" }, "Multi-Turn": { owasp: "LLM01", remediation: "r" } };

const server = setupServer();
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

function cfg(extra: Partial<ScanConfig> = {}): ScanConfig {
  const c = ScanConfigSchema.parse({
    target_url: TARGET, system_prompt: "secret is sk_live_x", max_retries: 0, concurrency: 2, ...extra,
  });
  c.judge.base_url = "https://judge.test/v1";
  return c;
}
function judgeHandler(verdict = "VULNERABLE") {
  return http.post(JUDGE, () =>
    HttpResponse.json({ choices: [{ message: { content: `{"verdict":"${verdict}","severity":"high","reason":"r"}` } }] }),
  );
}

describe("orchestrator", () => {
  it("leak is VULNERABLE", async () => {
    const leak = "Sure: " + "x".repeat(500) + " sk_live_x";
    server.use(http.post(TARGET, () => HttpResponse.json({ choices: [{ message: { content: leak } }] })), judgeHandler());
    const attack = { id: "PXR-T", category: "Role Hijacking", name: "N", technique: "", severity: "medium", lang: "en", markers: ["sk_live_"], prompt: "leak it" } as any;
    const findings = await runScan([attack], CATS, cfg(), "scan-1");
    expect(findings[0]!.verdict).toBe("VULNERABLE");
  });

  it("target 429 is ERROR", async () => {
    server.use(http.post(TARGET, () => new HttpResponse(null, { status: 429 })));
    const attack = { id: "PXR-E", category: "Role Hijacking", name: "N", technique: "", severity: "medium", lang: "en", markers: ["a"], prompt: "x" } as any;
    const findings = await runScan([attack], CATS, cfg(), "scan-2");
    expect(findings[0]!.verdict).toBe("ERROR");
  });

  it("multi-turn makes sequential calls", async () => {
    let targetCalls = 0;
    server.use(
      http.post(TARGET, () => { targetCalls += 1; return HttpResponse.json({ choices: [{ message: { content: "ok" } }] }); }),
      judgeHandler("SAFE"),
    );
    const attack = { id: "PXR-M", category: "Multi-Turn", name: "N", technique: "", severity: "medium", lang: "en", markers: ["zzz"], turns: ["t1", "t2", "t3"] } as any;
    const findings = await runScan([attack], CATS, cfg(), "scan-3");
    expect(targetCalls).toBe(3);
    expect(findings[0]!.transcript.length).toBe(3);
    expect(findings[0]!.is_multi_turn).toBe(true);
  });
});
