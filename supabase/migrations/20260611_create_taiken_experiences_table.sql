-- Create taiken_experiences table for storing vectorized participant experiences
CREATE TABLE IF NOT EXISTS taiken_experiences (
  id BIGSERIAL PRIMARY KEY,
  taiken_number INT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  country TEXT NOT NULL,
  age INT,
  year INT,
  url TEXT NOT NULL,
  embedding vector(1536),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create HNSW index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_taiken_experiences_embedding 
ON taiken_experiences 
USING hnsw (embedding vector_cosine_ops);
