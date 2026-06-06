import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { LLMClient } from "../src/llm/client.js";

const server = setupServer();
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("LLMClient", () => {
  it("posts to /chat/completions and returns the message content", async () => {
    let seenAuth: string | null = null;
    let seenBody: any = null;
    server.use(
      http.post("https://judge.test/v1/chat/completions", async ({ request }) => {
        seenAuth = request.headers.get("authorization");
        seenBody = await request.json();
        return HttpResponse.json({ choices: [{ message: { content: "hello" } }] });
      }),
    );
    const client = new LLMClient({
      base_url: "https://judge.test/v1", model: "m", api_key: "k", temperature: 0,
    });
    const out = await client.complete("sys", "usr");
    expect(out).toBe("hello");
    expect(seenAuth).toBe("Bearer k");
    expect(seenBody.model).toBe("m");
    expect(seenBody.messages[0]).toEqual({ role: "system", content: "sys" });
  });
});
