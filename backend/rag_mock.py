"""
RAG Mock - Catálogo simplificado por áreas
Em produção, substituir por RAG real (Qdrant, Pinecone, etc.)
"""

RAG_CATALOG = {
    "familia": [
        {
            "id": "cc_1694_1710",
            "tipo": "lei",
            "titulo": "Código Civil arts. 1.694 a 1.710 - Alimentos",
            "url": "https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm",
            "trecho": "Art. 1.694. Podem os parentes, os cônjuges ou companheiros pedir uns aos outros os alimentos de que necessitem para viver..."
        },
        {
            "id": "lei_5478_68",
            "tipo": "lei",
            "titulo": "Lei 5.478/68 - Lei de Alimentos",
            "url": "https://www.planalto.gov.br/ccivil_03/leis/l5478.htm",
            "trecho": "Regula a ação de alimentos e dá outras providências..."
        },
    ],
    "consumidor": [
        {
            "id": "cdc_art6",
            "tipo": "lei",
            "titulo": "CDC art. 6º - Direitos Básicos do Consumidor",
            "url": "https://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm",
            "trecho": "São direitos básicos do consumidor: a proteção da vida, saúde e segurança..."
        },
        {
            "id": "sumula_stj_479",
            "tipo": "sumula",
            "titulo": "Súmula STJ 479 - Dano Moral Negativação Indevida",
            "url": "https://www.stj.jus.br/docs_internet/revista/eletronica/stj-revista-sumulas-2016_51_capSumula479.pdf",
            "trecho": "As instituições financeiras respondem objetivamente pelos danos gerados por fortuito interno relativo a fraudes e delitos praticados por terceiros no âmbito de operações bancárias."
        },
    ],
    "bancario": [
        {
            "id": "res_bacen_pix",
            "tipo": "regulatorio",
            "titulo": "Resolução BCB sobre PIX e Fraudes",
            "url": "https://www.bcb.gov.br/estabilidadefinanceira/pix",
            "trecho": "O BCB estabelece regras de segurança e responsabilidade das instituições financeiras..."
        },
    ],
    "saude": [
        {
            "id": "lei_9656_98",
            "tipo": "lei",
            "titulo": "Lei 9.656/98 - Planos de Saúde",
            "url": "https://www.planalto.gov.br/ccivil_03/leis/l9656.htm",
            "trecho": "Dispõe sobre os planos e seguros privados de assistência à saúde..."
        },
    ],
    "aereo": [
        {
            "id": "anac_res_400",
            "tipo": "regulatorio",
            "titulo": "Resolução ANAC 400/2016",
            "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/resolucoes/2016/resolucao-no-400-13-12-2016",
            "trecho": "Dispõe sobre as Condições Gerais de Transporte Aéreo..."
        },
    ],
}


def match_sources(query: str, assunto: str = None) -> list:
    """
    Match simples de fontes baseado em keywords.
    Retorna 2-3 fontes relevantes.
    """
    query_lower = query.lower()
    results = []

    # Se assunto foi especificado, buscar nele primeiro
    if assunto and assunto in RAG_CATALOG:
        results.extend(RAG_CATALOG[assunto][:2])

    # Busca por keywords em todas as áreas
    keywords_map = {
        "pensão": "familia",
        "alimentos": "familia",
        "pix": "bancario",
        "golpe": "bancario",
        "plano de saúde": "saude",
        "ans": "saude",
        "voo": "aereo",
        "atraso": "aereo",
        "consumidor": "consumidor",
        "cdc": "consumidor",
    }

    for keyword, area in keywords_map.items():
        if keyword in query_lower and area in RAG_CATALOG:
            for source in RAG_CATALOG[area]:
                if source not in results:
                    results.append(source)
                    if len(results) >= 3:
                        break

    # Se não encontrou nada, retornar vazio
    return results[:3] if results else []
