-- ============================================================================
-- MIGRATION: 005_team_management.sql
-- Description: Creates team_members and team_invites tables for team management
-- Date: 2026-02-05
-- ============================================================================

-- Enable uuid extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. TEAM MEMBERS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    name TEXT,
    role TEXT NOT NULL DEFAULT 'viewer',
    -- Roles: admin_global, admin_lab, analyst, viewer
    status TEXT NOT NULL DEFAULT 'pending',
    -- Statuses: pending, active, inactive
    last_active TIMESTAMPTZ,
    invited_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure unique email per tenant
    CONSTRAINT unique_email_per_tenant UNIQUE(tenant_id, email)
);

-- ============================================================================
-- 2. TEAM INVITES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.team_invites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer',
    token TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending',
    -- Statuses: pending, accepted, rejected, expired
    message TEXT,
    invited_by TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 3. INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_team_members_tenant ON public.team_members(tenant_id);
CREATE INDEX IF NOT EXISTS idx_team_members_email ON public.team_members(email);
CREATE INDEX IF NOT EXISTS idx_team_members_status ON public.team_members(status);
CREATE INDEX IF NOT EXISTS idx_team_invites_tenant ON public.team_invites(tenant_id);
CREATE INDEX IF NOT EXISTS idx_team_invites_token ON public.team_invites(token);
CREATE INDEX IF NOT EXISTS idx_team_invites_status ON public.team_invites(status);
CREATE INDEX IF NOT EXISTS idx_team_invites_email ON public.team_invites(email);

-- ============================================================================
-- 4. ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on both tables
ALTER TABLE public.team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.team_invites ENABLE ROW LEVEL SECURITY;

-- Team Members Policies
DROP POLICY IF EXISTS "Users can view team members in same tenant" ON public.team_members;
CREATE POLICY "Users can view team members in same tenant" ON public.team_members
    FOR SELECT USING (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
    );

DROP POLICY IF EXISTS "Users can insert team members in own tenant" ON public.team_members;
CREATE POLICY "Users can insert team members in own tenant" ON public.team_members
    FOR INSERT WITH CHECK (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
    );

DROP POLICY IF EXISTS "Users can update team members in same tenant" ON public.team_members;
CREATE POLICY "Users can update team members in same tenant" ON public.team_members
    FOR UPDATE USING (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
    );

DROP POLICY IF EXISTS "Users can delete team members in same tenant" ON public.team_members;
CREATE POLICY "Users can delete team members in same tenant" ON public.team_members
    FOR DELETE USING (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
    );

DROP POLICY IF EXISTS "Service role full access team_members" ON public.team_members;
CREATE POLICY "Service role full access team_members" ON public.team_members
    FOR ALL USING (auth.role() = 'service_role');

-- Team Invites Policies
DROP POLICY IF EXISTS "Users can view invites in same tenant" ON public.team_invites;
CREATE POLICY "Users can view invites in same tenant" ON public.team_invites
    FOR SELECT USING (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
    );

DROP POLICY IF EXISTS "Users can insert invites in own tenant" ON public.team_invites;
CREATE POLICY "Users can insert invites in own tenant" ON public.team_invites
    FOR INSERT WITH CHECK (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
    );

DROP POLICY IF EXISTS "Users can update invites in same tenant" ON public.team_invites;
CREATE POLICY "Users can update invites in same tenant" ON public.team_invites
    FOR UPDATE USING (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
    );

DROP POLICY IF EXISTS "Service role full access team_invites" ON public.team_invites;
CREATE POLICY "Service role full access team_invites" ON public.team_invites
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================================================
-- 5. TRIGGERS
-- ============================================================================

-- Trigger to update updated_at on team_members
DROP TRIGGER IF EXISTS update_team_members_updated_at ON public.team_members;
CREATE TRIGGER update_team_members_updated_at
    BEFORE UPDATE ON public.team_members
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- Trigger to update updated_at on team_invites
DROP TRIGGER IF EXISTS update_team_invites_updated_at ON public.team_invites;
CREATE TRIGGER update_team_invites_updated_at
    BEFORE UPDATE ON public.team_invites
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================

-- Verify tables were created:
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public' AND table_name IN ('team_members', 'team_invites');
