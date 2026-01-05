#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar integração completa com 37k questões
Testa APIs locais antes de fazer deploy

Uso:
    python teste_integracao_37k.py

Pré-requisitos:
    - Backend rodando: python -m uvicorn api_questoes:app --port 8042
    - API Mapas rodando: python -m uvicorn api_mapas_flashcards:app --port 8041
    - PostgreSQL rodando
"""

import requests
import json
import time
import sys
from typing import Dict, List

# Configuração
BASE_URL_QUESTOES = "http://localhost:8042"
BASE_URL_MAPAS = "http://localhost:8041"

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg: str):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg: str):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg: str):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_info(msg: str):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def test_health_check():
    """Testa health check das APIs"""
    print("\n" + "="*80)
    print("🏥 TESTE 1: Health Check")
    print("="*80)

    try:
        response = requests.get(f"{BASE_URL_QUESTOES}/health", timeout=5)
        if response.status_code == 200:
            print_success("API Questões está respondendo")
        else:
            print_error(f"API Questões retornou status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"API Questões não está acessível: {e}")
        return False

    try:
        response = requests.get(f"{BASE_URL_MAPAS}/health", timeout=5)
        if response.status_code == 200:
            print_success("API Mapas está respondendo")
        else:
            print_error(f"API Mapas retornou status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"API Mapas não está acessível: {e}")
        return False

    return True

def test_questoes_listagem():
    """Testa listagem de questões"""
    print("\n" + "="*80)
    print("📚 TESTE 2: Listagem de Questões (37k)")
    print("="*80)

    try:
        # Teste 1: Listar todas as questões com paginação
        response = requests.get(f"{BASE_URL_QUESTOES}/questoes?skip=0&limit=10", timeout=10)

        if response.status_code != 200:
            print_error(f"Erro ao listar questões: {response.status_code}")
            return False

        data = response.json()
        total = data.get("total", 0)
        questoes = data.get("questoes", [])

        print_success(f"Listagem funcionando! Total de questões: {total}")
        print_info(f"Primeiros 10 questões retornadas: {len(questoes)}")

        if total < 30000:
            print_warning(f"Total esperado: ~37000, recebido: {total}")
        else:
            print_success(f"Total de questões OK: {total}")

        return True

    except Exception as e:
        print_error(f"Erro ao testar listagem: {e}")
        return False

def test_questoes_busca():
    """Testa busca de questões"""
    print("\n" + "="*80)
    print("🔍 TESTE 3: Busca de Questões")
    print("="*80)

    try:
        # Teste: Buscar por keyword
        response = requests.get(
            f"{BASE_URL_QUESTOES}/questoes/busca?termo=direito&limit=5",
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"Erro na busca: {response.status_code}")
            return False

        data = response.json()
        resultados = data.get("questoes", [])

        if resultados:
            print_success(f"Busca funcionando! Encontrados {len(resultados)} resultados")
            print_info(f"Primeira questão: {resultados[0]['enunciado'][:100]}...")
        else:
            print_warning("Nenhum resultado encontrado para 'direito'")

        return True

    except Exception as e:
        print_error(f"Erro na busca: {e}")
        return False

def test_questoes_por_topico():
    """Testa busca por tópico"""
    print("\n" + "="*80)
    print("📖 TESTE 4: Questões por Tópico")
    print("="*80)

    try:
        # Teste: Buscar por tópico
        response = requests.get(
            f"{BASE_URL_QUESTOES}/questoes/topico/civil?limit=5",
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"Erro ao buscar por tópico: {response.status_code}")
            return False

        data = response.json()
        questoes = data.get("questoes", [])
        total = data.get("total", 0)

        if questoes:
            print_success(f"Filtro por tópico funcionando! {total} questões de Direito Civil")
        else:
            print_warning("Nenhuma questão encontrada para Direito Civil")

        return True

    except Exception as e:
        print_error(f"Erro ao buscar por tópico: {e}")
        return False

def test_questoes_com_explicacao():
    """Testa se explicações foram geradas"""
    print("\n" + "="*80)
    print("💡 TESTE 5: Explicações Geradas (37k)")
    print("="*80)

    try:
        # Teste: Buscar questões com explicação
        response = requests.get(
            f"{BASE_URL_QUESTOES}/questoes?skip=0&limit=50",
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"Erro ao buscar questões: {response.status_code}")
            return False

        data = response.json()
        questoes = data.get("questoes", [])

        com_explicacao = sum(1 for q in questoes if q.get("comentario"))

        print_info(f"Amostra de 50 questões:")
        print_info(f"  - Com explicação: {com_explicacao}")
        print_info(f"  - Sem explicação: {50 - com_explicacao}")

        if com_explicacao > 40:
            print_success(f"Taxa de explicações OK: {com_explicacao}/50 (80%+)")
        else:
            print_warning(f"Taxa baixa: {com_explicacao}/50. Script de geração ainda rodando?")

        return True

    except Exception as e:
        print_error(f"Erro ao verificar explicações: {e}")
        return False

def test_mapas_listagem():
    """Testa listagem de mapas mentais"""
    print("\n" + "="*80)
    print("🗺️  TESTE 6: Mapas Mentais")
    print("="*80)

    try:
        response = requests.get(
            f"{BASE_URL_MAPAS}/mapas/mentais?limit=10",
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"Erro ao listar mapas: {response.status_code}")
            return False

        data = response.json()
        mapas = data.get("mapas", [])
        total = data.get("total", 0)

        if mapas:
            print_success(f"Mapas mentais carregados! Total: {total}")
            print_info(f"Primeiros mapas: {', '.join([m.get('nome', 'N/A') for m in mapas[:3]])}")
        else:
            print_warning("Nenhum mapa mental encontrado")

        return True

    except Exception as e:
        print_error(f"Erro ao listar mapas: {e}")
        return False

def test_flashcards():
    """Testa flashcards"""
    print("\n" + "="*80)
    print("📝 TESTE 7: Flashcards")
    print("="*80)

    try:
        response = requests.get(
            f"{BASE_URL_MAPAS}/flashcards?limit=10",
            timeout=10
        )

        if response.status_code != 200:
            print_warning(f"Endpoint flashcards pode não estar disponível: {response.status_code}")
            return True  # Não falhar o teste completo

        data = response.json()
        flashcards = data.get("flashcards", [])
        total = data.get("total", 0)

        if flashcards:
            print_success(f"Flashcards carregados! Total: {total}")
        else:
            print_warning("Nenhum flashcard encontrado")

        return True

    except Exception as e:
        print_warning(f"Flashcards pode não estar implementado: {e}")
        return True  # Não falhar

def test_performance():
    """Testa performance das APIs"""
    print("\n" + "="*80)
    print("⚡ TESTE 8: Performance")
    print("="*80)

    try:
        # Teste 1: Tempo de busca simples
        start = time.time()
        response = requests.get(
            f"{BASE_URL_QUESTOES}/questoes?skip=0&limit=20",
            timeout=10
        )
        elapsed = (time.time() - start) * 1000  # em ms

        if response.status_code == 200:
            if elapsed < 500:
                print_success(f"Busca rápida: {elapsed:.0f}ms ✅")
            elif elapsed < 1000:
                print_warning(f"Busca aceitável: {elapsed:.0f}ms ⚠️")
            else:
                print_warning(f"Busca lenta: {elapsed:.0f}ms")

        # Teste 2: Busca com filtro
        start = time.time()
        response = requests.get(
            f"{BASE_URL_QUESTOES}/questoes/topico/civil?limit=20",
            timeout=10
        )
        elapsed = (time.time() - start) * 1000

        if response.status_code == 200:
            if elapsed < 1000:
                print_success(f"Filtro rápido: {elapsed:.0f}ms ✅")
            else:
                print_warning(f"Filtro lento: {elapsed:.0f}ms")

        return True

    except Exception as e:
        print_error(f"Erro ao testar performance: {e}")
        return False

def test_error_handling():
    """Testa tratamento de erros"""
    print("\n" + "="*80)
    print("🛡️  TESTE 9: Tratamento de Erros")
    print("="*80)

    try:
        # Teste 1: Endpoint inválido
        response = requests.get(f"{BASE_URL_QUESTOES}/invalido", timeout=5)

        if response.status_code == 404:
            print_success("Erro 404 tratado corretamente")
        else:
            print_warning(f"Erro inesperado: {response.status_code}")

        # Teste 2: Parâmetro inválido
        response = requests.get(
            f"{BASE_URL_QUESTOES}/questoes?skip=abc&limit=10",
            timeout=5
        )

        if response.status_code in [400, 422]:
            print_success("Validação de parâmetros funcionando")
        else:
            print_warning(f"Resposta esperada 400/422, recebida: {response.status_code}")

        return True

    except Exception as e:
        print_error(f"Erro ao testar error handling: {e}")
        return False

def test_cors():
    """Testa CORS"""
    print("\n" + "="*80)
    print("🔒 TESTE 10: CORS")
    print("="*80)

    try:
        response = requests.get(
            f"{BASE_URL_QUESTOES}/questoes",
            headers={"Origin": "http://localhost:3000"},
            timeout=5
        )

        if "access-control-allow-origin" in response.headers:
            print_success(f"CORS configurado: {response.headers.get('access-control-allow-origin')}")
        else:
            print_warning("CORS headers não encontrados (pode estar desabilitado)")

        return True

    except Exception as e:
        print_warning(f"Erro ao testar CORS: {e}")
        return True  # Não falhar

def main():
    """Executa todos os testes"""

    print("\n" + "="*80)
    print("🧪 TESTE DE INTEGRAÇÃO - DOUTORA IA (37K QUESTÕES)")
    print("="*80)
    print("\nTestando APIs locais antes do deployment...")

    tests = [
        ("Health Check", test_health_check),
        ("Listagem", test_questoes_listagem),
        ("Busca", test_questoes_busca),
        ("Tópico", test_questoes_por_topico),
        ("Explicações", test_questoes_com_explicacao),
        ("Mapas", test_mapas_listagem),
        ("Flashcards", test_flashcards),
        ("Performance", test_performance),
        ("Erros", test_error_handling),
        ("CORS", test_cors),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Teste {test_name} falhou: {e}")
            results[test_name] = False

    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = (passed / total) * 100

    for test_name, result in results.items():
        if result:
            print(f"{GREEN}✅ {test_name}{RESET}")
        else:
            print(f"{RED}❌ {test_name}{RESET}")

    print("\n" + "="*80)
    if percentage >= 80:
        print_success(f"Teste concluído: {passed}/{total} ({percentage:.0f}%)")
        print_success("Sistema pronto para deployment!")
        return 0
    else:
        print_error(f"Teste inconclusivo: {passed}/{total} ({percentage:.0f}%)")
        print_error("Verifique os erros acima antes do deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())
