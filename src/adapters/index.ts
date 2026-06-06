import type { ScanConfig } from "../models.js";

export interface Message { role: string; content: string; }

export interface TargetAdapter {
  buildRequest(messages: Message[], cfg: ScanConfig): Record<string, any>;
  parseReply(resp: any): string;
}

function systemOf(messages: Message[]): string {
  return messages.find((m) => m.role === "system")?.content ?? "";
}
function nonSystem(messages: Message[]): Message[] {
  return messages.filter((m) => m.role !== "system");
}
function fallbackExtract(resp: any): string {
  if (typeof resp === "string") return resp;
  if (resp && typeof resp === "object") {
    for (const key of ["response", "output", "reply", "text"]) {
      if (typeof resp[key] === "string") return resp[key];
    }
    if (resp.message && typeof resp.message === "object" && typeof resp.message.content === "string") {
      return resp.message.content;
    }
    return JSON.stringify(resp);
  }
  return String(resp);
}

const openai: TargetAdapter = {
  buildRequest: (messages, cfg) => ({ model: cfg.target_model, messages }),
  parseReply: (resp) => {
    try {
      if (resp && typeof resp === "object" && Array.isArray(resp.choices) && resp.choices[0]) {
        const choice = resp.choices[0];
        return (choice.message?.content ?? choice.text ?? "") as string;
      }
    } catch {
      /* fall through */
    }
    return fallbackExtract(resp);
  },
};

const anthropic: TargetAdapter = {
  buildRequest: (messages, cfg) => ({
    model: cfg.target_model,
    max_tokens: 1024,
    system: systemOf(messages),
    messages: nonSystem(messages),
  }),
  parseReply: (resp) => {
    if (resp && typeof resp === "object") {
      if (Array.isArray(resp.content)) {
        return resp.content.map((c: any) => (c && typeof c === "object" ? c.text ?? "" : "")).join("");
      }
      if (typeof resp.completion === "string") return resp.completion;
    }
    return fallbackExtract(resp);
  },
};

const cohere: TargetAdapter = {
  buildRequest: (messages, cfg) => {
    const convo = nonSystem(messages);
    const history = convo.slice(0, -1);
    const last = convo.length ? convo[convo.length - 1]!.content : "";
    return {
      model: cfg.target_model,
      preamble: systemOf(messages),
      chat_history: history.map((m) => ({ role: m.role === "user" ? "USER" : "CHATBOT", message: m.content })),
      message: last,
    };
  },
  parseReply: (resp) => {
    if (resp && typeof resp === "object") {
      if (typeof resp.text === "string") return resp.text;
      const content = resp.message?.content;
      if (Array.isArray(content) && content[0] && typeof content[0] === "object") {
        return content[0].text ?? "";
      }
    }
    return fallbackExtract(resp);
  },
};

const rest: TargetAdapter = {
  buildRequest: (messages) => {
    const users = messages.filter((m) => m.role === "user").map((m) => m.content);
    return { system: systemOf(messages), input: users.length ? users[users.length - 1] : "", messages: nonSystem(messages) };
  },
  parseReply: (resp) => fallbackExtract(resp),
};

const ADAPTERS: Record<string, TargetAdapter> = { openai, anthropic, cohere, rest };

export function getAdapter(schema: string): TargetAdapter {
  return ADAPTERS[schema] ?? ADAPTERS["openai"]!;
}
