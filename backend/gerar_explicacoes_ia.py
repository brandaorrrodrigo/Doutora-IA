#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar explicações IA para questões sem comentários
Usa Ollama com Llama 3.1 para gerar explicações contextuais de qualidade

Uso:
    python gerar_explicacoes_ia.py

Pré-requisitos:
    - Ollama rodando na porta 11434
    - Modelo llama3.1 ou mistral instalado
"""

import os
import subprocess
import json
import requests
import sys
import io
import time

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuração
DB_CONFIG = {
    "user": "doutora_user",
    "database": "doutora",
    "password": "doutora_pass"
}

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"  # Usando Llama 3.1 8B

# Verificar se Ollama está disponível
try:
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
    response.raise_for_status()
except Exception as e:
    print(f"❌ ERRO: Ollama não está rodando em {OLLAMA_BASE_URL}")
    print(f"Erro: {e}")
    print("\nInicie Ollama com: ollama serve")
    sys.exit(1)

def execute_query_docker(sql):
    """Executa query via Docker psql"""
    cmd = [
        "docker", "exec", "-i", "doutora_postgres",
        "psql", "-U", DB_CONFIG["user"], "-d", DB_CONFIG["database"],
        "-t", "-c", sql
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, "PGPASSWORD": DB_CONFIG["password"]},
        timeout=30
    )

    if result.returncode != 0:
        raise Exception(f"PostgreSQL error: {result.stderr}")

    return result.stdout.strip()

def buscar_questoes_sem_explicacao(limite=100):
    """Busca questões sem comentários"""
    sql = f"""
    SELECT json_build_object(
        'id', id,
        'enunciado', enunciado,
        'alternativas', json_agg(
            json_build_object('letra', letra, 'texto', texto)
            ORDER BY ordem
        ),
        'gabarito', gabarito,
        'topico', topico,
        'dificuldade', dificuldade
    )
    FROM questoes q
    LEFT JOIN questoes_alternativas qa ON q.id = qa.questao_id
    WHERE (comentario IS NULL OR comentario = '')
    GROUP BY q.id
    ORDER BY q.id
    LIMIT {limite}
    """

    result = execute_query_docker(sql)

    questoes = []
    for line in result.split('\n'):
        if line.strip():
            try:
                questoes.append(json.loads(line))
            except:
                pass

    return questoes

def gerar_explicacao_ia(questao):
    """Gera explicação usando Ollama com Llama 3.1"""

    # Montar string de alternativas
    alternativas_str = "\n".join([
        f"{alt['letra']}: {alt['texto']}"
        for alt in questao.get('alternativas', [])
    ])

    prompt = f"""Você é um professor de Direito experiente. Analise esta questão e forneça uma explicação clara e educativa.

QUESTÃO:
{questao['enunciado']}

ALTERNATIVAS:
{alternativas_str}

GABARITO: {questao['gabarito']}
TÓPICO: {questao.get('topico', 'Geral')}
DIFICULDADE: {questao['dificuldade']}/5

Por favor, forneça:
1. Uma explicação clara do conceito jurídico envolvido (2-3 linhas)
2. Por que a alternativa correta é a {questao['gabarito']} (1-2 linhas)
3. Por que as outras alternativas estão erradas (breve análise)
4. Uma dica para memorizar ou não cair na pegadinha (1 linha)

Mantenha a explicação concisa mas completa (máximo 250 palavras)."""

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
            },
            timeout=120
        )
        response.raise_for_status()

        resultado = response.json()
        explicacao = resultado.get("response", "").strip()

        if explicacao:
            return explicacao
        else:
            return None

    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout ao gerar explicação (Ollama processando...)")
        return None
    except Exception as e:
        print(f"❌ Erro ao gerar explicação: {e}")
        return None

def atualizar_comentario(questao_id, explicacao):
    """Atualiza comentário da questão no banco"""

    # Escapa aspas para SQL
    explicacao_escaped = explicacao.replace("'", "''")

    sql = f"""
    UPDATE questoes
    SET comentario = '{explicacao_escaped}',
        data_atualizacao = NOW()
    WHERE id = {questao_id}
    RETURNING id
    """

    result = execute_query_docker(sql)
    return bool(result.strip())

def processar_lote(limite=50):
    """Processa um lote de questões"""

    print(f"\n📚 Buscando {limite} questões sem explicação...")
    questoes = buscar_questoes_sem_explicacao(limite)

    if not questoes:
        print("✅ Nenhuma questão pendente de explicação!")
        return 0

    print(f"🔍 Encontradas {len(questoes)} questões")
    print("=" * 80)

    processadas = 0
    erros = 0

    for i, questao in enumerate(questoes, 1):
        try:
            print(f"\n[{i}/{len(questoes)}] Questão #{questao['id']}")
            print(f"Tópico: {questao.get('topico', 'Geral')}")
            print(f"Enunciado: {questao['enunciado'][:80]}...")

            print("⏳ Gerando explicação IA...")
            explicacao = gerar_explicacao_ia(questao)

            if explicacao:
                print("💾 Salvando no banco...")
                if atualizar_comentario(questao['id'], explicacao):
                    print("✅ Explicação adicionada com sucesso!")
                    processadas += 1
                else:
                    print("❌ Erro ao salvar no banco")
                    erros += 1
            else:
                erros += 1

        except Exception as e:
            print(f"❌ Erro: {e}")
            erros += 1

    print("\n" + "=" * 80)
    print(f"\n📊 RESULTADO DO LOTE:")
    print(f"✅ Processadas com sucesso: {processadas}")
    print(f"❌ Erros: {erros}")
    print(f"📈 Taxa de sucesso: {(processadas / len(questoes) * 100):.1f}%")

    return processadas

def main():
    print("\n" + "=" * 80)
    print("🤖 GERADOR DE EXPLICAÇÕES IA - Doutora-IA")
    print("=" * 80)

    # Contar total de questões sem explicação
    sql = "SELECT COUNT(*) FROM questoes WHERE comentario IS NULL OR comentario = ''"
    total_sem_explicacao = int(execute_query_docker(sql).strip())

    print(f"\n📊 Status Atual:")
    print(f"Total de questões sem explicação: {total_sem_explicacao}")

    if total_sem_explicacao == 0:
        print("✅ Todas as questões já possuem explicações!")
        return

    # Processar em lotes
    lotes_processados = 0
    total_processadas = 0

    while True:
        print(f"\n🔄 Processando lote {lotes_processados + 1}...")
        processadas = processar_lote(limite=10)

        if processadas == 0:
            break

        lotes_processados += 1
        total_processadas += processadas

        # Parar após 50 questões para não consumir muita cota de API
        if total_processadas >= 50:
            print(f"\n⚠️  Limite de {total_processadas} questões atingido")
            print(f"Execute novamente para continuar processando")
            break

        # Pequeno delay entre lotes
        import time
        time.sleep(2)

    print("\n" + "=" * 80)
    print(f"🎯 RESUMO FINAL:")
    print(f"Lotes processados: {lotes_processados}")
    print(f"Total de explicações geradas: {total_processadas}")
    print(f"Tempo total: ~{total_processadas * 3} segundos (3s por questão)")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
