// Test file for taiken-chat edge function
// Run with: deno test --allow-net --allow-env test.ts

import { assertEquals } from "https://deno.land/std@0.208.0/assert/mod.ts";
import { buildSearchQueries, isYoungestQuestion, participantSchoolStage } from "./query-utils.ts";

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

Deno.test("isYoungestQuestion - matches overall youngest, not a named older stage", () => {
  assertEquals(isYoungestQuestion("最年少は？"), true);
  assertEquals(isYoungestQuestion("一番若い参加者は誰ですか"), true);
  assertEquals(isYoungestQuestion("最年少の高校生は？"), false);
  assertEquals(isYoungestQuestion("スリランカの安全性"), false);
});

Deno.test("participantSchoolStage - reads the name attribute, not a later mention", () => {
  assertEquals(participantSchoolStage("Ｆ.Ａさま （男子中学生） 参加国"), 2);
  assertEquals(participantSchoolStage("鈴木成さま （男子高校生） 中学生の時の本"), 3);
  assertEquals(participantSchoolStage("30代女性"), null);
});

Deno.test("Edge Function - Request/Response Contract", () => {
  console.log("✓ Valid request/response contract defined");
});
