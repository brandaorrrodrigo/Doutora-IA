#!/bin/bash
# Setup sample data for Doutora IA

echo "=== Doutora IA - Setup Sample Data ==="
echo ""

# Create data directories
echo "Creating data directories..."
mkdir -p data/raw data/clean data/json

# Generate sample corpus
echo "Generating sample corpus..."
cd ingest
python build_corpus.py --sample

echo ""
echo "=== Sample data setup complete! ==="
echo ""
echo "Next steps:"
echo "1. Start the services: docker compose up -d"
echo "2. Wait for services to be healthy"
echo "3. Sample corpus is already ingested into Qdrant"
echo "4. Access the web interface at http://localhost:3000"
