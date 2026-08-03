/// <reference types="vite/client" />
interface ImportMetaEnv {
  readonly VITE_BRIDGE?: string;
  readonly VITE_SUPABASE_URL?: string;
  readonly VITE_SUPABASE_BUCKET?: string;
}
interface ImportMeta { readonly env: ImportMetaEnv; }
