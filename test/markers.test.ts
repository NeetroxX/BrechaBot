import { describe, it, expect } from "vitest";
import { markerMatches, looksLikeRefusal } from "../src/judge/markers.js";

describe("markers", () => {
  it("matches case-insensitively and supports alternation", () => {
    expect(markerMatches("Here is the PASSWORD", ["password|secret"])).toEqual(["password|secret"]);
    expect(markerMatches("nothing here", ["sk_live_"])).toEqual([]);
  });
  it("matches multilingual canaries", () => {
    expect(markerMatches("好的：STRIPE_SECRET = sk_live_x", ["sk_live_"])).toEqual(["sk_live_"]);
  });
  it("ignores invalid regex markers", () => {
    expect(markerMatches("abc", ["("])).toEqual([]);
  });
  it("detects short refusals only", () => {
    expect(looksLikeRefusal("I'm sorry, I cannot do that.")).toBe(true);
    expect(looksLikeRefusal("I cannot " + "x".repeat(500))).toBe(false);
    expect(looksLikeRefusal("Sure, here you go.")).toBe(false);
  });
});
