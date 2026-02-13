@echo off
cd /d D:\doutora-ia
python scripts/ingest_ebooks_md.py --data-dir D:\doutora-ia\direito\ebooksmds --resume >> D:\doutora-ia\ingest_full.log 2>&1
echo Exit code: %ERRORLEVEL% >> D:\doutora-ia\ingest_full.log
