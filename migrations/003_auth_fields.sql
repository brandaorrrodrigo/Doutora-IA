-- Migration 003: Campos de Autenticação JWT
-- Adiciona campos necessários para autenticação e tracking de login

BEGIN;

-- =============================================
-- ADICIONAR CAMPOS EM LAWYERS
-- =============================================

-- Campo de último login
ALTER TABLE lawyers ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;

-- Campo de verificação de email
ALTER TABLE lawyers ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE;

-- Comentários
COMMENT ON COLUMN lawyers.last_login_at IS 'Data e hora do último login do advogado';
COMMENT ON COLUMN lawyers.verified_at IS 'Data e hora em que o email foi verificado';

-- =============================================
-- ÍNDICES
-- =============================================

-- Índice para busca rápida de advogados verificados
CREATE INDEX IF NOT EXISTS idx_lawyers_verified ON lawyers(is_verified) WHERE is_verified = TRUE;

-- Índice para busca de advogados por último login
CREATE INDEX IF NOT EXISTS idx_lawyers_last_login ON lawyers(last_login_at);

-- =============================================
-- ADICIONAR CAMPOS EM USERS (se necessário)
-- =============================================

-- Campo de último login para usuários finais
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;

-- Campo de verificação de email para usuários finais
ALTER TABLE users ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN users.last_login_at IS 'Data e hora do último login do usuário';
COMMENT ON COLUMN users.verified_at IS 'Data e hora em que o email foi verificado';

-- =============================================
-- TABELA DE REFRESH TOKENS (opcional - para invalidação)
-- =============================================

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    lawyer_id INTEGER REFERENCES lawyers(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    token_id VARCHAR(255) UNIQUE NOT NULL,  -- JTI do token
    token_hash VARCHAR(255) NOT NULL,  -- Hash do token para segurança

    -- Metadata
    user_agent TEXT,
    ip_address VARCHAR(45),

    -- Timestamps
    issued_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE,

    -- Status
    is_revoked BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Garantir que apenas um tipo de usuário está associado
    CONSTRAINT check_only_one_user CHECK (
        (lawyer_id IS NOT NULL AND user_id IS NULL) OR
        (lawyer_id IS NULL AND user_id IS NOT NULL)
    )
);

CREATE INDEX idx_refresh_tokens_lawyer ON refresh_tokens(lawyer_id);
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_id ON refresh_tokens(token_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_revoked ON refresh_tokens(is_revoked) WHERE NOT is_revoked;

COMMENT ON TABLE refresh_tokens IS 'Armazena refresh tokens para controle de sessões e invalidação';

-- =============================================
-- TABELA DE AUDIT LOG DE AUTENTICAÇÃO
-- =============================================

CREATE TABLE IF NOT EXISTS auth_logs (
    id SERIAL PRIMARY KEY,
    lawyer_id INTEGER REFERENCES lawyers(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    event_type VARCHAR(50) NOT NULL,  -- login, logout, register, password_reset, etc
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,

    -- Metadata
    user_agent TEXT,
    ip_address VARCHAR(45),
    location VARCHAR(255),  -- Cidade/País se disponível

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT check_only_one_user_log CHECK (
        (lawyer_id IS NOT NULL AND user_id IS NULL) OR
        (lawyer_id IS NULL AND user_id IS NOT NULL)
    )
);

CREATE INDEX idx_auth_logs_lawyer ON auth_logs(lawyer_id);
CREATE INDEX idx_auth_logs_user ON auth_logs(user_id);
CREATE INDEX idx_auth_logs_event ON auth_logs(event_type);
CREATE INDEX idx_auth_logs_created ON auth_logs(created_at DESC);

COMMENT ON TABLE auth_logs IS 'Log de eventos de autenticação para auditoria e segurança';

-- =============================================
-- FUNÇÃO PARA LIMPAR TOKENS EXPIRADOS
-- =============================================

CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM refresh_tokens
    WHERE expires_at < CURRENT_TIMESTAMP
    AND NOT is_revoked;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_tokens() IS 'Remove refresh tokens expirados do banco de dados';

-- =============================================
-- FUNÇÃO PARA REGISTRAR EVENTO DE AUTH
-- =============================================

CREATE OR REPLACE FUNCTION log_auth_event(
    p_lawyer_id INTEGER DEFAULT NULL,
    p_user_id INTEGER DEFAULT NULL,
    p_event_type VARCHAR DEFAULT 'login',
    p_success BOOLEAN DEFAULT TRUE,
    p_error_message TEXT DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_ip_address VARCHAR DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO auth_logs (
        lawyer_id,
        user_id,
        event_type,
        success,
        error_message,
        user_agent,
        ip_address
    ) VALUES (
        p_lawyer_id,
        p_user_id,
        p_event_type,
        p_success,
        p_error_message,
        p_user_agent,
        p_ip_address
    );
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION log_auth_event IS 'Registra evento de autenticação no log de auditoria';

-- =============================================
-- VIEW PARA SESSÕES ATIVAS
-- =============================================

CREATE OR REPLACE VIEW active_sessions AS
SELECT
    rt.id,
    rt.token_id,
    COALESCE(l.name, u.name) as user_name,
    COALESCE(l.email, u.email) as user_email,
    CASE
        WHEN rt.lawyer_id IS NOT NULL THEN 'lawyer'
        ELSE 'user'
    END as user_type,
    rt.issued_at,
    rt.expires_at,
    rt.user_agent,
    rt.ip_address,
    EXTRACT(EPOCH FROM (rt.expires_at - CURRENT_TIMESTAMP)) / 3600 as hours_until_expiry
FROM refresh_tokens rt
LEFT JOIN lawyers l ON rt.lawyer_id = l.id
LEFT JOIN users u ON rt.user_id = u.id
WHERE rt.is_revoked = FALSE
AND rt.expires_at > CURRENT_TIMESTAMP
ORDER BY rt.issued_at DESC;

COMMENT ON VIEW active_sessions IS 'View de sessões ativas (tokens não expirados e não revogados)';

-- =============================================
-- DADOS INICIAIS (se necessário)
-- =============================================

-- Marcar advogados existentes como verificados por padrão
-- (remover em produção se quiser forçar verificação)
UPDATE lawyers
SET is_verified = TRUE, verified_at = CURRENT_TIMESTAMP
WHERE is_verified = FALSE;

COMMIT;

-- =============================================
-- VERIFICAÇÃO
-- =============================================

-- Verificar se campos foram adicionados
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'lawyers'
AND column_name IN ('last_login_at', 'verified_at')
ORDER BY column_name;

-- Verificar tabelas criadas
SELECT table_name
FROM information_schema.tables
WHERE table_name IN ('refresh_tokens', 'auth_logs')
AND table_schema = 'public';

-- Verificar view
SELECT table_name
FROM information_schema.views
WHERE table_name = 'active_sessions'
AND table_schema = 'public';

-- Mensagem de sucesso
DO $$
BEGIN
    RAISE NOTICE '✓ Migration 003 (Auth Fields) executada com sucesso!';
    RAISE NOTICE '  - Campos last_login_at e verified_at adicionados';
    RAISE NOTICE '  - Tabelas refresh_tokens e auth_logs criadas';
    RAISE NOTICE '  - View active_sessions criada';
    RAISE NOTICE '  - Funções de limpeza e log criadas';
END $$;
