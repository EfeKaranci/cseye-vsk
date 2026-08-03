# CSEYE Phase 3 — Publish & Share (Supabase + Cloudflare Pages)

Publish a snapshot from the local app; colleagues open a link and view it with
**no ETABS, no bridge, no install**.

```
Local app ──Publish──► Supabase Storage: snapshots/<token>/{geometry.json, forces.json}
                       Supabase Postgres: share(token → model, results, expiry)
                                   │
              Share viewer (Cloudflare Pages) at  <pages-url>/share.html?s=<token>
              fetches the public JSON bundle and renders (same PlanRenderer).
```

## 1. Supabase project (one-time)

1. Create a **new** Supabase project.
2. **Storage → New bucket**: name `cseye`, **Public = ON**.
3. **SQL editor**: run [`supabase.sql`](./supabase.sql) (creates the `share` table).
4. **Project settings → API**: copy **Project URL**, **anon public** key, **service_role** key.

## 2. Point the bridge at Supabase

Set env vars before starting the bridge (or put them in a `.env` you load):

```
SUPABASE_URL=https://<ref>.supabase.co
SUPABASE_SERVICE_KEY=<service_role key>      # bridge only — never in the browser
SUPABASE_BUCKET=cseye
CSEYE_SHARE_URL=https://<your-pages-site>    # optional; fills in share_url
```

Restart the bridge. The header **Publish…** button lights up once a model is loaded.

## 3. Deploy the share viewer (Cloudflare Pages)

Build the viewer with the public Supabase URL baked in (anon-safe — public bucket,
no keys needed by the browser):

```
cd cseye-web/viewer
VITE_SUPABASE_URL=https://<ref>.supabase.co VITE_SUPABASE_BUCKET=cseye npm run build
```

Deploy `viewer/dist` to Cloudflare Pages (framework preset: **None**, build output: `dist`).
The share viewer is `dist/share.html`; a link looks like:

```
https://<your-pages-site>/share.html?s=<token>
```

Set `CSEYE_SHARE_URL=https://<your-pages-site>/share.html` on the bridge so
**Publish…** returns the full clickable link (copied to your clipboard).

## Revoking a share

Delete the objects under `snapshots/<token>/` in the `cseye` bucket (and optionally
the row in `share`). The link stops resolving.

## Notes

- The browser only ever reads the **public** bundle by token — the `service_role`
  key stays on your machine (bridge). anon key isn't needed by the share viewer.
- `forces.json` holds all *extracted* result sets. Extract the combos/cases you
  want to share (in the app) before pressing Publish.
