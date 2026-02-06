-- Script de Configuração do Banco de Dados (Supabase)
-- Execute este script no SQL Editor do seu projeto Supabase para criar as tabelas necessárias.
-- IMPORTANTE: Todas as tabelas usam tenant_id para isolamento multi-tenant via RLS.

-- 1. Habilitar extensão UUID (geralmente já vem habilitada)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- HELPER: Função para extrair tenant_id do JWT (usada nas policies RLS)
-- ============================================================================
CREATE OR REPLACE FUNCTION public.get_current_tenant_id()
RETURNS text AS $$
BEGIN
    RETURN coalesce(
        current_setting('request.jwt.claims', true)::json->>'tenant_id',
        current_setting('request.jwt.claims', true)::json->'app_metadata'->>'tenant_id',
        ''
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

-- ============================================================================
-- 2. TABELAS DE AUDITORIA
-- ============================================================================

-- Tabela de Resumos de Auditoria (audit_summaries)
CREATE TABLE IF NOT EXISTS public.audit_summaries (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    tenant_id text NOT NULL DEFAULT '',
    compulab_total double precision,
    simus_total double precision,
    missing_exams_count integer,
    divergences_count integer,
    missing_patients_count integer,
    ai_summary text
);

-- Índice para tenant_id
CREATE INDEX IF NOT EXISTS idx_audit_summaries_tenant ON public.audit_summaries(tenant_id);

-- RLS: Isolamento por tenant_id
ALTER TABLE public.audit_summaries ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso público audit_summaries" ON public.audit_summaries;
DROP POLICY IF EXISTS "tenant_isolation_audit_summaries" ON public.audit_summaries;
CREATE POLICY "tenant_isolation_audit_summaries" ON public.audit_summaries
    FOR ALL USING (tenant_id = public.get_current_tenant_id());
-- Permitir service_role acessar tudo (backend)
DROP POLICY IF EXISTS "service_role_audit_summaries" ON public.audit_summaries;
CREATE POLICY "service_role_audit_summaries" ON public.audit_summaries
    FOR ALL USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');


-- Tabela de Histórico de Pacientes / Resoluções (patient_history)
CREATE TABLE IF NOT EXISTS public.patient_history (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    tenant_id text NOT NULL DEFAULT '',
    patient_name text NOT NULL,
    exam_name text NOT NULL,
    status text,
    last_value double precision,
    notes text,
    CONSTRAINT unique_patient_exam_tenant UNIQUE(patient_name, exam_name, tenant_id)
);

CREATE INDEX IF NOT EXISTS idx_patient_history_tenant ON public.patient_history(tenant_id);
CREATE INDEX IF NOT EXISTS idx_patient_history_patient ON public.patient_history(patient_name, tenant_id);

-- RLS: Isolamento por tenant_id
ALTER TABLE public.patient_history ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso público patient_history" ON public.patient_history;
DROP POLICY IF EXISTS "tenant_isolation_patient_history" ON public.patient_history;
CREATE POLICY "tenant_isolation_patient_history" ON public.patient_history
    FOR ALL USING (tenant_id = public.get_current_tenant_id());
DROP POLICY IF EXISTS "service_role_patient_history" ON public.patient_history;
CREATE POLICY "service_role_patient_history" ON public.patient_history
    FOR ALL USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');

-- ============================================================================
-- 3. TABELA DE ANÁLISES SALVAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.saved_analyses (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    tenant_id text NOT NULL DEFAULT '',

    -- Identificação (escolhida pelo usuário)
    analysis_name text NOT NULL,
    analysis_date date NOT NULL,
    description text,

    -- Arquivos Originais
    compulab_file_url text,
    compulab_file_name text,
    simus_file_url text,
    simus_file_name text,

    -- Arquivos Convertidos
    converted_compulab_url text,
    converted_simus_url text,

    -- Relatório PDF
    analysis_report_url text,

    -- Resumo da Análise
    compulab_total double precision DEFAULT 0,
    simus_total double precision DEFAULT 0,
    difference double precision DEFAULT 0,
    missing_patients_count integer DEFAULT 0,
    missing_patients_total double precision DEFAULT 0,
    missing_exams_count integer DEFAULT 0,
    missing_exams_total double precision DEFAULT 0,
    divergences_count integer DEFAULT 0,
    divergences_total double precision DEFAULT 0,
    extra_simus_count integer DEFAULT 0,

    -- Metadados
    ai_summary text,
    tags text[],
    status text DEFAULT 'completed',

    -- Constraint (inclui tenant_id para multi-tenant)
    CONSTRAINT unique_analysis_name_date_tenant UNIQUE(analysis_name, analysis_date, tenant_id)
);

-- Tabela de Detalhes da Análise
CREATE TABLE IF NOT EXISTS public.analysis_items (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id uuid NOT NULL REFERENCES public.saved_analyses(id) ON DELETE CASCADE,
    created_at timestamptz DEFAULT now(),
    item_type text NOT NULL,
    patient_name text,
    exam_name text,
    compulab_value double precision,
    simus_value double precision,
    difference double precision,
    exams_count integer,
    is_resolved boolean DEFAULT false,
    resolution_notes text
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_saved_analyses_tenant ON public.saved_analyses(tenant_id);
CREATE INDEX IF NOT EXISTS idx_saved_analyses_date ON public.saved_analyses(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_saved_analyses_name ON public.saved_analyses(analysis_name);
CREATE INDEX IF NOT EXISTS idx_analysis_items_analysis_id ON public.analysis_items(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_items_type ON public.analysis_items(item_type);

-- RLS: saved_analyses isoladas por tenant
ALTER TABLE public.saved_analyses ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso público saved_analyses" ON public.saved_analyses;
DROP POLICY IF EXISTS "tenant_isolation_saved_analyses" ON public.saved_analyses;
CREATE POLICY "tenant_isolation_saved_analyses" ON public.saved_analyses
    FOR ALL USING (tenant_id = public.get_current_tenant_id());
DROP POLICY IF EXISTS "service_role_saved_analyses" ON public.saved_analyses;
CREATE POLICY "service_role_saved_analyses" ON public.saved_analyses
    FOR ALL USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');

-- RLS: analysis_items herdam isolamento via foreign key + join
ALTER TABLE public.analysis_items ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso público analysis_items" ON public.analysis_items;
DROP POLICY IF EXISTS "tenant_isolation_analysis_items" ON public.analysis_items;
CREATE POLICY "tenant_isolation_analysis_items" ON public.analysis_items
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.saved_analyses sa
            WHERE sa.id = analysis_items.analysis_id
            AND sa.tenant_id = public.get_current_tenant_id()
        )
    );
DROP POLICY IF EXISTS "service_role_analysis_items" ON public.analysis_items;
CREATE POLICY "service_role_analysis_items" ON public.analysis_items
    FOR ALL USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');

-- Trigger para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_saved_analyses_updated_at ON public.saved_analyses;
CREATE TRIGGER update_saved_analyses_updated_at
    BEFORE UPDATE ON public.saved_analyses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 4. TABELA DE INTEGRAÇÕES
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.integrations (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    tenant_id text NOT NULL DEFAULT '',

    name text NOT NULL,
    type text NOT NULL,  -- 'compulab', 'simus', 'erp', 'api', etc
    description text,

    -- Status
    status text DEFAULT 'inactive',  -- 'active', 'inactive', 'error', 'pending'
    is_connected boolean DEFAULT false,
    last_sync_at timestamptz,
    last_sync_status text,

    -- Configuração (armazenar de forma segura)
    config jsonb DEFAULT '{}',

    -- Estatísticas
    sync_count integer DEFAULT 0,
    records_synced integer DEFAULT 0,
    error_count integer DEFAULT 0,
    last_error text
);

CREATE INDEX IF NOT EXISTS idx_integrations_tenant ON public.integrations(tenant_id);

-- RLS: Isolamento por tenant
ALTER TABLE public.integrations ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso público integrations" ON public.integrations;
DROP POLICY IF EXISTS "tenant_isolation_integrations" ON public.integrations;
CREATE POLICY "tenant_isolation_integrations" ON public.integrations
    FOR ALL USING (tenant_id = public.get_current_tenant_id());
DROP POLICY IF EXISTS "service_role_integrations" ON public.integrations;
CREATE POLICY "service_role_integrations" ON public.integrations
    FOR ALL USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');

-- Tabela de Logs de Integração
CREATE TABLE IF NOT EXISTS public.integration_logs (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    integration_id uuid REFERENCES public.integrations(id) ON DELETE CASCADE,
    
    action text NOT NULL,  -- 'sync', 'connect', 'disconnect', 'error'
    status text NOT NULL,  -- 'success', 'error', 'warning'
    message text,
    details jsonb,
    records_affected integer DEFAULT 0
);

-- RLS: integration_logs herdam isolamento via foreign key
ALTER TABLE public.integration_logs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso público integration_logs" ON public.integration_logs;
DROP POLICY IF EXISTS "tenant_isolation_integration_logs" ON public.integration_logs;
CREATE POLICY "tenant_isolation_integration_logs" ON public.integration_logs
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.integrations i
            WHERE i.id = integration_logs.integration_id
            AND i.tenant_id = public.get_current_tenant_id()
        )
    );
