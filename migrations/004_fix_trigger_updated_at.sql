-- Migration 004: Corrigir trigger de updated_at
-- Remove trigger problemático que usa campo "atualizado_em" ao invés de "updated_at"

BEGIN;

-- =============================================
-- REMOVER TRIGGERS PROBLEMÁTICOS
-- =============================================

-- Verificar e remover triggers existentes que usam "atualizado_em"
DO $$
DECLARE
    r RECORD;
BEGIN
    -- Buscar todos os triggers que usam a função update_updated_at_column
    FOR r IN
        SELECT DISTINCT trigger_name, event_object_table
        FROM information_schema.triggers
        WHERE trigger_schema = 'public'
        AND action_statement LIKE '%update_updated_at_column%'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS %I ON %I CASCADE', r.trigger_name, r.event_object_table);
        RAISE NOTICE 'Trigger % removido da tabela %', r.trigger_name, r.event_object_table;
    END LOOP;
END $$;

-- Remover a função problemática
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- =============================================
-- CRIAR FUNÇÃO CORRETA (usando updated_at em inglês)
-- =============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    -- Verifica se a coluna "updated_at" existe na tabela
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = TG_TABLE_SCHEMA
        AND table_name = TG_TABLE_NAME
        AND column_name = 'updated_at'
    ) THEN
        NEW.updated_at = NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column() IS
    'Atualiza automaticamente o campo updated_at antes de UPDATE';

-- =============================================
-- APLICAR TRIGGER NAS TABELAS RELEVANTES
-- =============================================

-- Tabelas que têm campo updated_at e precisam de auto-update
DO $$
DECLARE
    table_name TEXT;
    tables_with_updated_at TEXT[] := ARRAY[
        'users',
        'lawyers',
        'subscriptions',
        'referrals',
        'cost_table',
        'processos',
        'prazos',
        'avaliacoes',
        'agendamentos',
        'parceiros',
        'blog_posts'
    ];
BEGIN
    FOREACH table_name IN ARRAY tables_with_updated_at
    LOOP
        -- Verificar se a tabela existe e tem campo updated_at
        IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = table_name
            AND column_name = 'updated_at'
        ) THEN
            -- Remover trigger antigo se existir
            EXECUTE format('DROP TRIGGER IF EXISTS trigger_update_updated_at ON %I', table_name);

            -- Criar novo trigger
            EXECUTE format(
                'CREATE TRIGGER trigger_update_updated_at
                BEFORE UPDATE ON %I
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()',
                table_name
            );

            RAISE NOTICE 'Trigger criado para tabela: %', table_name;
        ELSE
            RAISE NOTICE 'Tabela % não encontrada ou sem campo updated_at', table_name;
        END IF;
    END LOOP;
END $$;

COMMIT;

-- =============================================
-- VERIFICAÇÃO
-- =============================================

-- Listar todas as tabelas com campo updated_at
SELECT
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND column_name = 'updated_at'
ORDER BY table_name;

-- Listar triggers criados
SELECT
    trigger_name,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public'
AND trigger_name LIKE '%updated_at%'
ORDER BY event_object_table;

-- Mensagem de sucesso
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✓ Migration 004 executada com sucesso!';
    RAISE NOTICE '  - Triggers problemáticos removidos';
    RAISE NOTICE '  - Função update_updated_at_column() corrigida';
    RAISE NOTICE '  - Triggers criados corretamente em todas as tabelas';
    RAISE NOTICE '';
END $$;
