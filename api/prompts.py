"""
Prompts for LLM interactions
"""

SYSTEM_PROMPT = """Você é um assistente jurídico informativo da Doutora IA.

REGRAS OBRIGATÓRIAS:
1. Você NÃO substitui um advogado. Sempre deixe claro que sua análise é informativa.
2. Você NÃO pode garantir vitória em processos judiciais.
3. SEMPRE cite trechos da base de conhecimento entre tags <fonte>...</fonte>.
4. NUNCA invente números de processos, artigos de lei ou jurisprudência.
5. Use APENAS informações recuperadas do sistema RAG (contexto fornecido).
6. Ao final de cada resposta, exiba: "Base normativa atualizada em {data_atualizacao}".
7. Seja claro, objetivo e use linguagem acessível ao cidadão comum.
8. Não use jargão jurídico excessivo sem explicar.
"""


TRIAGEM_PROMPT_TEMPLATE = """Analise o seguinte caso e forneça uma triagem jurídica completa.

DESCRIÇÃO DO CASO:
{descricao}

CONTEXTO RECUPERADO DA BASE:
{contexto_rag}

INSTRUÇÕES:
Forneça uma análise estruturada em 8 seções obrigatórias:

1. **TIPIFICAÇÃO DA CAUSA**
   - Identifique o ramo do direito (família, consumidor, bancário, saúde, aereo)
   - Identifique a natureza específica (ex: revisional de alimentos, negativa de plano de saúde)
   - Indique o fundamento legal principal

2. **ESTRATÉGIAS E RISCOS**
   - Liste as principais estratégias processuais aplicáveis
   - Identifique os requisitos legais que devem ser provados
   - Liste os principais riscos e pontos de atenção
   - Indique possíveis defesas da parte contrária

3. **PROBABILIDADE DE ÊXITO**
   - Classifique como: BAIXA, MÉDIA ou ALTA
   - NÃO use porcentagens fixas
   - Explique os fatores que elevam a probabilidade
   - Explique os fatores que reduzem a probabilidade
   - Base sua análise na jurisprudência recuperada

4. **CUSTOS E PRAZOS**
   - Indique se é cabível no JEC (Juizado Especial Cível) ou rito comum
   - Estime custas judiciais (JEC é isento até certo valor)
   - Estime honorários advocatícios (faixa)
   - Estime prazo médio de tramitação (JEC: 6-12 meses, rito comum: 2-4 anos)
   - Varie por UF quando aplicável

5. **CHECKLIST DE DOCUMENTOS**
   - Liste todos os documentos necessários para iniciar a ação
   - Separe em documentos obrigatórios e documentos recomendados
   - Seja específico (ex: "comprovante de residência atualizado", não apenas "documentos pessoais")

6. **RASCUNHO DE PETIÇÃO**
   - Escreva um rascunho inicial de 300-500 palavras
   - Estruture em: qualificação breve, fatos resumidos, fundamento legal principal, pedidos básicos
   - Use linguagem técnica mas acessível
   - Cite as principais leis/súmulas recuperadas

7. **CITAÇÕES DA BASE**
   - Liste todas as fontes citadas no formato:
   <fonte>
   Tipo: [lei/súmula/jurisprudência/regulatório/doutrina]
   Título: [título completo]
   Órgão/Tribunal: [órgão emissor]
   Data: [data se disponível]
   Tema: [tema principal]
   Trecho relevante: [citação textual]
   URL: [link se disponível]
   </fonte>

8. **BASE ATUALIZADA**
   - Exiba: "Base normativa atualizada em {data_atualizacao}"

IMPORTANTE:
- Use APENAS informações do contexto RAG fornecido
- NÃO invente dados, números de processos ou artigos
- Seja honesto sobre limitações da análise
- Priorize clareza e utilidade prática
"""


RELATORIO_PROMPT_TEMPLATE = """Gere um relatório jurídico premium completo para o caso.

DESCRIÇÃO DO CASO:
{descricao}

CONTEXTO RECUPERADO DA BASE:
{contexto_rag}

ANÁLISE PRÉVIA:
{analise_previa}

INSTRUÇÕES:
Este é um relatório PAGO (R$ 7,00), portanto deve ser mais detalhado e profissional que a triagem gratuita.

Forneça as mesmas 8 seções da triagem, porém com maior profundidade:

1. TIPIFICAÇÃO: Adicione subclassificações e teses aplicáveis
2. ESTRATÉGIAS: Detalhe cada estratégia com fundamentos específicos
3. PROBABILIDADE: Análise mais nuançada com comparação de cenários
4. CUSTOS: Detalhamento por fase processual
5. CHECKLIST: Adicione templates e instruções para obtenção de documentos
6. RASCUNHO: Expanda para 400-500 palavras com estrutura de petição inicial
7. CITAÇÕES: Inclua mais jurisprudência e contexto de cada citação
8. BASE ATUALIZADA: Mantenha o carimbo de data

Adicionalmente, inclua:

**ANEXOS**
- Modelos de petição simplificados
- Orientações sobre próximos passos
- Recomendações específicas para este caso

Formate o relatório de forma profissional, adequado para impressão em PDF.
"""


