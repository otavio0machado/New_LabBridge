-- Script de Configuração do Banco de Dados (Supabase)
-- Execute este script no SQL Editor do seu projeto Supabase para criar as tabelas necessárias.

-- 1. Habilitar extensão UUID (geralmente já vem habilitada)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 2. TABELAS DE AUDITORIA
-- ============================================================================

-- Tabela de Resumos de Auditoria (audit_summaries)
CREATE TABLE IF NOT EXISTS public.audit_summaries (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    compulab_total double precision,
    simus_total double precision,
    missing_exams_count integer,
    divergences_count integer,
    missing_patients_count integer,
    ai_summary text
);

-- Políticas de Segurança (RLS) para audit_summaries
ALTER TABLE public.audit_summaries ENABLE ROW LEVEL SECURITY;

-- Remover política existente se houver para evitar erro de duplicação ao rodar novamente
DROP POLICY IF EXISTS "Permitir acesso público audit_summaries" ON public.audit_summaries;
CREATE POLICY "Permitir acesso público audit_summaries" ON public.audit_summaries FOR ALL USING (true);


-- Tabela de Histórico de Pacientes / Resoluções (patient_history)
CREATE TABLE IF NOT EXISTS public.patient_history (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    patient_name text NOT NULL,
    exam_name text NOT NULL,
    status text,
    last_value double precision,
    notes text,
    CONSTRAINT unique_patient_exam UNIQUE(patient_name, exam_name)
);

-- Políticas de Segurança (RLS) para patient_history
ALTER TABLE public.patient_history ENABLE ROW LEVEL SECURITY;

-- Remover política existente se houver
DROP POLICY IF EXISTS "Permitir acesso público patient_history" ON public.patient_history;
CREATE POLICY "Permitir acesso público patient_history" ON public.patient_history FOR ALL USING (true);

-- ============================================================================
-- 3. TABELA DE ANÁLISES SALVAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.saved_analyses (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    
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
    
    -- Constraint
    CONSTRAINT unique_analysis_name_date UNIQUE(analysis_name, analysis_date)
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
CREATE INDEX IF NOT EXISTS idx_saved_analyses_date ON public.saved_analyses(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_saved_analyses_name ON public.saved_analyses(analysis_name);
CREATE INDEX IF NOT EXISTS idx_analysis_items_analysis_id ON public.analysis_items(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_items_type ON public.analysis_items(item_type);

-- RLS
ALTER TABLE public.saved_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_items ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Permitir acesso público saved_analyses" ON public.saved_analyses;
CREATE POLICY "Permitir acesso público saved_analyses" ON public.saved_analyses FOR ALL USING (true);

DROP POLICY IF EXISTS "Permitir acesso público analysis_items" ON public.analysis_items;
CREATE POLICY "Permitir acesso público analysis_items" ON public.analysis_items FOR ALL USING (true);

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

-- RLS para integrations
ALTER TABLE public.integrations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Permitir acesso público integrations" ON public.integrations;
CREATE POLICY "Permitir acesso público integrations" ON public.integrations FOR ALL USING (true);

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

-- RLS para integration_logs
ALTER TABLE public.integration_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Permitir acesso público integration_logs" ON public.integration_logs;
CREATE POLICY "Permitir acesso público integration_logs" ON public.integration_logs FOR ALL USING (true);

-- Índices
CREATE INDEX IF NOT EXISTS idx_integration_logs_integration ON public.integration_logs(integration_id);
CREATE INDEX IF NOT EXISTS idx_integration_logs_created ON public.integration_logs(created_at DESC);

-- ============================================================================
-- 5. TABELA DE LOGS DE AUDITORIA (DATA_AUDITS)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.data_audits (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    record_id text NOT NULL,
    table_name text NOT NULL,
    old_value text,
    new_value text,
    action text,
    user_id uuid,
    consistency_result jsonb
);

-- RLS
ALTER TABLE public.data_audits ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Permitir acesso público data_audits" ON public.data_audits;
CREATE POLICY "Permitir acesso público data_audits" ON public.data_audits FOR ALL USING (true);

-- ============================================================================
-- 6. TABELA DE MEMBROS DA EQUIPE (TEAM_MEMBERS)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.team_members (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    
    name text NOT NULL,
    email text UNIQUE NOT NULL,
    role text DEFAULT 'analyst',  -- 'admin', 'manager', 'analyst', 'viewer'
    department text,
    avatar_url text,
    status text DEFAULT 'active',  -- 'active', 'inactive', 'pending'
    last_active_at timestamptz,
    
    -- Permissões
    can_export boolean DEFAULT true,
    can_resolve boolean DEFAULT true,
    can_manage_team boolean DEFAULT false
);

-- RLS
ALTER TABLE public.team_members ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Permitir acesso público team_members" ON public.team_members;
CREATE POLICY "Permitir acesso público team_members" ON public.team_members FOR ALL USING (true);

-- ============================================================================
-- FIM DO SCRIPT
-- ============================================================================

