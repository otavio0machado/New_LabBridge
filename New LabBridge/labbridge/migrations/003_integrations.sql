-- Migration: 003_integrations.sql
-- Description: Adds integrations table and RLS policies.

CREATE TABLE IF NOT EXISTS public.integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    integration_key TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    icon TEXT,
    is_enabled BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'inactive', -- active, inactive, error, syncing
    last_sync_at TIMESTAMPTZ,
    last_error TEXT,
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (tenant_id, integration_key)
);

CREATE INDEX IF NOT EXISTS idx_integrations_tenant ON public.integrations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_integrations_status ON public.integrations(status);

ALTER TABLE public.integrations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "tenant_isolation_integrations" ON public.integrations;
CREATE POLICY "tenant_isolation_integrations" ON public.integrations
    FOR ALL USING (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
        OR auth.role() = 'service_role'
    );

-- Updated_at trigger
DROP TRIGGER IF EXISTS update_integrations_updated_at ON public.integrations;
CREATE TRIGGER update_integrations_updated_at
    BEFORE UPDATE ON public.integrations
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

