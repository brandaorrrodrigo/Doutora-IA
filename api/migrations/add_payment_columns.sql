-- Migration: Add payment provider columns
-- Date: 2025-01-24
-- Description: Adds provider and payment_url columns to payments table

-- Add provider column if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'payments' AND column_name = 'provider'
    ) THEN
        ALTER TABLE payments ADD COLUMN provider VARCHAR(50) DEFAULT 'stub';
    END IF;
END $$;

-- Add payment_url column if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'payments' AND column_name = 'payment_url'
    ) THEN
        ALTER TABLE payments ADD COLUMN payment_url TEXT;
    END IF;
END $$;

-- Update existing payments to have provider = 'stub'
UPDATE payments SET provider = 'stub' WHERE provider IS NULL;
