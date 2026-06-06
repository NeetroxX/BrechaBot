import { afterEach, describe, expect, it, vi } from "vitest";
import { mkdtempSync, readFileSync, existsSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

// Mock the orchestrator so the CLI test does no network I/O.
vi.mock("../src/orchestrator.js", () => ({
  runScan: async () => [{
    id: "X", name: "N", category: "Role Hijacking", technique: "", owasp: "LLM01", remediation: "",
    lang: "en", is_multi_turn: false, transcript: [], attack_prompt: "p", bot_reply: "r",
    verdict: "SAFE", severity: "none", reason: "", marker_matches: [], judge_verdict: "SAFE", judge_severity: "none",
  }],
}));

import { buildProgram } from "../src/cli.js";

let dir: string;
afterEach(() => { if (dir) rmSync(dir, { recursive: true, force: true }); });

describe("cli scan", () => {
  it("writes JSON + HTML report", async () => {
    dir = mkdtempSync(join(tmpdir(), "brc-"));
    const out = join(dir, "report.json");
    const html = join(dir, "report.html");
    const program = buildProgram();
    await program.parseAsync(
      ["scan", "--target-url", "https://x", "--out", out, "--html", html],
      { from: "user" },
    );
    const data = JSON.parse(readFileSync(out, "utf-8"));
    expect(data.summary.total).toBe(1);
    expect(data.scanId).toBeTruthy();
    expect(existsSync(html)).toBe(true);
    const reportHtml = readFileSync(html, "utf-8");
    expect(reportHtml).toContain("Red-Team Report");
    expect(reportHtml).toContain("BrechaBot");
  });
});
