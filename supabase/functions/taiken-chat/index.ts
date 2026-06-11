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

// Main handler (stub - placeholder for now)
serve(async (req: Request) => {
  try {
    const llm = createLLMProvider();

    // TODO: Implement chat handler with vector search (Task 7)

    return new Response(
      JSON.stringify({ message: "Chat API ready for vector search integration" }),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