DROP POLICY IF EXISTS "service_role_integration_logs" ON public.integration_logs;
CREATE POLICY "service_role_integration_logs" ON public.integration_logs
    FOR ALL USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');

-- Índices
CREATE INDEX IF NOT EXISTS idx_integration_logs_integration ON public.integration_logs(integration_id);
CREATE INDEX IF NOT EXISTS idx_integration_logs_created ON public.integration_logs(created_at DESC);

-- ============================================================================
-- 5. TABELA DE LOGS DE AUDITORIA (DATA_AUDITS)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.data_audits (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    tenant_id text NOT NULL DEFAULT '',
    record_id text NOT NULL,
    table_name text NOT NULL,
    old_value text,
    new_value text,
    action text,
    user_id uuid,
    consistency_result jsonb
);

CREATE INDEX IF NOT EXISTS idx_data_audits_tenant ON public.data_audits(tenant_id);

-- RLS: Isolamento por tenant
ALTER TABLE public.data_audits ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso público data_audits" ON public.data_audits;
DROP POLICY IF EXISTS "tenant_isolation_data_audits" ON public.data_audits;
CREATE POLICY "tenant_isolation_data_audits" ON public.data_audits
    FOR ALL USING (tenant_id = public.get_current_tenant_id());
DROP POLICY IF EXISTS "service_role_data_audits" ON public.data_audits;
CREATE POLICY "service_role_data_audits" ON public.data_audits
    FOR ALL USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');

