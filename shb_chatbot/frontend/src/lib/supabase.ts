import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://aehzparpmmjdzpxkuwic.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFlaHpwYXJwbW1qZHpweGt1d2ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg0MzcyNTAsImV4cCI6MjA5NDAxMzI1MH0.89q-QUjJRLsoQvJMS0wjZOUkt13c8wa_M_uavpwYp6E';

if (!supabaseUrl || !supabaseAnonKey) {
  if (typeof window !== 'undefined') {
    console.warn('Supabase URL or Anon Key is missing. Check your environment variables.');
  }
}

// Only create the client if we have the required variables to avoid top-level crash during SSR
// If they are missing, the client will be null, and we handle that in the hooks
export const supabase = (supabaseUrl && supabaseAnonKey) 
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null as any;
