-- Migration: 002_multi_tenant_schema.sql
-- Description: Creates schemas for multi-tenancy, plans, and subscriptions.

-- 1. Tenants Table (Laboratórios)
CREATE TABLE IF NOT EXISTS public.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    cnpj TEXT,
    email TEXT,
    phone TEXT,
    plan_type TEXT DEFAULT 'starter',
    subscription_status TEXT DEFAULT 'active',
    stripe_customer_id TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Users Table (Extension of Supabase Auth)
-- Note: Supabase handles auth in auth.users, but we need application specific data.
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    tenant_id UUID REFERENCES public.tenants(id),
    role TEXT DEFAULT 'member', -- owner, admin, member
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Plans Table
CREATE TABLE IF NOT EXISTS public.plans (
    id TEXT PRIMARY KEY, -- 'starter', 'pro', 'enterprise'
    name TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    currency TEXT DEFAULT 'BRL',
    features JSONB DEFAULT '[]',
    limits JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Subscriptions Table
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id),
    plan_id TEXT REFERENCES public.plans(id),
    status TEXT NOT NULL, -- active, past_due, canceled, trialing
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    stripe_subscription_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Add tenant_id to Saved Analyses (if not exists)
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'saved_analyses' AND column_name = 'tenant_id') THEN
        ALTER TABLE public.saved_analyses ADD COLUMN tenant_id UUID REFERENCES public.tenants(id);
    END IF;
END $$;

-- 6. Row Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_analyses ENABLE ROW LEVEL SECURITY;

-- Tenants: Users can view their own tenant
CREATE POLICY "Users can view own tenant" ON public.tenants
    FOR SELECT USING (
        id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
    );

-- Profiles: Users can view profiles in their tenant
CREATE POLICY "Users can view profiles in same tenant" ON public.profiles
    FOR SELECT USING (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
    );

-- Profiles: Users can update their own profile
CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (
        id = auth.uid()
    );

-- Saved Analyses: Users can only see analyses from their tenant
CREATE POLICY "Users can view tenant analyses" ON public.saved_analyses
    FOR ALL USING (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
    );

-- Initial Data Seeding (Plans)
INSERT INTO public.plans (id, name, price, features, limits) VALUES 
('starter', 'Starter', 0.00, '["Até 50 análises/mês", "1 Usuário", "Suporte por Email"]', '{"analyses_per_month": 50, "users": 1}'),
('pro', 'Pro', 299.00, '["Análises Ilimitadas", "5 Usuários", "Suporte Prioritário", "IA Detective Avançado"]', '{"analyses_per_month": -1, "users": 5}'),
('enterprise', 'Enterprise', 0.00, '["Usuários Ilimitados", "API Dedicada", "Gerente de Contas"]', '{"analyses_per_month": -1, "users": -1}')
ON CONFLICT (id) DO NOTHING;
