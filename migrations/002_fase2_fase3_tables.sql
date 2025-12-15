-- Migration para Fase 2 (Tribunais) e Fase 3 (Marketplace)
-- Execute após 001_initial_schema.sql

-- =============================================
-- FASE 2: INTEGRAÇÃO COM TRIBUNAIS
-- =============================================

-- Tabela de processos monitorados
CREATE TABLE IF NOT EXISTS processos (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(50) UNIQUE NOT NULL,
    tribunal VARCHAR(20) NOT NULL,
    lawyer_id INTEGER REFERENCES lawyers(id) ON DELETE CASCADE,
    case_id INTEGER REFERENCES cases(id),

    -- Dados do processo
    classe VARCHAR(100),
    assunto VARCHAR(500),
    vara VARCHAR(200),
    juiz VARCHAR(200),
    valor_causa NUMERIC(15,2),
    data_distribuicao DATE,

    -- Partes
    partes JSONB,

    -- Monitoramento
    monitorar BOOLEAN DEFAULT TRUE,
    ultima_atualizacao TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_processos_numero ON processos(numero);
CREATE INDEX idx_processos_lawyer ON processos(lawyer_id);
CREATE INDEX idx_processos_tribunal ON processos(tribunal);


-- Tabela de movimentações processuais
CREATE TABLE IF NOT EXISTS movimentacoes (
    id SERIAL PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processos(id) ON DELETE CASCADE,

    data DATE NOT NULL,
    tipo VARCHAR(200),
    descricao TEXT,

    -- Análise IA
    relevante BOOLEAN DEFAULT FALSE,
    tipo_movimentacao VARCHAR(50),  -- decisao, despacho, certidao, juntada
    sentimento VARCHAR(20),  -- favoravel, desfavoravel, neutro

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_movimentacoes_processo ON movimentacoes(processo_id);
CREATE INDEX idx_movimentacoes_data ON movimentacoes(data DESC);


-- Tabela de prazos processuais
CREATE TABLE IF NOT EXISTS prazos (
    id SERIAL PRIMARY KEY,
    processo_id INTEGER NOT NULL REFERENCES processos(id) ON DELETE CASCADE,
    lawyer_id INTEGER NOT NULL REFERENCES lawyers(id),

    tipo VARCHAR(100) NOT NULL,  -- recurso, contestacao, manifestacao, etc
    data_limite DATE NOT NULL,
    dias_restantes INTEGER,

    -- Alertas
    alertado BOOLEAN DEFAULT FALSE,
    alerta_5_dias BOOLEAN DEFAULT FALSE,
    alerta_3_dias BOOLEAN DEFAULT FALSE,
    alerta_1_dia BOOLEAN DEFAULT FALSE,

    -- Status
    cumprido BOOLEAN DEFAULT FALSE,
    cumprido_em TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_prazos_processo ON prazos(processo_id);
CREATE INDEX idx_prazos_lawyer ON prazos(lawyer_id);
CREATE INDEX idx_prazos_data ON prazos(data_limite);
CREATE INDEX idx_prazos_alertado ON prazos(alertado) WHERE NOT alertado;


-- Tabela de publicações DJe
CREATE TABLE IF NOT EXISTS publicacoes_dje (
    id SERIAL PRIMARY KEY,
    processo_id INTEGER REFERENCES processos(id),
    lawyer_id INTEGER REFERENCES lawyers(id),

    tribunal VARCHAR(20) NOT NULL,
    data_publicacao DATE NOT NULL,
    tipo VARCHAR(100),
    texto TEXT,

    prazo_dias INTEGER,
    prazo_data_limite DATE,

    lido BOOLEAN DEFAULT FALSE,
    lido_em TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_publicacoes_tribunal ON publicacoes_dje(tribunal);
CREATE INDEX idx_publicacoes_data ON publicacoes_dje(data_publicacao DESC);
CREATE INDEX idx_publicacoes_lawyer ON publicacoes_dje(lawyer_id);
CREATE INDEX idx_publicacoes_lido ON publicacoes_dje(lido) WHERE NOT lido;


-- =============================================
-- FASE 3: MARKETPLACE E PERFIL PÚBLICO
-- =============================================

-- Adicionar campos em lawyers para perfil público
ALTER TABLE lawyers ADD COLUMN IF NOT EXISTS slug VARCHAR(255) UNIQUE;
ALTER TABLE lawyers ADD COLUMN IF NOT EXISTS perfil_url VARCHAR(500);
ALTER TABLE lawyers ADD COLUMN IF NOT EXISTS rating NUMERIC(3,2) DEFAULT 0.0;
ALTER TABLE lawyers ADD COLUMN IF NOT EXISTS total_ratings INTEGER DEFAULT 0;
ALTER TABLE lawyers ADD COLUMN IF NOT EXISTS perfil_publico BOOLEAN DEFAULT TRUE;
ALTER TABLE lawyers ADD COLUMN IF NOT EXISTS consulta_gratis BOOLEAN DEFAULT TRUE;
ALTER TABLE lawyers ADD COLUMN IF NOT EXISTS perfil_gerado_em TIMESTAMP WITH TIME ZONE;

-- Adicionar índice para slug
CREATE INDEX IF NOT EXISTS idx_lawyers_slug ON lawyers(slug);


-- Tabela de avaliações
CREATE TABLE IF NOT EXISTS avaliacoes (
    id SERIAL PRIMARY KEY,
    lawyer_id INTEGER NOT NULL REFERENCES lawyers(id) ON DELETE CASCADE,
    case_id INTEGER REFERENCES cases(id),
    user_id INTEGER REFERENCES users(id),

    nota INTEGER NOT NULL CHECK (nota >= 1 AND nota <= 5),
    comentario TEXT,

    -- Moderação
    aprovado BOOLEAN DEFAULT TRUE,
    visivel BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_avaliacoes_lawyer ON avaliacoes(lawyer_id);
CREATE INDEX idx_avaliacoes_nota ON avaliacoes(nota);
CREATE INDEX idx_avaliacoes_visivel ON avaliacoes(visivel) WHERE visivel;


-- Tabela de agendamentos
CREATE TABLE IF NOT EXISTS agendamentos (
    id SERIAL PRIMARY KEY,
    lawyer_id INTEGER NOT NULL REFERENCES lawyers(id) ON DELETE CASCADE,
    case_id INTEGER REFERENCES cases(id),
    user_id INTEGER REFERENCES users(id),

    data_hora TIMESTAMP WITH TIME ZONE NOT NULL,
    duracao_minutos INTEGER DEFAULT 15,
    tipo VARCHAR(50) DEFAULT 'consulta_inicial',  -- consulta_inicial, retorno, audiencia

    -- Status
    status VARCHAR(50) DEFAULT 'pendente',  -- pendente, confirmado, cancelado, realizado
    confirmado_em TIMESTAMP WITH TIME ZONE,
    cancelado_em TIMESTAMP WITH TIME ZONE,
    realizado_em TIMESTAMP WITH TIME ZONE,

    -- Detalhes
    notas TEXT,
    link_videochamada VARCHAR(500),

    -- Lembretes
    lembrete_24h_enviado BOOLEAN DEFAULT FALSE,
    lembrete_1h_enviado BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_agendamentos_lawyer ON agendamentos(lawyer_id);
CREATE INDEX idx_agendamentos_user ON agendamentos(user_id);
CREATE INDEX idx_agendamentos_data ON agendamentos(data_hora);
CREATE INDEX idx_agendamentos_status ON agendamentos(status);


-- Tabela de parcerias B2B2C
CREATE TABLE IF NOT EXISTS parceiros (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL,  -- sindicato, empresa, banco, plano_saude
    cnpj VARCHAR(18) UNIQUE,

    -- Contato
    contato_nome VARCHAR(255),
    contato_email VARCHAR(255),
    contato_telefone VARCHAR(50),

    -- Comercial
    comissao_percent NUMERIC(5,2) DEFAULT 15.0,
    plano_id INTEGER REFERENCES plans(id),

    -- Status
    ativo BOOLEAN DEFAULT TRUE,
    contrato_inicio DATE,
    contrato_fim DATE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_parceiros_tipo ON parceiros(tipo);
CREATE INDEX idx_parceiros_ativo ON parceiros(ativo) WHERE ativo;


-- Tabela de leads de parcerias
CREATE TABLE IF NOT EXISTS leads_parceria (
    id SERIAL PRIMARY KEY,
    parceiro_id INTEGER NOT NULL REFERENCES parceiros(id),
    case_id INTEGER NOT NULL REFERENCES cases(id),

    -- Dados adicionais da parceria
    identificador_externo VARCHAR(255),  -- ID do cliente no sistema do parceiro
    metadata JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_leads_parceria_parceiro ON leads_parceria(parceiro_id);
CREATE INDEX idx_leads_parceria_case ON leads_parceria(case_id);


-- Tabela de blog posts (gerados por IA)
CREATE TABLE IF NOT EXISTS blog_posts (
    id SERIAL PRIMARY KEY,
    lawyer_id INTEGER REFERENCES lawyers(id) ON DELETE CASCADE,

    titulo VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    conteudo TEXT,
    area VARCHAR(100),

    -- SEO
    meta_description VARCHAR(500),
    keywords TEXT,

    -- Status
    publicado BOOLEAN DEFAULT FALSE,
    publicado_em TIMESTAMP WITH TIME ZONE,

    -- Analytics
    visualizacoes INTEGER DEFAULT 0,
    ultima_visualizacao TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_blog_posts_lawyer ON blog_posts(lawyer_id);
CREATE INDEX idx_blog_posts_slug ON blog_posts(slug);
CREATE INDEX idx_blog_posts_area ON blog_posts(area);
CREATE INDEX idx_blog_posts_publicado ON blog_posts(publicado) WHERE publicado;


-- Tabela de notificações
CREATE TABLE IF NOT EXISTS notificacoes (
    id SERIAL PRIMARY KEY,
    lawyer_id INTEGER REFERENCES lawyers(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    tipo VARCHAR(50) NOT NULL,  -- novo_lead, prazo, publicacao, agendamento
    titulo VARCHAR(255) NOT NULL,
    mensagem TEXT,

    -- Links
    link_url VARCHAR(500),
    link_texto VARCHAR(100),

    -- Status
    lida BOOLEAN DEFAULT FALSE,
    lida_em TIMESTAMP WITH TIME ZONE,
    enviada_whatsapp BOOLEAN DEFAULT FALSE,
    enviada_email BOOLEAN DEFAULT FALSE,
    enviada_sms BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notificacoes_lawyer ON notificacoes(lawyer_id);
CREATE INDEX idx_notificacoes_user ON notificacoes(user_id);
CREATE INDEX idx_notificacoes_tipo ON notificacoes(tipo);
CREATE INDEX idx_notificacoes_lida ON notificacoes(lida) WHERE NOT lida;
CREATE INDEX idx_notificacoes_created ON notificacoes(created_at DESC);


-- Adicionar campo em cases para rastreamento de parceria
ALTER TABLE cases ADD COLUMN IF NOT EXISTS origem VARCHAR(50) DEFAULT 'direto';  -- direto, parceria, indicacao
ALTER TABLE cases ADD COLUMN IF NOT EXISTS parceiro_id INTEGER REFERENCES parceiros(id);


-- Função para atualizar rating médio do advogado
CREATE OR REPLACE FUNCTION atualizar_rating_advogado()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE lawyers
    SET
        rating = (
            SELECT AVG(nota)
            FROM avaliacoes
            WHERE lawyer_id = NEW.lawyer_id AND visivel = TRUE
        ),
        total_ratings = (
            SELECT COUNT(*)
            FROM avaliacoes
            WHERE lawyer_id = NEW.lawyer_id AND visivel = TRUE
        )
    WHERE id = NEW.lawyer_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar rating automaticamente
DROP TRIGGER IF EXISTS trigger_atualizar_rating ON avaliacoes;
CREATE TRIGGER trigger_atualizar_rating
    AFTER INSERT OR UPDATE ON avaliacoes
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_rating_advogado();


-- View para dashboard do advogado
CREATE OR REPLACE VIEW dashboard_advogado AS
SELECT
    l.id as lawyer_id,
    l.name,
    l.oab,
    l.rating,
    l.total_ratings,
    l.success_score,
    l.total_leads,
    l.accepted_leads,
    l.rejected_leads,

    -- Leads pendentes
    (SELECT COUNT(*)
     FROM referrals r
     WHERE r.lawyer_id = l.id AND r.status = 'pending' AND r.expires_at > NOW()) as leads_pendentes,

    -- Prazos próximos (5 dias)
    (SELECT COUNT(*)
     FROM prazos p
     WHERE p.lawyer_id = l.id AND p.data_limite <= CURRENT_DATE + INTERVAL '5 days' AND NOT p.cumprido) as prazos_proximos,

    -- Agendamentos hoje
    (SELECT COUNT(*)
     FROM agendamentos a
     WHERE a.lawyer_id = l.id AND DATE(a.data_hora) = CURRENT_DATE AND a.status != 'cancelado') as agendamentos_hoje,

    -- Notificações não lidas
    (SELECT COUNT(*)
     FROM notificacoes n
     WHERE n.lawyer_id = l.id AND NOT n.lida) as notificacoes_nao_lidas

FROM lawyers l
WHERE l.is_active = TRUE;


COMMIT;
