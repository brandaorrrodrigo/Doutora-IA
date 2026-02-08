-- =============================================
-- FIX URGENTE: Remover trigger problemático
-- Execute este script no banco de dados para resolver o erro imediatamente
-- =============================================

-- Remover TODOS os triggers que usam update_updated_at_column
DROP TRIGGER IF EXISTS trigger_update_updated_at ON users CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON lawyers CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON subscriptions CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON referrals CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON cost_table CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON processos CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON prazos CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON avaliacoes CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON agendamentos CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON parceiros CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON blog_posts CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON payments CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON cases CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON plans CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON publicacoes_dje CASCADE;
DROP TRIGGER IF EXISTS trigger_update_updated_at ON movimentacoes CASCADE;

-- Remover a função problemática
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Pronto! O erro deve parar de aparecer.
-- Os campos updated_at ainda serão atualizados pelo SQLAlchemy via onupdate=func.now()
