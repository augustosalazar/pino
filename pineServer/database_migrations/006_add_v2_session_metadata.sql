ALTER TABLE pine_exercise_sessions
ADD COLUMN IF NOT EXISTS v2_metadata JSONB;
