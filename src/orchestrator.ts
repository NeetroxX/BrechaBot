import pLimit from "p-limit";
import pRetry from "p-retry";
import { getAdapter, type Message, type TargetAdapter } from "./adapters/index.js";
import { owaspFor, remediationFor, type Categories } from "./corpus/loader.js";
import { combine } from "./judge/combine.js";
import { judge as runJudge } from "./judge/llmJudge.js";
import { LLMClient } from "./llm/client.js";
import {
  isMultiTurn, turnList, toSeverity, toVerdict,
  type Attack, type Finding, type ScanConfig, type TranscriptTurn,
} from "./models.js";

const TURN_SEP = "\n--- next turn ---\n";
const RETRYABLE_STATUS = new Set([429, 500, 502, 503, 504]);

function parseAuthHeader(auth: string | null | undefined): Record<string, string> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (!auth) return headers;
  const idx = auth.indexOf(":");
  if (idx >= 0) headers[auth.slice(0, idx).trim()] = auth.slice(idx + 1).trim();
  else headers["Authorization"] = auth;
  return headers;
}

async function callTarget(
  url: string, body: unknown, headers: Record<string, string>, timeoutMs: number, maxRetries: number,
): Promise<[unknown | null, string | null]> {
  try {
    const resp = await pRetry(
      async () => {
        const ctrl = new AbortController();
        const timer = setTimeout(() => ctrl.abort(), timeoutMs);
        try {
          const r = await fetch(url, { method: "POST", headers, body: JSON.stringify(body), signal: ctrl.signal });
          if (RETRYABLE_STATUS.has(r.status)) throw new Error(`HTTP ${r.status}`);
          return r;
        } finally {
          clearTimeout(timer);
        }
      },
      { retries: maxRetries, minTimeout: 1000, maxTimeout: 10_000, factor: 2 },
    );
    if (resp.status >= 400) return [null, `HTTP ${resp.status}`];
    try {
      return [await resp.clone().json(), null];
    } catch {
      return [await resp.text(), null];
    }
  } catch (exc) {
    return [null, exc instanceof Error ? exc.message : String(exc)];
  }
}

async function runAttack(
  attack: Attack, cfg: ScanConfig, adapter: TargetAdapter, llm: LLMClient, categories: Categories,
): Promise<Finding> {
  const headers = parseAuthHeader(cfg.auth_header);
  const messages: Message[] = [{ role: "system", content: cfg.system_prompt }];
  const transcript: TranscriptTurn[] = [];
  let reply = "";
  let error: string | null = null;
  const turns = turnList(attack);

  for (let i = 0; i < turns.length; i++) {
    const turn = turns[i]!;
    messages.push({ role: "user", content: turn });
    const body = adapter.buildRequest(messages, cfg);
    const [parsed, err] = await callTarget(cfg.target_url, body, headers, cfg.timeout_s * 1000, cfg.max_retries);
    if (err !== null) {
      error = err;
      transcript.push({ turn: i + 1, user: turn, bot: `[error] ${err}` });
      break;
    }
    reply = adapter.parseReply(parsed).slice(0, 4000);
    messages.push({ role: "assistant", content: reply });
    transcript.push({ turn: i + 1, user: turn, bot: reply });
  }

  const owasp = owaspFor(attack.category, categories);
  const remediation = remediationFor(attack.category, categories);
  const attackPrompt = turns.join(TURN_SEP);
  const base = {
    id: attack.id, name: attack.name, category: attack.category, technique: attack.technique,
    owasp, remediation, lang: attack.lang, is_multi_turn: isMultiTurn(attack),
    transcript, attack_prompt: attackPrompt,
  };

  if (error !== null) {
    return {
      ...base, bot_reply: "", verdict: "ERROR", severity: attack.severity,
      reason: `target-error: ${error}`, marker_matches: [], judge_verdict: "ERROR", judge_severity: "none",
    };
  }

  const judgeResult = await runJudge(llm, cfg.system_prompt, attackPrompt, reply);
  const c = combine(reply, attack.markers, attack.severity, judgeResult);
  return {
    ...base, bot_reply: reply, verdict: toVerdict(c.verdict), severity: toSeverity(c.severity),
    reason: c.reason, marker_matches: c.marker_matches, judge_verdict: c.judge_verdict, judge_severity: c.judge_severity,
  };
}

export async function runScan(
  attacks: Attack[], categories: Categories, cfg: ScanConfig, _scanId: string,
): Promise<Finding[]> {
  const adapter = getAdapter(cfg.schema);
  const llm = new LLMClient(cfg.judge);
  const limit = pLimit(cfg.concurrency);
  return Promise.all(attacks.map((a) => limit(() => runAttack(a, cfg, adapter, llm, categories))));
}
