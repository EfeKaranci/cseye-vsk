-- CSEYE Phase 3 — Supabase setup (run in the SQL editor of a NEW project).
--
-- Data model: the local bridge publishes each snapshot as two JSON bundles
-- (geometry.json, forces.json) into a PUBLIC Storage bucket under a random
-- token:  snapshots/<token>/...  . The share viewer reads those directly by
-- token, so it never needs table access. This `share` table is only the
-- owner-side registry (for listing / labels / expiry / revocation), written by
-- the bridge with the service_role key.

create table if not exists public.share (
  token       uuid primary key default gen_random_uuid(),
  model       text,
  label       text,
  results     text[],
  created_at  timestamptz not null default now(),
  expires_at  timestamptz
);

alter table public.share enable row level security;
-- No anon/authenticated policies → the table is readable/writable only with the
-- service_role key (the local bridge). Revoke a share by deleting its Storage
-- objects (and optionally its row here).

-- Storage bucket (create in Dashboard → Storage, or via API):
--   name: cseye   |   public: true
-- Public buckets serve objects at:
--   {SUPABASE_URL}/storage/v1/object/public/cseye/snapshots/<token>/geometry.json
