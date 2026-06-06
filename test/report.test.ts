import { describe, it, expect } from "vitest";
import { htmlReport } from "../src/report/html.js";
import { summarize } from "../src/scoring.js";
import type { Finding } from "../src/models.js";

function vuln(): Finding {
  return {
    id: "PXR-030", name: "DELIMITER SHADOW", category: "Token Smuggling", technique: "t",
    owasp: "LLM07: System Prompt Leakage", remediation: "Do not disclose.", lang: "en",
    is_multi_turn: false, transcript: [{ turn: 1, user: "atk", bot: "leaked sk_live_x" }],
    attack_prompt: "atk", bot_reply: "leaked sk_live_x", verdict: "VULNERABLE", severity: "high",
    reason: "Leak markers matched", marker_matches: ["sk_live_"], judge_verdict: "VULNERABLE", judge_severity: "high",
  };
}

describe("html report", () => {
  it("contains key sections", () => {
    const findings = [vuln()];
    const html = htmlReport(summarize(findings), findings, "scan-123");
    expect(html.toLowerCase()).toContain("<!doctype html>");
    expect(html).toContain("OWASP LLM Top 10 Exposure");
    expect(html).toContain("PXR-030");
    expect(html).toContain("DELIMITER SHADOW");
    expect(html).toContain("scan-123");
    expect(html).toContain("REMEDIATION");
    expect(html).toContain("BrechaBot");
  });
  it("escapes HTML in replies", () => {
    const f = vuln();
    f.bot_reply = "<script>alert(1)</script>";
    f.transcript = [{ turn: 1, user: "u", bot: "<script>alert(1)</script>" }];
    const html = htmlReport(summarize([f]), [f], "s");
    expect(html).not.toContain("<script>alert(1)</script>");
    expect(html).toContain("&lt;script&gt;");
  });
});
