-- ============================================================================
-- LABBRIDGE - SCHEMA COMPLETO FASE 1
-- Execute este script no SQL Editor do Supabase
-- Data: 2026-02-03
-- ============================================================================

-- Habilitar extensoes necessarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. TABELAS DE MULTI-TENANCY
-- ============================================================================

-- Tenants (Laboratorios)
CREATE TABLE IF NOT EXISTS public.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    cnpj TEXT,
    email TEXT,
    phone TEXT,
    plan_type TEXT DEFAULT 'starter',
    subscription_status TEXT DEFAULT 'active',
    stripe_customer_id TEXT,
    settings JSONB DEFAULT '{"analysis_threshold": 0.05, "auto_detect_typos": true, "theme": "light"}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Profiles (vincula auth.users com tenants)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member', -- owner, admin, member
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Plans (Planos de assinatura)
CREATE TABLE IF NOT EXISTS public.plans (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    currency TEXT DEFAULT 'BRL',
    features JSONB DEFAULT '[]',
    limits JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subscriptions
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    plan_id TEXT REFERENCES public.plans(id),
    status TEXT NOT NULL DEFAULT 'active',
    current_period_start TIMESTAMPTZ DEFAULT NOW(),
    current_period_end TIMESTAMPTZ DEFAULT NOW() + INTERVAL '1 month',
    stripe_subscription_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 2. TABELAS DE ANALISES
-- ============================================================================

-- Saved Analyses (Analises salvas)
CREATE TABLE IF NOT EXISTS public.saved_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    analysis_name TEXT NOT NULL,
    analysis_date DATE NOT NULL,
    description TEXT,

    -- URLs de arquivos
    compulab_file_url TEXT,
    compulab_file_name TEXT,
    simus_file_url TEXT,
    simus_file_name TEXT,
    converted_compulab_url TEXT,
    converted_simus_url TEXT,
    analysis_report_url TEXT,

    -- Totais
    compulab_total DECIMAL(12,2) DEFAULT 0,
    simus_total DECIMAL(12,2) DEFAULT 0,
    difference DECIMAL(12,2) DEFAULT 0,

    -- Contadores
    missing_patients_count INT DEFAULT 0,
    missing_patients_total DECIMAL(12,2) DEFAULT 0,
    missing_exams_count INT DEFAULT 0,
    missing_exams_total DECIMAL(12,2) DEFAULT 0,
    divergences_count INT DEFAULT 0,
    divergences_total DECIMAL(12,2) DEFAULT 0,
    extra_simus_count INT DEFAULT 0,

    -- Metadata
    ai_summary TEXT,
    tags TEXT[],
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analysis Items (Itens detalhados de cada analise)
CREATE TABLE IF NOT EXISTS public.analysis_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES public.saved_analyses(id) ON DELETE CASCADE,
    item_type TEXT NOT NULL, -- 'missing_patient', 'missing_exam', 'divergence', 'extra_simus'
    patient_name TEXT,
    exam_name TEXT,
    compulab_value DECIMAL(12,2),
    simus_value DECIMAL(12,2),
    difference DECIMAL(12,2),
    exams_count INT,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 3. TABELAS DE AUDITORIA
-- ============================================================================

-- Audit Summaries (resumos de auditoria legado)
CREATE TABLE IF NOT EXISTS public.audit_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    compulab_total DOUBLE PRECISION,
    simus_total DOUBLE PRECISION,
    missing_exams_count INTEGER,
    divergences_count INTEGER,
    missing_patients_count INTEGER,
    ai_summary TEXT
);

-- Patient History (historico de resolucoes)
CREATE TABLE IF NOT EXISTS public.patient_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    patient_name TEXT NOT NULL,
    exam_name TEXT NOT NULL,
    status TEXT,
    last_value DOUBLE PRECISION,
    notes TEXT,
    CONSTRAINT unique_patient_exam_tenant UNIQUE(patient_name, exam_name, tenant_id)
);