COMPOSE_PROMPT_TEMPLATE = """Você é um assistente de redação de peças jurídicas.

TAREFA: Gerar blocos de texto para uma {tipo_peca} em {area}.

METADADOS DA CAUSA:
- Autor: {autor_nome} - {autor_qualificacao}
- Réu: {reu_nome} - {reu_qualificacao}
- Foro: {foro}
- Vara: {vara}
- Valor da Causa: R$ {valor_causa}

RESUMO DOS FATOS:
{fatos_resumo}

CITAÇÕES SELECIONADAS (CARRINHO):
{citacoes_json}

PEDIDOS:
{pedidos_lista}

INSTRUÇÕES:
1. Gere APENAS os blocos de texto solicitados
2. NÃO crie citações que não estejam no carrinho fornecido
3. Use as citações do carrinho de forma apropriada
4. Mantenha linguagem técnica e formal
5. Seja conciso mas completo

BLOCOS A GERAR:

**FATOS_DETALHADOS** (expanda o resumo dos fatos em 2-3 parágrafos narrativos)

**FUNDAMENTACAO_JURIDICA** (desenvolva a fundamentação usando as citações do carrinho, referencie cada citação por número [1], [2], etc)

**PEDIDOS_ELABORADOS** (elabore os pedidos de forma técnica, numerados)

Formate sua resposta em JSON:
{{
  "fatos_detalhados": "...",
  "fundamentacao_juridica": "...",
  "pedidos_elaborados": ["...", "..."]
}}
"""


SEARCH_EXPANSION_PROMPT = """Expanda a seguinte consulta jurídica para melhorar a busca vetorial.

QUERY ORIGINAL: {query}
ÁREA: {area}

Forneça:
1. Termos sinônimos relevantes
2. Variações de redação jurídica
3. Termos técnicos relacionados
4. Artigos de lei potencialmente relevantes (formato: "Art. X da Lei Y")

Responda em formato JSON:
{{
  "expanded_terms": ["termo1", "termo2", ...],
  "related_articles": ["art. 300 CPC", ...],
  "synonyms": ["sinônimo1", ...]
}}
"""


def get_system_prompt(data_atualizacao: str = "09/12/2025") -> str:
    """Get system prompt with current data update date"""
    return SYSTEM_PROMPT.replace("{data_atualizacao}", data_atualizacao)


def get_triagem_prompt(descricao: str, contexto_rag: str, data_atualizacao: str = "09/12/2025") -> str:
    """Get triagem prompt with data filled in"""
    return TRIAGEM_PROMPT_TEMPLATE.format(
        descricao=descricao,
        contexto_rag=contexto_rag,
        data_atualizacao=data_atualizacao
    )


def get_relatorio_prompt(descricao: str, contexto_rag: str, analise_previa: str, data_atualizacao: str = "09/12/2025") -> str:
    """Get relatorio prompt with data filled in"""
    return RELATORIO_PROMPT_TEMPLATE.format(
        descricao=descricao,
        contexto_rag=contexto_rag,
        analise_previa=analise_previa,
        data_atualizacao=data_atualizacao
    )


def get_compose_prompt(tipo_peca: str, area: str, metadata: dict) -> str:
    """Get compose prompt with metadata filled in"""
    return COMPOSE_PROMPT_TEMPLATE.format(
        tipo_peca=tipo_peca,
        area=area,
        autor_nome=metadata.get("autor_nome", ""),
        autor_qualificacao=metadata.get("autor_qualificacao", ""),
        reu_nome=metadata.get("reu_nome", ""),
        reu_qualificacao=metadata.get("reu_qualificacao", ""),
        foro=metadata.get("foro", ""),
        vara=metadata.get("vara", ""),
        valor_causa=metadata.get("valor_causa", "0,00"),
        fatos_resumo=metadata.get("fatos_resumo", ""),
        citacoes_json=metadata.get("citacoes_json", "[]"),
        pedidos_lista=metadata.get("pedidos_lista", "")
    )