-- ============================================================================
-- 6. TABELA DE MEMBROS DA EQUIPE (TEAM_MEMBERS)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.team_members (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    tenant_id text NOT NULL DEFAULT '',

    name text NOT NULL,
    email text NOT NULL,
    role text DEFAULT 'analyst',  -- 'admin', 'manager', 'analyst', 'viewer'
    department text,
    avatar_url text,
    status text DEFAULT 'active',  -- 'active', 'inactive', 'pending'
    last_active_at timestamptz,

    -- Permissões
    can_export boolean DEFAULT true,
    can_resolve boolean DEFAULT true,
    can_manage_team boolean DEFAULT false,

    -- Unique por tenant (não global)
    CONSTRAINT unique_email_per_tenant UNIQUE(email, tenant_id)
);

CREATE INDEX IF NOT EXISTS idx_team_members_tenant ON public.team_members(tenant_id);

-- RLS: Isolamento por tenant
ALTER TABLE public.team_members ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir acesso público team_members" ON public.team_members;
DROP POLICY IF EXISTS "tenant_isolation_team_members" ON public.team_members;
CREATE POLICY "tenant_isolation_team_members" ON public.team_members
    FOR ALL USING (tenant_id = public.get_current_tenant_id());
DROP POLICY IF EXISTS "service_role_team_members" ON public.team_members;
CREATE POLICY "service_role_team_members" ON public.team_members
    FOR ALL USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');

-- ============================================================================
-- 7. TABELA DE RESOLUÇÕES DE DIVERGÊNCIAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.divergence_resolutions (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    tenant_id text NOT NULL DEFAULT '',
    analysis_id uuid REFERENCES public.saved_analyses(id) ON DELETE CASCADE,

    patient_name text NOT NULL,
    exam_name text NOT NULL DEFAULT '',
    resolution_status text NOT NULL DEFAULT '',  -- 'resolvido', ''
    annotation text DEFAULT '',  -- error type classification
    notes text DEFAULT '',

    CONSTRAINT unique_resolution_per_analysis UNIQUE(analysis_id, patient_name, exam_name)
);

CREATE INDEX IF NOT EXISTS idx_resolutions_tenant ON public.divergence_resolutions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_resolutions_analysis ON public.divergence_resolutions(analysis_id);

ALTER TABLE public.divergence_resolutions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "tenant_isolation_resolutions" ON public.divergence_resolutions;
CREATE POLICY "tenant_isolation_resolutions" ON public.divergence_resolutions
    FOR ALL USING (tenant_id = public.get_current_tenant_id());
DROP POLICY IF EXISTS "service_role_resolutions" ON public.divergence_resolutions;
CREATE POLICY "service_role_resolutions" ON public.divergence_resolutions
    FOR ALL USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');

-- ============================================================================
-- FIM DO SCRIPT
-- ============================================================================

