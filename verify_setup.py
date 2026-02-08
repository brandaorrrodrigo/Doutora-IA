#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG System Setup Verification
Checks all prerequisites and dependencies before running the system
"""

import os
import sys
import subprocess
from pathlib import Path

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class SetupVerifier:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []

    def print_header(self, text):
        """Print section header"""
        print("\n" + "="*80)
        print(f"  {text}")
        print("="*80 + "\n")

    def check_python(self):
        """Check Python version"""
        self.print_header("1. PYTHON VERSION")
        version = sys.version_info

        if version.major >= 3 and version.minor >= 10:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
            print(f"   Location: {sys.executable}\n")
            self.checks_passed += 1
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor} (need 3.10+)\n")
            self.checks_failed += 1
            return False

    def check_cuda(self):
        """Check CUDA availability"""
        self.print_header("2. NVIDIA CUDA & GPU")

        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,name,driver_version,memory.total"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                print("✅ NVIDIA GPU detected:\n")
                for line in lines[1:]:  # Skip header
                    print(f"   {line}")
                print()
                self.checks_passed += 1
                return True
            else:
                print("❌ nvidia-smi command failed")
                print("   CUDA might not be installed\n")
                self.checks_failed += 1
                return False

        except FileNotFoundError:
            print("❌ nvidia-smi not found")
            print("   CUDA Toolkit might not be installed\n")
            print("   Download: https://developer.nvidia.com/cuda-toolkit\n")
            self.checks_failed += 1
            return False
        except Exception as e:
            print(f"❌ Error checking CUDA: {e}\n")
            self.checks_failed += 1
            return False

    def check_ollama(self):
        """Check Ollama installation and running status"""
        self.print_header("3. OLLAMA LLM SERVER")

        # Check if ollama is installed
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✅ Ollama installed: {result.stdout.strip()}\n")
            else:
                print("❌ Ollama installation detected but --version failed\n")
                self.checks_failed += 1
                return False

        except FileNotFoundError:
            print("❌ Ollama not found in PATH")
            print("   Download: https://ollama.ai\n")
            self.checks_failed += 1
            return False
        except Exception as e:
            print(f"❌ Error checking Ollama: {e}\n")
            self.checks_failed += 1
            return False

        # Check if ollama server is running
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"✅ Ollama server running at http://localhost:11434")
                print(f"   Available models: {len(models)}\n")

                if models:
                    print("   Installed models:")
                    for model in models[:5]:
                        model_name = model.get("name", "unknown")
                        print(f"     • {model_name}")
                    if len(models) > 5:
                        print(f"     ... and {len(models) - 5} more")
                    print()

                    # Check for llama3 or mistral
                    model_names = [m.get("name", "") for m in models]
                    if any("llama3" in name for name in model_names):
                        print("✅ llama3 model available\n")
                    elif any("mistral" in name for name in model_names):
                        print("⚠️  llama3 not found, but mistral available\n")
                        self.warnings.append("Consider: ollama pull llama3")
                    else:
                        print("⚠️  Neither llama3 nor mistral found\n")
                        self.warnings.append("Run: ollama pull llama3")
                else:
                    print("   ⚠️  No models installed\n")
                    self.warnings.append("Run: ollama pull llama3")

                self.checks_passed += 1
                return True
            else:
                print("❌ Ollama server returned error\n")
                self.checks_failed += 1
                return False

        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama server (http://localhost:11434)")
            print("   Make sure Ollama is running: ollama serve\n")
            self.checks_failed += 1
            return False
        except Exception as e:
            print(f"❌ Error checking Ollama server: {e}\n")
            self.checks_failed += 1
            return False

    def check_pytorch(self):
        """Check PyTorch and CUDA support"""
        self.print_header("4. PYTORCH & CUDA SUPPORT")

        try:
            import torch
            print(f"✅ PyTorch version: {torch.__version__}")

            if torch.cuda.is_available():
                print(f"✅ CUDA support: YES")
                print(f"   Device: {torch.cuda.get_device_name(0)}")
                print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB\n")
                self.checks_passed += 1
                return True
            else:
                print("⚠️  CUDA support: NO (PyTorch CPU-only)")
                print("   Reinstall: pip install torch --index-url https://download.pytorch.org/whl/cu121\n")
                self.warnings.append("PyTorch CUDA support not available")
                self.checks_passed += 1
                return False

        except ImportError:
            print("❌ PyTorch not installed")
            print("   Install: pip install -r requirements.txt\n")
            self.checks_failed += 1
            return False
        except Exception as e:
            print(f"❌ Error checking PyTorch: {e}\n")
            self.checks_failed += 1
            return False

    def check_langchain(self):
        """Check LangChain installation"""
        self.print_header("5. LANGCHAIN & DEPENDENCIES")

        required = [
            "langchain",
            "langchain_community",
            "langchain_huggingface",
            "chromadb",
            "sentence_transformers",
        ]

        installed = []
        missing = []

        for module in required:
            try:
                __import__(module)
                installed.append(module)
            except ImportError:
                missing.append(module)

        if installed:
            print(f"✅ Installed: {len(installed)}/{len(required)}\n")
            for module in installed[:3]:
                print(f"   ✓ {module}")
            if len(installed) > 3:
                print(f"   ✓ ... and {len(installed) - 3} more")
            print()

        if missing:
            print(f"❌ Missing: {len(missing)}/{len(required)}\n")
            for module in missing:
                print(f"   ✗ {module}")
            print("\n   Install: pip install -r requirements.txt\n")
            self.checks_failed += 1
            return False

        self.checks_passed += 1
        return True

    def check_documents_directory(self):
        """Check documents directory"""
        self.print_header("6. DOCUMENT LIBRARY")

        docs_dir = r"E:\biblioteca_juridica\direito"

        if os.path.exists(docs_dir):
            md_files = list(Path(docs_dir).rglob("*.md"))
            print(f"✅ Documents directory found: {docs_dir}")
            print(f"✅ Markdown files: {len(md_files)}\n")

            if len(md_files) == 0:
                print("⚠️  Warning: No .md files found\n")
                self.warnings.append("No markdown files in document directory")
            elif len(md_files) < 2000:
                print(f"⚠️  Warning: Expected ~2,752 files, found {len(md_files)}\n")
                self.warnings.append(f"Only {len(md_files)} markdown files found")
            else:
                print(f"   Total size: ~{sum(f.stat().st_size for f in md_files) / 1024**3:.1f} GB\n")

            self.checks_passed += 1
            return True
        else:
            print(f"❌ Documents directory not found: {docs_dir}\n")
            self.checks_failed += 1
            return False

    def check_vector_db(self):
        """Check if vector database exists"""
        self.print_header("7. VECTOR DATABASE")

        vector_db_dir = "vector_db"

        if os.path.exists(vector_db_dir):
            files = os.listdir(vector_db_dir)
            size = sum(
                os.path.getsize(os.path.join(vector_db_dir, f))
                for f in files if os.path.isfile(os.path.join(vector_db_dir, f))
            )
            print(f"✅ Vector database exists: {vector_db_dir}/")
            print(f"   Files: {len(files)}")
            print(f"   Size: {size / 1024**3:.1f} GB\n")
            print("   ℹ️  Database already created - ready to chat!\n")
            self.checks_passed += 1
            return True
        else:
            print(f"⚠️  Vector database not found: {vector_db_dir}/")
            print("   This is normal on first setup")
            print("   You need to run: python ingest.py\n")
            self.warnings.append("Vector database not yet created")
            self.checks_passed += 1
            return False

    def print_summary(self):
        """Print verification summary"""
        self.print_header("VERIFICATION SUMMARY")

        print(f"✅ Passed: {self.checks_passed}")
        print(f"❌ Failed: {self.checks_failed}")

        if self.warnings:
            print(f"⚠️  Warnings: {len(self.warnings)}\n")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
            print()

        if self.checks_failed == 0:
            print("\n" + "🎉 "*20)
            print("\n✨ SETUP VERIFICATION PASSED!\n")
            print("Your system is ready! Next steps:\n")

            if not os.path.exists("vector_db"):
                print("1. CREATE VECTOR DATABASE:")
                print("   python ingest.py")
                print("   (This takes 3-5 minutes, run once)\n")

            print("2. START CHATTING:")
            print("   python chat.py\n")
            print("For detailed setup: see QUICKSTART.md or RAG_SETUP_GUIDE.md\n")

        else:
            print("\n❌ SETUP VERIFICATION FAILED!\n")
            print("Please fix the above issues before proceeding.\n")
            print("For help: see RAG_SETUP_GUIDE.md\n")

        print("="*80 + "\n")

        return self.checks_failed == 0

    def run_all_checks(self):
        """Run all verification checks"""
        print("\n")
        print("╔" + "="*78 + "╗")
        print("║" + " "*15 + "RAG SYSTEM SETUP VERIFICATION" + " "*35 + "║")
        print("╚" + "="*78 + "╝")

        self.check_python()
        self.check_cuda()
        self.check_ollama()
        self.check_pytorch()
        self.check_langchain()
        self.check_documents_directory()
        self.check_vector_db()

        success = self.print_summary()
        return success


def main():
    """Main entry point"""
    verifier = SetupVerifier()
    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
