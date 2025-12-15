-- Initial schema for Doutora IA
-- This script creates all tables and initial data

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(50),
    cpf VARCHAR(14) UNIQUE,
    hashed_password VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_cpf ON users(cpf);

-- Lawyers table
CREATE TABLE IF NOT EXISTS lawyers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    oab VARCHAR(50) UNIQUE NOT NULL,
    phone VARCHAR(50),
    cpf VARCHAR(14) UNIQUE,
    hashed_password VARCHAR(255),
    areas TEXT[],
    cities TEXT[],
    states TEXT[],
    bio TEXT,
    success_score NUMERIC(5,2) DEFAULT 0.0,
    total_leads INTEGER DEFAULT 0,
    accepted_leads INTEGER DEFAULT 0,
    rejected_leads INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    last_lead_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_lawyers_email ON lawyers(email);
CREATE INDEX idx_lawyers_oab ON lawyers(oab);
CREATE INDEX idx_lawyers_areas ON lawyers USING GIN(areas);

-- Plans table
CREATE TABLE IF NOT EXISTS plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    feature_search BOOLEAN DEFAULT FALSE,
    feature_advanced_search BOOLEAN DEFAULT FALSE,
    feature_jurimetrics BOOLEAN DEFAULT FALSE,
    feature_leads BOOLEAN DEFAULT FALSE,
    feature_priority_leads BOOLEAN DEFAULT FALSE,
    feature_document_generation BOOLEAN DEFAULT FALSE,
    feature_premium_templates BOOLEAN DEFAULT FALSE,
    leads_per_month INTEGER DEFAULT 0,
    docs_per_month INTEGER DEFAULT 0,
    searches_per_day INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    lawyer_id INTEGER UNIQUE NOT NULL REFERENCES lawyers(id) ON DELETE CASCADE,
    plan_id INTEGER NOT NULL REFERENCES plans(id),
    status VARCHAR(50) DEFAULT 'active',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    leads_used INTEGER DEFAULT 0,
    docs_used INTEGER DEFAULT 0,
    searches_today INTEGER DEFAULT 0,
    last_search_date TIMESTAMP WITH TIME ZONE,
    external_subscription_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_subscriptions_lawyer ON subscriptions(lawyer_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);

-- Cases table
CREATE TABLE IF NOT EXISTS cases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    description TEXT NOT NULL,
    area VARCHAR(100),
    sub_area VARCHAR(255),
    typification TEXT,
    strategies TEXT,
    risks TEXT,
    probability VARCHAR(20),
    cost_estimate TEXT,
    timeline_estimate TEXT,
    checklist JSONB,
    draft_petition TEXT,
    citations JSONB,
    score_prob NUMERIC(5,2),
    status VARCHAR(50) DEFAULT 'pending',
    report_paid BOOLEAN DEFAULT FALSE,
    report_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    analyzed_at TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_cases_user ON cases(user_id);
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_cases_area ON cases(area);

-- Referrals table
CREATE TABLE IF NOT EXISTS referrals (
    id SERIAL PRIMARY KEY,
    case_id INTEGER UNIQUE NOT NULL REFERENCES cases(id),
    lawyer_id INTEGER NOT NULL REFERENCES lawyers(id),
    status VARCHAR(50) DEFAULT 'pending',
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    responded_at TIMESTAMP WITH TIME ZONE,
    response_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_referrals_case ON referrals(case_id);
CREATE INDEX idx_referrals_lawyer ON referrals(lawyer_id);
CREATE INDEX idx_referrals_status ON referrals(status);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    case_id INTEGER UNIQUE REFERENCES cases(id),
    amount NUMERIC(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'BRL',
    status VARCHAR(50) DEFAULT 'pending',
    external_payment_id VARCHAR(255) UNIQUE,
    pix_qr_code TEXT,
    pix_qr_code_base64 TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_payments_case ON payments(case_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_external_id ON payments(external_payment_id);

-- Citations log table
CREATE TABLE IF NOT EXISTS citations_log (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50),
    source_id INTEGER,
    citation_id VARCHAR(255) NOT NULL,
    citation_type VARCHAR(50),
    citation_title VARCHAR(500),
    citation_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_citations_source ON citations_log(source_type, source_id);

-- Cost table
CREATE TABLE IF NOT EXISTS cost_table (
    id SERIAL PRIMARY KEY,
    state VARCHAR(2) NOT NULL,
    area VARCHAR(100) NOT NULL,
    court_fees_jec NUMERIC(10,2),
    court_fees_comum NUMERIC(10,2),
    lawyer_fees_min NUMERIC(10,2),
    lawyer_fees_max NUMERIC(10,2),
    timeline_jec_min INTEGER,
    timeline_jec_max INTEGER,
    timeline_comum_min INTEGER,
    timeline_comum_max INTEGER,
    notes TEXT,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_cost_state_area ON cost_table(state, area);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    lawyer_id INTEGER REFERENCES lawyers(id),
    properties JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_user ON events(user_id);
CREATE INDEX idx_events_lawyer ON events(lawyer_id);
CREATE INDEX idx_events_created ON events(created_at);

-- Insert default plans
INSERT INTO plans (name, price, feature_search, feature_advanced_search, feature_jurimetrics, feature_leads, feature_priority_leads, feature_document_generation, feature_premium_templates, leads_per_month, docs_per_month, searches_per_day) VALUES
('Pesquisa', 79.00, TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, 0, 0, 50),
('Leads', 99.00, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, 10, 0, 0),
('Redacao', 149.00, TRUE, FALSE, FALSE, FALSE, FALSE, TRUE, FALSE, 0, 30, 20),
('Pro', 229.00, TRUE, TRUE, TRUE, FALSE, FALSE, TRUE, TRUE, 0, 50, 100),
('Full', 299.00, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 999, 999, 999)
ON CONFLICT (name) DO NOTHING;

-- Insert sample cost data (São Paulo)
INSERT INTO cost_table (state, area, court_fees_jec, court_fees_comum, lawyer_fees_min, lawyer_fees_max, timeline_jec_min, timeline_jec_max, timeline_comum_min, timeline_comum_max, notes) VALUES
('SP', 'familia', 0.00, 450.00, 2000.00, 8000.00, 180, 360, 730, 1460, 'JEC isento até 40 salários mínimos'),
('SP', 'consumidor', 0.00, 350.00, 1500.00, 5000.00, 120, 240, 540, 1095, 'JEC isento até 40 salários mínimos'),
('SP', 'bancario', 0.00, 500.00, 2500.00, 10000.00, 150, 300, 730, 1460, 'Valores variam conforme montante'),
('SP', 'saude', 0.00, 600.00, 3000.00, 12000.00, 90, 180, 365, 730, 'Liminar comum em casos urgentes')
ON CONFLICT DO NOTHING;

COMMIT;
