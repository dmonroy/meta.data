CREATE TABLE meta(
  id SERIAL PRIMARY KEY,
  data JSONB,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX meta_data_source_idx ON meta ((data->>'source'));
CREATE INDEX meta_data_tags_idx ON meta ((data->>'tags'));
CREATE INDEX meta_created_idx ON meta (created);