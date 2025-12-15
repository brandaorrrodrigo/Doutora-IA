"""
Build corpus and ingest into Qdrant
"""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.rag import get_rag_system
from normalize import normalize_document


def load_json_documents(json_dir: str) -> dict:
    """
    Load all JSON documents from directory

    Returns:
        Dict with keys: legis, sumulas, juris, regulatorio, doutrina
    """
    documents = {
        "legis": [],
        "sumulas": [],
        "juris": [],
        "regulatorio": [],
        "doutrina": []
    }

    json_path = Path(json_dir)

    # Load each type
    for tipo_file in json_path.glob("*.json"):
        tipo = tipo_file.stem  # lei, sumula, juris, etc.

        with open(tipo_file, "r", encoding="utf-8") as f:
            data = json.load(f)

            # Normalize each document
            for item in data:
                normalized = normalize_document(item, tipo)

                # Add to appropriate collection
                if tipo == "lei":
                    documents["legis"].extend(normalized)
                elif tipo == "sumula":
                    documents["sumulas"].extend(normalized)
                elif tipo == "juris":
                    documents["juris"].extend(normalized)
                elif tipo == "regulatorio":
                    documents["regulatorio"].extend(normalized)
                elif tipo == "doutrina":
                    documents["doutrina"].extend(normalized)

    return documents


def ingest_to_qdrant(documents: dict):
    """
    Ingest documents into Qdrant collections

    Args:
        documents: Dict with normalized documents by collection
    """
    rag = get_rag_system()

    # Create collections if they don't exist
    print("Creating Qdrant collections...")
    rag.create_collections()

    # Ingest each collection
    for collection, docs in documents.items():
        if not docs:
            print(f"No documents for {collection}, skipping...")
            continue

        print(f"\nIngesting {len(docs)} documents into {collection}...")

        # Prepare for bulk insert: (id, payload, text)
        bulk_data = [
            (doc["id"], doc, doc["texto"])
            for doc in docs
        ]

        # Bulk insert
        try:
            rag.bulk_insert(collection, bulk_data)
            print(f"✓ Successfully ingested {len(docs)} documents into {collection}")
        except Exception as e:
            print(f"✗ Error ingesting into {collection}: {e}")


