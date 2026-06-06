import { describe, it, expect } from "vitest";
import { getAdapter, type Message } from "../src/adapters/index.js";

const cfg = { target_model: "m" } as any;
const msgs: Message[] = [
  { role: "system", content: "S" },
  { role: "user", content: "u1" },
  { role: "assistant", content: "a1" },
  { role: "user", content: "u2" },
];

describe("adapters", () => {
  it("openai builds messages and parses choices", () => {
    const a = getAdapter("openai");
    expect(a.buildRequest(msgs, cfg)).toEqual({ model: "m", messages: msgs });
    expect(a.parseReply({ choices: [{ message: { content: "hi" } }] })).toBe("hi");
  });
  it("anthropic splits system and parses content blocks", () => {
    const a = getAdapter("anthropic");
    const body: any = a.buildRequest(msgs, cfg);
    expect(body.system).toBe("S");
    expect(body.messages.every((m: Message) => m.role !== "system")).toBe(true);
    expect(a.parseReply({ content: [{ text: "x" }, { text: "y" }] })).toBe("xy");
  });
  it("cohere maps history and last message", () => {
    const a = getAdapter("cohere");
    const body: any = a.buildRequest(msgs, cfg);
    expect(body.message).toBe("u2");
    expect(body.preamble).toBe("S");
    expect(body.chat_history[0]).toEqual({ role: "USER", message: "u1" });
    expect(a.parseReply({ text: "hello" })).toBe("hello");
  });
  it("rest uses last user input and fallback extraction", () => {
    const a = getAdapter("rest");
    expect((a.buildRequest(msgs, cfg) as any).input).toBe("u2");
    expect(a.parseReply({ response: "r" })).toBe("r");
  });
  it("unknown schema falls back to openai", () => {
    expect(getAdapter("nope")).toBe(getAdapter("openai"));
  });
});
