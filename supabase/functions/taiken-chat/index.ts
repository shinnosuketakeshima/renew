import { serve } from "https://deno.land/std@0.208.0/http/server.ts";

serve(async (req: Request) => {
  // TODO: Implement chat handler
  return new Response(
    JSON.stringify({ message: "Chat API coming soon" }),
    { headers: { "Content-Type": "application/json" } }
  );
});