def build_sample_corpus(output_dir: str):
    """
    Build sample corpus for testing

    Creates JSON files with sample legal documents
    """
    os.makedirs(output_dir, exist_ok=True)

    # Sample laws
    leis = [
        {
            "titulo": "Código de Processo Civil - Art. 300",
            "artigo": "Art. 300",
            "texto": "A tutela de urgência será concedida quando houver elementos que evidenciem a probabilidade do direito e o perigo de dano ou o risco ao resultado útil do processo.",
            "area": "familia",
            "orgao": "Congresso Nacional",
            "data": "2015-03-16",
            "vigencia_inicio": "2016-03-18",
            "vigencia_fim": None,
            "fonte_url": "http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm"
        },
        {
            "titulo": "Código de Defesa do Consumidor - Art. 14",
            "artigo": "Art. 14",
            "texto": "O fornecedor de serviços responde, independentemente da existência de culpa, pela reparação dos danos causados aos consumidores por defeitos relativos à prestação dos serviços, bem como por informações insuficientes ou inadequadas sobre sua fruição e riscos.",
            "area": "consumidor",
            "orgao": "Congresso Nacional",
            "data": "1990-09-11",
            "vigencia_inicio": "1991-03-11",
            "vigencia_fim": None,
            "fonte_url": "http://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm"
        }
    ]

    # Sample súmulas
    sumulas = [
        {
            "titulo": "Súmula 385 do STJ",
            "numero": "385",
            "tribunal": "STJ",
            "texto": "Da anotação irregular em cadastro de proteção ao crédito, não cabe indenização por dano moral, quando preexistente legítima inscrição, ressalvado o direito ao cancelamento.",
            "tema": "Dano moral - cadastro de proteção ao crédito",
            "area": "consumidor",
            "data": "2009-05-27",
            "fonte_url": "https://www.stj.jus.br/docs_internet/revista/eletronica/stj-revista-sumulas-2013_39_capSumula385.pdf"
        },
        {
            "titulo": "Súmula 309 do STJ",
            "numero": "309",
            "tribunal": "STJ",
            "texto": "O débito alimentar que autoriza a prisão civil do alimentante é o que compreende as três prestações anteriores ao ajuizamento da execução e as que se vencerem no curso do processo.",
            "tema": "Alimentos - prisão civil",
            "area": "familia",
            "data": "2005-03-22",
            "fonte_url": "https://www.stj.jus.br/docs_internet/revista/eletronica/stj-revista-sumulas-2013_35_capSumula309.pdf"
        }
    ]

    # Sample jurisprudence
    juris = [
        {
            "numero": "REsp 1737412",
            "classe": "REsp",
            "tribunal": "STJ",
            "ementa": "RECURSO ESPECIAL. DIREITO DO CONSUMIDOR. RESPONSABILIDADE CIVIL. FRAUDE BANCÁRIA. PIX. Trata-se de recurso especial interposto por instituição financeira contra acórdão que manteve a condenação em danos materiais e morais decorrente de fraude em transferências via PIX. A instituição financeira responde objetivamente por falha na segurança do sistema de pagamentos instantâneos.",
            "texto_completo": "RECURSO ESPECIAL. DIREITO DO CONSUMIDOR. RESPONSABILIDADE CIVIL. FRAUDE BANCÁRIA. PIX. Trata-se de recurso especial interposto por instituição financeira contra acórdão que manteve a condenação em danos materiais e morais decorrente de fraude em transferências via PIX. A instituição financeira responde objetivamente por falha na segurança do sistema de pagamentos instantâneos, nos termos do art. 14 do CDC. A fraude configurou falha na prestação do serviço, sendo irrelevante a culpa exclusiva de terceiro quando o sistema não oferece segurança adequada ao consumidor. Recurso especial não provido.",
            "tema": "PIX - Fraude - Responsabilidade do banco",
            "area": "bancario",
            "data": "2023-08-15",
            "leading_case": True,
            "fonte_url": "https://exemplo.com/resp1737412"
        },
        {
            "numero": "REsp 1657156",
            "classe": "REsp",
            "tribunal": "STJ",
            "ementa": "PLANO DE SAÚDE. ROL DA ANS. CARÁTER EXEMPLIFICATIVO. O rol de procedimentos da ANS é exemplificativo, devendo o plano de saúde custear tratamento não listado quando há indicação médica e urgência.",
            "texto_completo": "O rol de procedimentos e eventos em saúde suplementar constitui referência básica, de caráter exemplificativo e não taxativo, para os planos privados de assistência à saúde. A cobertura mínima obrigatória não impede a prestação de atendimento e procedimentos não previstos expressamente no rol, desde que haja prescrição médica e urgência do tratamento. Recurso especial provido.",
            "tema": "Plano de saúde - Rol ANS - Negativa de cobertura",
            "area": "saude",
            "data": "2022-06-08",
            "leading_case": True,
            "fonte_url": "https://exemplo.com/resp1657156"
        }
    ]

    # Sample regulatory
    regulatorio = [
        {
            "titulo": "Resolução Normativa ANS nº 465/2021",
            "numero": "465",
            "orgao": "ANS",
            "texto": "Atualiza o Rol de Procedimentos e Eventos em Saúde, que constitui a referência básica para cobertura assistencial mínima nos planos privados de assistência à saúde, contratados a partir de 1º de janeiro de 1999; fixa as diretrizes de atenção à saúde; revoga as Resoluções Normativas - RN nº 387, de 28 de outubro de 2015, RN nº 469, de 23 de julho de 2021, RN nº 470, de 23 de julho de 2021; e dá outras providências.",
            "tema": "Rol ANS - Procedimentos e eventos em saúde",
            "area": "saude",
            "data": "2021-08-24",
            "vigencia_inicio": "2022-01-01",
            "vigencia_fim": None,
            "fonte_url": "https://www.gov.br/ans/pt-br/assuntos/consumidor/o-que-seu-plano-deve-cobrir/resolucao-normativa-rn-no-465"
        },
        {
            "titulo": "Resolução BCB nº 107/2020 - PIX",
            "numero": "107",
            "orgao": "BACEN",
            "texto": "Disciplina o Pix, arranjo de pagamento instantâneo no âmbito do Sistema de Pagamentos Brasileiro (SPB). O Pix é um meio de pagamento eletrônico que permite a transferência de recursos entre contas em poucos segundos, a qualquer hora ou dia. As instituições participantes devem garantir a segurança e a autenticação das transações.",
            "tema": "PIX - Sistema de pagamentos instantâneos",
            "area": "bancario",
            "data": "2020-10-09",
            "vigencia_inicio": "2020-11-16",
            "vigencia_fim": None,
            "fonte_url": "https://www.bcb.gov.br/estabilidadefinanceira/pix"
        }
    ]

    # Sample doctrine
    doutrina = [
        {
            "titulo": "A Responsabilidade Civil das Instituições Financeiras em Operações de PIX",
            "autor": "Dra. Maria Silva",
            "texto": "A responsabilidade das instituições financeiras em operações realizadas por meio do PIX segue a regra geral do CDC, sendo objetiva. Não se admite a excludente de culpa exclusiva de terceiro quando há falha no sistema de segurança. O banco deve garantir mecanismos de autenticação robustos e sistemas de detecção de fraudes. A simples alegação de que o cliente foi vítima de phishing ou engenharia social não afasta a responsabilidade da instituição financeira se o sistema permitiu a efetivação de transações suspeitas sem validação adicional.",
            "tema": "Responsabilidade bancária - PIX - Fraude",
            "area": "bancario",
            "data": "2024-03-15",
            "fonte_url": "https://exemplo.com/artigo-pix"
        },
        {
            "titulo": "O Rol da ANS e a Cobertura de Procedimentos Não Listados",
            "autor": "Dr. João Santos",
            "texto": "A jurisprudência do STJ consolidou o entendimento de que o rol de procedimentos da ANS possui caráter exemplificativo. Isso significa que, havendo prescrição médica e justificativa técnica, o plano de saúde deve custear tratamentos não expressamente previstos no rol. A recusa injustificada configura prática abusiva e pode gerar danos morais além da obrigação de custear o procedimento. A seguradora deve avaliar cada caso concretamente, considerando a urgência e a necessidade do tratamento.",
            "tema": "Plano de saúde - Rol ANS - Interpretação",
            "area": "saude",
            "data": "2024-01-20",
            "fonte_url": "https://exemplo.com/artigo-ans"
        }
    ]

    # Save to JSON files
    with open(os.path.join(output_dir, "lei.json"), "w", encoding="utf-8") as f:
        json.dump(leis, f, ensure_ascii=False, indent=2)

    with open(os.path.join(output_dir, "sumula.json"), "w", encoding="utf-8") as f:
        json.dump(sumulas, f, ensure_ascii=False, indent=2)

    with open(os.path.join(output_dir, "juris.json"), "w", encoding="utf-8") as f:
        json.dump(juris, f, ensure_ascii=False, indent=2)

    with open(os.path.join(output_dir, "regulatorio.json"), "w", encoding="utf-8") as f:
        json.dump(regulatorio, f, ensure_ascii=False, indent=2)

    with open(os.path.join(output_dir, "doutrina.json"), "w", encoding="utf-8") as f:
        json.dump(doutrina, f, ensure_ascii=False, indent=2)

    print(f"✓ Sample corpus created in {output_dir}")
    print(f"  - {len(leis)} laws")
    print(f"  - {len(sumulas)} súmulas")
    print(f"  - {len(juris)} jurisprudence")
    print(f"  - {len(regulatorio)} regulatory")
    print(f"  - {len(doutrina)} doctrine")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build and ingest legal corpus")
    parser.add_argument("--sample", action="store_true", help="Build sample corpus")
    parser.add_argument("--ingest", type=str, help="Ingest JSON files from directory")

    args = parser.parse_args()

    if args.sample:
        # Build sample corpus
        output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "json")
        build_sample_corpus(output_dir)

        # Ingest it
        print("\nIngesting sample corpus...")
        docs = load_json_documents(output_dir)
        ingest_to_qdrant(docs)

    elif args.ingest:
        # Ingest from specified directory
        print(f"Loading documents from {args.ingest}...")
        docs = load_json_documents(args.ingest)

        print("\nIngesting into Qdrant...")
        ingest_to_qdrant(docs)

    else:
        parser.print_help()
