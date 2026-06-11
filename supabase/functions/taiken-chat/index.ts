import { serve } from "https://deno.land/std@0.208.0/http/server.ts";

// LLM Provider Interface
interface LLMProvider {
  chat(systemPrompt: string, userMessage: string): Promise<string>;
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
                { text: userMessage }
              ]
            }
          ],
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 800
          }
        })
      }
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
        "Authorization": `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: this.model,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userMessage }
        ],
        temperature: 0.7,
        max_tokens: 800
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`DeepSeek API error: ${error}`);
    }

    const json = await response.json();
    return json.choices[0].message.content;
  }
}

// Factory function
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

// Supabase client initialization
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabaseUrl = Deno.env.get("SUPABASE_URL");
const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
if (!supabaseUrl || !supabaseServiceKey) {
  throw new Error("Missing required env: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY");
}
const supabase = createClient(supabaseUrl, supabaseServiceKey);

// Embed text using Google Generative AI
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
        outputDimensionality: 1536
      })
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Embedding API error: ${error}`);
  }

  const json = await response.json();
  return json.embedding.values;
}

// Search for similar taiken experiences
async function searchTaiken(embedding: number[], matchCount: number = 5, threshold: number = 0.6) {
  const { data, error } = await supabase.rpc(
    "match_taiken_experiences",
    {
      query_embedding: embedding,
      match_count: matchCount,
      match_threshold: threshold
    }
  );

  if (error) throw new Error(`Search error: ${error.message}`);
  return data || [];
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

// Main handler
serve(async (req: Request) => {
  const origin = req.headers.get("Origin");
  const headers = corsHeaders(origin);

  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers });
  }

  try {
    // Parse request
    const { question } = await req.json();

    if (!question) {
      return new Response(
        JSON.stringify({ error: "Missing 'question' field" }),
        { status: 400, headers: { "Content-Type": "application/json", ...headers } }
      );
    }

    // 1. Embed the question
    const questionEmbedding = await embedText(question);

    // 2. Search for similar experiences
    const results = await searchTaiken(questionEmbedding, 5, 0.6);

    if (results.length === 0) {
      return new Response(
        JSON.stringify({
          answer: "関連する体験が見つかりませんでした。別の質問をお試しください。",
          sources: []
        }),
        { headers: { "Content-Type": "application/json", ...headers } }
      );
    }

    // 3. Build context from results
    const context = results
      .map((r: any) => {
        return `【${r.title}】\n年: ${r.year}, 国: ${r.country}, 年齢: ${r.age}歳\n\n${r.body.substring(0, 500)}...`;
      })
      .join("\n\n---\n\n");

    // 4. Generate response using LLM
    const llm = createLLMProvider();
    const systemPrompt = `You are a helpful assistant answering questions about study abroad experiences.
Always cite the sources from the experiences.
Respond in Japanese.
Be encouraging and authentic.
Keep responses to 2-3 paragraphs.`;

    const userMessage = `質問: ${question}\n\nコンテキスト:\n${context}`;

    const answer = await llm.chat(systemPrompt, userMessage);

    // 5. Format sources
    const sources = results.map((r: any) => ({
      title: r.title,
      number: r.taiken_number,
      url: `/taiken${r.taiken_number}.html`,
      excerpt: r.body.substring(0, 200),
      country: r.country,
      age: r.age,
      year: r.year,
      similarity: r.similarity
    }));

    return new Response(
      JSON.stringify({ answer, sources }),
      { headers: { "Content-Type": "application/json", ...headers } }
    );

  } catch (error) {
    console.error("Function error:", error instanceof Error ? error.message : "unknown");
    return new Response(
      JSON.stringify({ error: "サーバーエラーが発生しました。しばらくしてからお試しください。" }),
      { status: 500, headers: { "Content-Type": "application/json", ...headers } }
    );
  }
});
