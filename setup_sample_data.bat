@echo off
REM Setup sample data for Doutora IA

echo === Doutora IA - Setup Sample Data ===
echo.

REM Create data directories
echo Creating data directories...
if not exist data\raw mkdir data\raw
if not exist data\clean mkdir data\clean
if not exist data\json mkdir data\json

REM Generate sample corpus
echo Generating sample corpus...
cd ingest
python build_corpus.py --sample
cd ..

echo.
echo === Sample data setup complete! ===
echo.
echo Next steps:
echo 1. Start the services: docker compose up -d
echo 2. Wait for services to be healthy
echo 3. Sample corpus is already ingested into Qdrant
echo 4. Access the web interface at http://localhost:3000

pause