-- ============================================================================
-- 4. INDICES PARA PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_profiles_tenant ON public.profiles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_profiles_user ON public.profiles(id);
CREATE INDEX IF NOT EXISTS idx_saved_analyses_tenant ON public.saved_analyses(tenant_id);
CREATE INDEX IF NOT EXISTS idx_saved_analyses_date ON public.saved_analyses(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_saved_analyses_status ON public.saved_analyses(status);
CREATE INDEX IF NOT EXISTS idx_analysis_items_analysis ON public.analysis_items(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_items_type ON public.analysis_items(item_type);
CREATE INDEX IF NOT EXISTS idx_audit_summaries_tenant ON public.audit_summaries(tenant_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_tenant ON public.patient_history(tenant_id);

-- ============================================================================
-- 5. ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Habilitar RLS em todas as tabelas
ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patient_history ENABLE ROW LEVEL SECURITY;

-- Politicas para TENANTS
DROP POLICY IF EXISTS "Users can view own tenant" ON public.tenants;
CREATE POLICY "Users can view own tenant" ON public.tenants
    FOR SELECT USING (
        id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
    );

DROP POLICY IF EXISTS "Service role full access tenants" ON public.tenants;
CREATE POLICY "Service role full access tenants" ON public.tenants
    FOR ALL USING (auth.role() = 'service_role');

-- Politicas para PROFILES
DROP POLICY IF EXISTS "Users can view profiles in same tenant" ON public.profiles;
CREATE POLICY "Users can view profiles in same tenant" ON public.profiles
    FOR SELECT USING (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
    );

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (id = auth.uid());

DROP POLICY IF EXISTS "Service role full access profiles" ON public.profiles;
CREATE POLICY "Service role full access profiles" ON public.profiles
    FOR ALL USING (auth.role() = 'service_role');

-- Politicas para SAVED_ANALYSES
DROP POLICY IF EXISTS "tenant_isolation_saved_analyses" ON public.saved_analyses;
CREATE POLICY "tenant_isolation_saved_analyses" ON public.saved_analyses
    FOR ALL USING (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
        OR auth.role() = 'service_role'
    );

-- Politicas para ANALYSIS_ITEMS
DROP POLICY IF EXISTS "tenant_isolation_analysis_items" ON public.analysis_items;
CREATE POLICY "tenant_isolation_analysis_items" ON public.analysis_items
    FOR ALL USING (
        analysis_id IN (
            SELECT id FROM public.saved_analyses WHERE tenant_id IN (
                SELECT tenant_id FROM public.profiles WHERE id = auth.uid()
            )
        )
        OR auth.role() = 'service_role'
    );

-- Politicas para AUDIT_SUMMARIES
DROP POLICY IF EXISTS "tenant_isolation_audit_summaries" ON public.audit_summaries;
CREATE POLICY "tenant_isolation_audit_summaries" ON public.audit_summaries
    FOR ALL USING (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
        OR auth.role() = 'service_role'
    );

-- Politicas para PATIENT_HISTORY
DROP POLICY IF EXISTS "tenant_isolation_patient_history" ON public.patient_history;
CREATE POLICY "tenant_isolation_patient_history" ON public.patient_history
    FOR ALL USING (
        tenant_id IN (SELECT tenant_id FROM public.profiles WHERE id = auth.uid())
        OR auth.role() = 'service_role'
    );

-- ============================================================================
-- 6. TRIGGERS PARA AUTOMACAO
-- ============================================================================

-- Trigger para criar profile automaticamente apos signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    v_tenant_id UUID;
BEGIN
    -- Verificar se tenant_id foi passado nos metadados
    v_tenant_id := (NEW.raw_user_meta_data->>'tenant_id')::UUID;

    -- Se nao houver tenant_id, criar um novo tenant
    IF v_tenant_id IS NULL THEN
        INSERT INTO public.tenants (name, email)
        VALUES (
            COALESCE(NEW.raw_user_meta_data->>'lab_name', 'Meu Laboratorio'),
            NEW.email
        )
        RETURNING id INTO v_tenant_id;
    END IF;

    -- Criar profile
    INSERT INTO public.profiles (id, email, full_name, tenant_id, role)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
        v_tenant_id,
        COALESCE(NEW.raw_user_meta_data->>'role', 'owner')
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Ativar trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger de updated_at
DROP TRIGGER IF EXISTS update_tenants_updated_at ON public.tenants;
CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON public.tenants
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS update_profiles_updated_at ON public.profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS update_saved_analyses_updated_at ON public.saved_analyses;
CREATE TRIGGER update_saved_analyses_updated_at
    BEFORE UPDATE ON public.saved_analyses
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- ============================================================================
-- 7. DADOS INICIAIS (SEED)
-- ============================================================================

-- Inserir planos padrao
INSERT INTO public.plans (id, name, price, features, limits) VALUES
    ('starter', 'Starter', 0.00, '["Ate 50 analises/mes", "1 Usuario", "Suporte por Email"]', '{"analyses_per_month": 50, "users": 1}'),
    ('pro', 'Pro', 299.00, '["Analises Ilimitadas", "5 Usuarios", "Suporte Prioritario", "IA Detective Avancado"]', '{"analyses_per_month": -1, "users": 5}'),
    ('enterprise', 'Enterprise', 0.00, '["Usuarios Ilimitados", "API Dedicada", "Gerente de Contas"]', '{"analyses_per_month": -1, "users": -1}')
ON CONFLICT (id) DO UPDATE SET
    features = EXCLUDED.features,
    limits = EXCLUDED.limits;

-- ============================================================================
-- FIM DO SCRIPT
-- ============================================================================

-- Para verificar se tudo foi criado:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
