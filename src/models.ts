import { z } from "zod";

export const VERDICTS = ["VULNERABLE", "PARTIAL", "SAFE", "UNKNOWN", "ERROR"] as const;
export type Verdict = (typeof VERDICTS)[number];
export const SEVERITIES = ["high", "medium", "low", "none"] as const;
export type Severity = (typeof SEVERITIES)[number];

export function toVerdict(value: string): Verdict {
  return (VERDICTS as readonly string[]).includes(value) ? (value as Verdict) : "UNKNOWN";
}
export function toSeverity(value: string): Severity {
  return (SEVERITIES as readonly string[]).includes(value) ? (value as Severity) : "none";
}

export const AttackSchema = z
  .object({
    id: z.string(),
    category: z.string(),
    name: z.string(),
    technique: z.string().default(""),
    severity: z.enum(SEVERITIES).default("medium"),
    prompt: z.string().nullish(),
    turns: z.array(z.string()).nullish(),
    markers: z.array(z.string()).default([]),
    lang: z.string().default("en"),
  })
  .refine(
    (a) => (a.prompt != null) !== !!(a.turns && a.turns.length > 0),
    (a) => ({ message: `${a.id}: provide exactly one of 'prompt' or 'turns'` }),
  );
export type Attack = z.infer<typeof AttackSchema>;

export function turnList(a: Attack): string[] {
  return a.turns && a.turns.length > 0 ? a.turns : [a.prompt ?? ""];
}
export function isMultiTurn(a: Attack): boolean {
  return a.turns != null && a.turns.length > 1;
}

export const JudgeConfigSchema = z.object({
  base_url: z.string().default("http://localhost:11434/v1"),
  model: z.string().default("gemma4:31b-cloud"),
  api_key: z.string().nullish(),
  temperature: z.number().default(0.0),
});
export type JudgeConfig = z.infer<typeof JudgeConfigSchema>;

export const SCHEMAS = ["openai", "anthropic", "cohere", "rest"] as const;
export type TargetSchema = (typeof SCHEMAS)[number];

export const ScanConfigSchema = z.object({
  target_url: z.string(),
  schema: z.enum(SCHEMAS).default("openai"),
  target_model: z.string().default("gpt-4o-mini"),
  system_prompt: z.string().default("You are a helpful assistant."),
  auth_header: z.string().nullish(),
  judge: JudgeConfigSchema.default({}),
  profile: z.string().default("full"),
  concurrency: z.number().default(4),
  timeout_s: z.number().default(90.0),
  max_retries: z.number().default(2),
});
export type ScanConfig = z.infer<typeof ScanConfigSchema>;

export interface TranscriptTurn { turn: number; user: string; bot: string; }

export interface Finding {
  id: string;
  name: string;
  category: string;
  technique: string;
  owasp: string;
  remediation: string;
  lang: string;
  is_multi_turn: boolean;
  transcript: TranscriptTurn[];
  attack_prompt: string;
  bot_reply: string;
  verdict: Verdict;
  severity: Severity;
  reason: string;
  marker_matches: string[];
  judge_verdict: string;
  judge_severity: string;
}

export interface ScanResult {
  scanId: string;
  corpus_version: string;
  started_at: string;
  finished_at: string;
  summary: Summary;
  findings: Finding[];
  html: string;
}

export interface OwaspRollup { total: number; vulnerable: number; }
export interface CategoryRollup { total: number; vulnerable: number; partial: number; }
export interface Summary {
  total: number;
  vulnerable: number;
  partial: number;
  safe: number;
  unknown: number;
  score: number;
  grade: string;
  byCategory: Record<string, CategoryRollup>;
  byOwasp: Record<string, OwaspRollup>;
}
