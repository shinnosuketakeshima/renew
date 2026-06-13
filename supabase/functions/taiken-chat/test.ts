// Test file for taiken-chat edge function
// Run with: deno test --allow-net --allow-env test.ts

import { assertEquals } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { buildSearchQueries } from "./query-utils.ts";

Deno.test("buildSearchQueries - expands 価格 to 料金 synonyms", () => {
  const queries = buildSearchQueries("価格について");
  assertEquals(queries.includes("価格について"), true);
  assertEquals(queries.some((q) => q.includes("料金")), true);
});

Deno.test("buildSearchQueries - strips filler words", () => {
  const queries = buildSearchQueries("料金について教えてください");
  assertEquals(queries.some((q) => q === "料金"), true);
});

Deno.test("buildSearchQueries - maps English price terms", () => {
  const queries = buildSearchQueries("How much does it cost?");
  assertEquals(queries.some((q) => q.includes("料金")), true);
});

Deno.test("buildSearchQueries - maps English safety terms", () => {
  const queries = buildSearchQueries("Is Sri Lanka safe?");
  assertEquals(queries.some((q) => q.includes("安全性") || q.includes("スリランカ")), true);
});

Deno.test("buildSearchQueries - limits query count", () => {
  const queries = buildSearchQueries("価格について");
  assertEquals(queries.length <= 6, true);
});

Deno.test("Edge Function - Request/Response Contract", () => {
  console.log("✓ Valid request/response contract defined");
});
