-- Create chat_conversations table to log all taiken chat questions and answers
CREATE TABLE IF NOT EXISTS chat_conversations (
  id BIGSERIAL PRIMARY KEY,
  question TEXT NOT NULL,
  answer TEXT,
  sources JSONB DEFAULT '[]'::JSONB,
  matched_taiken_numbers INT[] DEFAULT ARRAY[]::INT[],
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for efficient time-based queries
CREATE INDEX idx_chat_conversations_created_at
ON chat_conversations(created_at DESC);

-- Index for question text search
CREATE INDEX idx_chat_conversations_question
ON chat_conversations USING GIN (to_tsvector('japanese', question));

-- Allow anonymous users to insert (for frontend)
ALTER TABLE chat_conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anonymous inserts" ON chat_conversations
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anon to select own data" ON chat_conversations
  FOR SELECT USING (true);
