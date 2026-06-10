import { readFileSync, writeFileSync } from "node:fs";
import { argv } from "node:process";
import { Command } from "commander";
import { parse as parseYaml } from "yaml";
import { loadCorpus } from "./corpus/loader.js";
import { isMultiTurn, ScanConfigSchema, type ScanResult } from "./models.js";
import { runScan } from "./orchestrator.js";
import { htmlReport } from "./report/html.js";
import { summarize } from "./scoring.js";

const VERSION = "0.1.2";

function nowIso(): string { return new Date().toISOString(); }
function collect(value: string, prev: string[]): string[] { return prev.concat([value]); }

export function buildProgram(): Command {
  const program = new Command();
  program.name("brechabot").description("AI chatbot red-team engine (PXR corpus + two-layer judge).");

  program.command("version").description("Print the engine and corpus versions.").action(() => {
    console.log(`brechabot ${VERSION} (${loadCorpus().version})`);
  });

  const corpus = program.command("corpus").description("Inspect the attack corpus.");
  corpus.command("list").description("List attacks and OWASP coverage.")
    .option("--pack <ref>", "Attack pack (repeatable)", collect, [])
    .action((opts: { pack: string[] }) => {
      const c = loadCorpus(opts.pack.length ? opts.pack : null);
      for (const a of c.attacks) {
        const kind = isMultiTurn(a) ? "multi" : "single";
        console.log(`${a.id}  [${a.severity.padEnd(6)}] ${kind.padEnd(6)} ${a.category} — ${a.name}`);
      }
      console.log(`\nPacks: ${c.packs.join(", ")} — ${c.attacks.length} attacks`);
    });
  corpus.command("validate").description("Validate the corpus loads and maps OWASP + remediation.")
    .option("--pack <ref>", "Attack pack (repeatable)", collect, [])
    .action((opts: { pack: string[] }) => {
      const c = loadCorpus(opts.pack.length ? opts.pack : null);
      const missing = c.attacks.filter((a) => !(a.category in c.categories)).map((a) => a.id);
      if (missing.length) {
        console.log(`INVALID: attacks with unmapped category: ${missing.join(", ")}`);
        process.exitCode = 1;
        return;
      }
      console.log(`OK: ${c.attacks.length} attacks, ${Object.keys(c.categories).length} categories, all mapped.`);
    });

  program.command("scan").description("Run a red-team scan against a target chatbot.")
    .requiredOption("--target-url <url>", "Target chatbot endpoint.")
    .option("--schema <schema>", "openai|anthropic|cohere|rest", "openai")
    .option("--target-model <model>", "Target model", "gpt-4o-mini")
    .option("--auth <header>", 'e.g. "Authorization: Bearer X"')
    .option("--system-prompt-file <path>", "Optional white-box: file with the target's system prompt. Omit for a black-box scan.")
    .option("--judge-base-url <url>", "Judge base URL", "http://localhost:11434/v1")
    .option("--judge-model <model>", "Judge model", "gemma4:31b-cloud")
    .option("--judge-key <key>", "Judge API key")
    .option("--profile <profile>", "Profile", "full")
    .option("--concurrency <n>", "Concurrency", (v) => parseInt(v, 10), 4)
    .option("--pack <ref>", "Attack pack(s): builtin name or path (repeatable).", collect, [])
    .option("--out <path>", "JSON report path", "report.json")
    .option("--html <path>", "HTML report path")
    .option("--config <path>", "YAML config (overrides flags).")
    .action(async (opts: any) => {
      const cfg = opts.config
        ? ScanConfigSchema.parse(parseYaml(readFileSync(opts.config, "utf-8")))
        : ScanConfigSchema.parse({
            target_url: opts.targetUrl,
            schema: opts.schema,
            target_model: opts.targetModel,
            system_prompt: opts.systemPromptFile ? readFileSync(opts.systemPromptFile, "utf-8") : null,
            auth_header: opts.auth ?? null,
            judge: { base_url: opts.judgeBaseUrl, model: opts.judgeModel, api_key: opts.judgeKey ?? null },
            profile: opts.profile,
            concurrency: opts.concurrency,
          });

      const c = loadCorpus(opts.pack.length ? opts.pack : null);
      const scanId = String(Date.now());
      const started = nowIso();
      const findings = await runScan(c.attacks, c.categories, cfg, scanId);
      const finished = nowIso();

      const summary = summarize(findings);
      const reportHtml = htmlReport(summary, findings, scanId);
      const result: ScanResult = {
        scanId, corpus_version: c.version, started_at: started, finished_at: finished, summary, findings, html: reportHtml,
      };
      writeFileSync(opts.out, JSON.stringify(result, null, 2), "utf-8");
      if (opts.html) writeFileSync(opts.html, reportHtml, "utf-8");

      console.log(
        `Grade ${summary.grade}  Score ${summary.score}/100  ` +
        `VULN:${summary.vulnerable} PARTIAL:${summary.partial} SAFE:${summary.safe} /${summary.total}  -> ${opts.out}`,
      );
    });

  return program;
}

export function main(): void {
  buildProgram().parseAsync(argv).catch((err) => {
    console.error(err instanceof Error ? err.message : String(err));
    process.exitCode = 1;
  });
}
