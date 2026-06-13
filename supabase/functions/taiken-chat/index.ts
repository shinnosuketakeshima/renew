import { serve } from "https://deno.land/std@0.208.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { buildSearchQueries, buildSystemPrompt } from "./query-utils.ts";

interface LLMProvider {
  chat(systemPrompt: string, userMessage: string): Promise<string>;
}

interface TaikenResult {
  taiken_number: number;
  title: string;
  body: string;
  country: string;
  age: number | null;
  year: number | null;
  url: string;
  similarity: number;
}

// Gemini Provider
class GeminiProvider implements LLMProvider {
  private apiKey: string;
  private model: string = "gemini-2.5-flash-lite";

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async chat(systemPrompt: string, userMessage: string): Promise<string> {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${this.model}:generateContent?key=${this.apiKey}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [
            {
              role: "user",
              parts: [
                { text: systemPrompt },
                { text: userMessage },
              ],
            },
          ],
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 800,
          },
        }),
      },
    );

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Gemini API error: ${error}`);
    }

    const json = await response.json();
    return json.candidates[0].content.parts[0].text;
  }
}

// DeepSeek Provider (for future use)
class DeepSeekProvider implements LLMProvider {
  private apiKey: string;
  private model: string = "deepseek-chat";

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async chat(systemPrompt: string, userMessage: string): Promise<string> {
    const response = await fetch("https://api.deepseek.com/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: this.model,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userMessage },
        ],
        temperature: 0.7,
        max_tokens: 800,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`DeepSeek API error: ${error}`);
    }

    const json = await response.json();
    return json.choices[0].message.content;
  }
}

function createLLMProvider(): LLMProvider {
  const providerName = Deno.env.get("LLM_PROVIDER") || "gemini";

  if (providerName === "gemini") {
    const apiKey = Deno.env.get("GOOGLE_API_KEY");
    if (!apiKey) throw new Error("Missing GOOGLE_API_KEY");
    return new GeminiProvider(apiKey);
  }

  if (providerName === "deepseek") {
    const apiKey = Deno.env.get("DEEPSEEK_API_KEY");
    if (!apiKey) throw new Error("Missing DEEPSEEK_API_KEY");
    return new DeepSeekProvider(apiKey);
  }

  throw new Error(`Unknown LLM provider: ${providerName}`);
}

const supabaseUrl = Deno.env.get("SUPABASE_URL");
const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
if (!supabaseUrl || !supabaseServiceKey) {
  throw new Error("Missing required env: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY");
}
const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function embedText(text: string): Promise<number[]> {
  const apiKey = Deno.env.get("GOOGLE_API_KEY");
  if (!apiKey) throw new Error("Missing GOOGLE_API_KEY");

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key=${apiKey}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "models/gemini-embedding-001",
        content: { parts: [{ text }] },
        taskType: "RETRIEVAL_QUERY",
        outputDimensionality: 1536,
      }),
    },
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Embedding API error: ${error}`);
  }

  const json = await response.json();
  return json.embedding.values;
}

async function searchTaiken(
  embedding: number[],
  matchCount: number = 5,
  threshold: number = 0.55,
): Promise<TaikenResult[]> {
  const { data, error } = await supabase.rpc(
    "match_taiken_experiences",
    {
      query_embedding: embedding,
      match_count: matchCount,
      match_threshold: threshold,
    },
  );

  if (error) throw new Error(`Search error: ${error.message}`);
  return (data || []) as TaikenResult[];
}

/** Search with multiple query variants and merge by best similarity per article */
async function searchTaikenMulti(
  queries: string[],
  matchCount: number = 5,
  threshold: number = 0.55,
): Promise<TaikenResult[]> {
  const seen = new Map<number, TaikenResult>();

  for (const query of queries) {
    const embedding = await embedText(query);
    const results = await searchTaiken(embedding, matchCount, threshold);

    for (const result of results) {
      const existing = seen.get(result.taiken_number);
      if (!existing || result.similarity > existing.similarity) {
        seen.set(result.taiken_number, result);
      }
    }
  }

  return [...seen.values()]
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, matchCount);
}

const ALLOWED_ORIGINS = [
  "https://be-intl.com",
  "https://www.be-intl.com",
  "http://localhost:8765",
  "http://localhost:3000",
];

function corsHeaders(origin: string | null): Record<string, string> {
  const allowed = origin && ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": allowed,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Vary": "Origin",
  };
}

serve(async (req: Request) => {
  const origin = req.headers.get("Origin");
  const headers = corsHeaders(origin);

  if (req.method === "OPTIONS") {
    return new Response("ok", { headers });
  }

  try {
    const { question } = await req.json();

    if (!question) {
      return new Response(
        JSON.stringify({ error: "Missing 'question' field" }),
        { status: 400, headers: { "Content-Type": "application/json", ...headers } },
      );
    }

    console.log(`[chat_question] ${new Date().toISOString()} | ${question}`);

    const searchQueries = buildSearchQueries(question);
    console.log(`[chat_search_queries] ${searchQueries.join(" | ")}`);

    // 1. Multi-query vector search (synonym-expanded)
    let results = await searchTaikenMulti(searchQueries, 5, 0.55);

    // 2. Retry with lower threshold if no matches
    if (results.length === 0) {
      const primaryEmbedding = await embedText(question);
      results = await searchTaiken(primaryEmbedding, 5, 0.4);
    }

    // 3. Build context (always proceed to LLM — site knowledge fills gaps)
    const context = results.length > 0
      ? results
        .map((r) =>
          `【${r.title}】\n年: ${r.year ?? "不明"}, 国: ${r.country}, 年齢: ${r.age ?? "不明"}歳\n\n${r.body.substring(0, 500)}...`
        )
        .join("\n\n---\n\n")
      : "（該当する体験記事は見つかりませんでした。サイト基本情報を参考に回答してください。）";

    // 4. Generate response
    const llm = createLLMProvider();
    const systemPrompt = buildSystemPrompt();
    const userMessage = `質問: ${question}\n\n体験記事コンテキスト:\n${context}`;

    const answer = await llm.chat(systemPrompt, userMessage);

    const sources = results.map((r) => ({
      title: r.title,
      number: r.taiken_number,
      url: `/taiken${r.taiken_number}.html`,
      excerpt: r.body.substring(0, 200),
      country: r.country,
      age: r.age,
      year: r.year,
      similarity: r.similarity,
    }));

    return new Response(
      JSON.stringify({ answer, sources }),
      { headers: { "Content-Type": "application/json", ...headers } },
    );
  } catch (error) {
    console.error("Function error:", error instanceof Error ? error.message : "unknown");
    return new Response(
      JSON.stringify({ error: "サーバーエラーが発生しました。しばらくしてからお試しください。" }),
      { status: 500, headers: { "Content-Type": "application/json", ...headers } },
    );
  }
});
