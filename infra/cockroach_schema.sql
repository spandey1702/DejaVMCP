-- CockroachDB schema for the Agentic Fleet Decision Ledger
-- Run this against your CockroachDB database after connecting with the SQL shell.

CREATE DATABASE IF NOT EXISTS agentic_fleet;
USE agentic_fleet;

CREATE TABLE IF NOT EXISTS agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_key STRING NOT NULL UNIQUE,
    name STRING NOT NULL,
    role STRING,
    status STRING NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp()
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_key STRING NOT NULL UNIQUE,
    title STRING NOT NULL,
    description STRING,
    status STRING NOT NULL DEFAULT 'open',
    created_by_agent_id UUID REFERENCES agents(agent_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp()
);

CREATE TABLE IF NOT EXISTS task_claims (
    claim_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    status STRING NOT NULL DEFAULT 'active',
    claimed_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp(),
    released_at TIMESTAMPTZ,
    note STRING
);

CREATE TABLE IF NOT EXISTS task_decisions (
    decision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    decision_text STRING NOT NULL,
    reason STRING,
    state STRING NOT NULL DEFAULT 'proposed',
    decision_rank INT NOT NULL DEFAULT 0,
    embedding VECTOR(1024),
    created_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp()
);

CREATE UNIQUE INDEX IF NOT EXISTS task_claims_one_active_idx
    ON task_claims(task_id)
    WHERE status = 'active';

CREATE INDEX IF NOT EXISTS task_claims_agent_idx ON task_claims(agent_id);
CREATE INDEX IF NOT EXISTS task_claims_task_idx ON task_claims(task_id);

CREATE TABLE IF NOT EXISTS task_decisions (
    decision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    decision_text STRING NOT NULL,
    reason STRING,
    state STRING NOT NULL DEFAULT 'proposed',
    decision_rank INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp()
);

CREATE INDEX IF NOT EXISTS task_decisions_task_idx ON task_decisions(task_id);
CREATE INDEX IF NOT EXISTS task_decisions_agent_idx ON task_decisions(agent_id);
CREATE INDEX IF NOT EXISTS task_decisions_created_at_idx ON task_decisions(created_at DESC);

CREATE TABLE IF NOT EXISTS task_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(agent_id) ON DELETE SET NULL,
    event_type STRING NOT NULL,
    event_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp()
);


CREATE VECTOR INDEX IF NOT EXISTS task_decisions_embedding_idx
    ON task_decisions (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS task_events_task_idx ON task_events(task_id);
CREATE INDEX IF NOT EXISTS task_events_created_at_idx ON task_events(created_at DESC);

-- Optional seed data for local testing.
-- INSERT INTO agents(agent_key, name, role) VALUES
--     ('agent-alpha', 'Agent Alpha', 'planner'),
--     ('agent-beta', 'Agent Beta', 'executor');
