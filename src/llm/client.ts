import type { JudgeConfig } from "../models.js";

export class LLMClient {
  constructor(private cfg: JudgeConfig, private timeoutMs = 60_000) {}

  async complete(system: string, user: string): Promise<string> {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (this.cfg.api_key) headers["Authorization"] = `Bearer ${this.cfg.api_key}`;
    const body = {
      model: this.cfg.model,
      temperature: this.cfg.temperature,
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
    };
    const url = this.cfg.base_url.replace(/\/+$/, "") + "/chat/completions";
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), this.timeoutMs);
    try {
      const resp = await fetch(url, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
        signal: ctrl.signal,
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data: any = await resp.json();
      return data.choices[0].message.content;
    } finally {
      clearTimeout(timer);
    }
  }
}
