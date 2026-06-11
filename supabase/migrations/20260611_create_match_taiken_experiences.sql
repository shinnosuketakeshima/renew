-- Create match_taiken_experiences RPC function for vector similarity search
CREATE OR REPLACE FUNCTION match_taiken_experiences(
  query_embedding vector(1536),
  match_count int DEFAULT 5,
  match_threshold float DEFAULT 0.6
)
RETURNS TABLE(
  taiken_number int,
  title text,
  body text,
  country text,
  age int,
  year int,
  url text,
  similarity float
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    te.taiken_number,
    te.title,
    te.body,
    te.country,
    te.age,
    te.year,
    te.url,
    1 - (te.embedding <=> query_embedding) AS similarity
  FROM taiken_experiences te
  WHERE 1 - (te.embedding <=> query_embedding) > match_threshold
  ORDER BY te.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
