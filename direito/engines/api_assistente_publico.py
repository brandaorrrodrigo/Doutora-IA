"""
API Assistente Jurídico Público - Doutora IA
API REST completa integrando todos os engines

Produto: Assistência jurídica para cidadãos + Marketplace de advogados
Preço: R$ 7,00 por parecer para cliente
Planos advogados: R$ 197/397/597 por mês

Versão: 1.0.0
Data: 31/12/2025
Porta: 8116
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional, Any
from datetime import datetime
import uvicorn

# Importar engines
from engine_assistente_publico import (
    EngineAssistentePublico, TipoCaso, RespostasCompletas,
    RespostaUsuario, criar_engine_assistente
)
from engine_gerador_pareceres import (
    EngineGeradorPareceres, ParecerPremium,
    ConfiguracaoParecer, criar_engine_pareceres
)
from engine_marketplace_advogados import (
    EngineMarketplaceAdvogados, DadosCliente, PlanoAdvogado,
    EspecialidadeAdvogado, EnderecoAdvogado, criar_engine_marketplace
)
from engine_pagamentos import (
    EnginePagamentos, MetodoPagamento, TipoProduto,
    DadosCartao, criar_engine_pagamentos
)

# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="Doutora IA - Assistente Jurídico Público",
    description="API para assistência jurídica ao cidadão e marketplace de advogados",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Engines (singleton)
engine_assistente = criar_engine_assistente()
engine_pareceres = criar_engine_pareceres()
engine_marketplace = criar_engine_marketplace()
engine_pagamentos = criar_engine_pagamentos(producao=False)

# =====================================================
# MODELS - REQUEST
# =====================================================

class RespostaQuizRequest(BaseModel):
    pergunta_id: str
    valor: Any

class AnaliseCasoRequest(BaseModel):
    tipo_caso: str
    respostas: List[RespostaQuizRequest]

class ComprarParecerRequest(BaseModel):
    tipo_caso: str
    respostas: List[RespostaQuizRequest]
    dados_cliente: Dict[str, str]
    metodo_pagamento: str
    cupom: Optional[str] = None
    dados_cartao: Optional[Dict] = None

class CadastroAdvogadoRequest(BaseModel):
    oab_numero: str
    oab_estado: str
    nome_completo: str
    email: EmailStr
    telefone: str
    especialidades: List[str]
    endereco: Dict[str, str]
    plano: str

class AvaliarAdvogadoRequest(BaseModel):
    advogado_id: str
    cliente_id: str
    lead_id: str
    nota: float
    comentario: Optional[str] = None

# =====================================================
# ENDPOINTS - PÚBLICO
# =====================================================

@app.get("/")
def root():
    """Homepage da API"""
    return {
        "servico": "Doutora IA - Assistente Jurídico Público",
        "versao": "1.0.0",
        "descricao": "Assistência jurídica inteligente para todos os brasileiros",
        "preco_parecer": "R$ 7,00",
        "casos_disponiveis": 10,
        "docs": "/docs"
    }

@app.get("/health")
def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engines": {
            "assistente": "ok",
            "pareceres": "ok",
            "marketplace": "ok",
            "pagamentos": "ok"
        }
    }

# =====================================================
# ENDPOINTS - CASOS E QUIZZES
# =====================================================

@app.get("/api/casos")
def listar_casos():
    """Lista todos os tipos de casos disponíveis"""
    casos = engine_assistente.listar_casos_disponiveis()
    return {
        "total": len(casos),
        "casos": casos
    }

@app.get("/api/casos/{tipo_caso}/quiz")
def obter_quiz(tipo_caso: str):
    """Obtém o quiz para um tipo de caso"""
    try:
        tipo = TipoCaso(tipo_caso)
        quiz = engine_assistente.obter_quiz(tipo)

        if not quiz:
            raise HTTPException(404, "Quiz não encontrado")

        # Converter para dict
        return {
            "tipo_caso": quiz.tipo_caso.value,
            "titulo": quiz.titulo,
            "descricao": quiz.descricao,
            "tempo_estimado_minutos": quiz.tempo_estimado_minutos,
            "perguntas": [
                {
                    "id": p.id,
                    "texto": p.texto,
                    "tipo": p.tipo,
                    "obrigatoria": p.obrigatoria,
                    "opcoes": [
                        {"valor": o.valor, "texto": o.texto}
                        for o in p.opcoes
                    ] if p.opcoes else [],
                    "ajuda": p.ajuda,
                    "condicao": p.condicao
                }
                for p in quiz.perguntas
            ]
        }

    except ValueError:
        raise HTTPException(400, f"Tipo de caso inválido: {tipo_caso}")

@app.post("/api/analise-gratuita")
def analise_gratuita(request: AnaliseCasoRequest):
    """Análise gratuita do caso (sem pagamento)"""
    try:
        tipo = TipoCaso(request.tipo_caso)

        # Converter respostas
        respostas = RespostasCompletas(
            tipo_caso=tipo,
            respostas=[
                RespostaUsuario(r.pergunta_id, r.valor)
                for r in request.respostas
            ]
        )

        # Analisar
        analise = engine_assistente.analisar_caso(respostas)

        # Retornar versão gratuita
        return {
            "tipo_caso": analise.tipo_caso.value,
            "viabilidade": analise.viabilidade.value,
            "complexidade": analise.complexidade.value,
            "urgencia": analise.urgencia.value,
            "resumo": analise.resumo_caso,
            "direitos_principais": analise.direitos_principais,
            "valores_estimados": {
                "minimo": analise.calculo_valores.valor_minimo if analise.calculo_valores else None,
                "maximo": analise.calculo_valores.valor_maximo if analise.calculo_valores else None,
                "medio": analise.calculo_valores.valor_medio if analise.calculo_valores else None
            } if analise.calculo_valores else None,
            "tempo_estimado_meses": analise.tempo_estimado_meses,
            "probabilidade_sucesso": f"{analise.probabilidade_sucesso*100:.1f}%",
            "estatisticas": {
                "total_casos_similares": analise.estatisticas.total_casos_similares,
                "taxa_sucesso": f"{analise.estatisticas.taxa_sucesso_percentual}%",
                "tempo_medio_meses": analise.estatisticas.tempo_medio_meses
            },
            "alertas": analise.alertas_importantes,
            "preco_parecer_completo": 7.00,
            "mensagem": "Esta é a análise gratuita. Por R$ 7,00 você recebe o parecer completo com jurisprudência, modelos de documentos e estratégia detalhada."
        }

    except ValueError as e:
        raise HTTPException(400, str(e))

# =====================================================
# ENDPOINTS - PAGAMENTO E PARECER
# =====================================================

@app.post("/api/comprar-parecer")
def comprar_parecer(request: ComprarParecerRequest):
    """Compra parecer completo por R$ 7,00"""
    try:
        tipo = TipoCaso(request.tipo_caso)
        metodo = MetodoPagamento(request.metodo_pagamento)

        # 1. Criar análise
        respostas = RespostasCompletas(
            tipo_caso=tipo,
            respostas=[
                RespostaUsuario(r.pergunta_id, r.valor)
                for r in request.respostas
            ]
        )

        # 2. Gerar parecer completo
        parecer = engine_pareceres.gerar_parecer_completo(
            respostas=respostas,
            dados_cliente=request.dados_cliente
        )

        # 3. Criar pagamento
        dados_cartao = None
        if request.dados_cartao:
            dados_cartao = DadosCartao(**request.dados_cartao)

        transacao = engine_pagamentos.criar_pagamento_parecer(
            usuario_id=request.dados_cliente.get("email", "anonimo"),
            usuario_email=request.dados_cliente.get("email", ""),
            parecer_id=parecer.numero_parecer,
            metodo=metodo,
            cupom=request.cupom,
            dados_cartao=dados_cartao
        )

        # 4. Retornar dados conforme método
        resposta = {
            "parecer_id": parecer.numero_parecer,
            "transacao_id": transacao.id,
            "valor": transacao.valor,
            "valor_original": 7.00,
            "metodo_pagamento": metodo.value,
            "status_pagamento": transacao.status.value
        }

        # PIX
        if metodo == MetodoPagamento.PIX and transacao.dados_pix:
            resposta["pix"] = {
                "qr_code": transacao.dados_pix.qr_code,
                "chave": transacao.dados_pix.chave_pix,
                "validade_minutos": transacao.dados_pix.validade_minutos
            }
            resposta["mensagem"] = "Pague via PIX para liberar seu parecer"

        # Boleto
        elif metodo == MetodoPagamento.BOLETO and transacao.dados_boleto:
            resposta["boleto"] = {
                "linha_digitavel": transacao.dados_boleto.linha_digitavel,
                "url_pdf": transacao.dados_boleto.url_pdf,
                "vencimento": transacao.dados_boleto.data_vencimento
            }
            resposta["mensagem"] = "Pague o boleto para liberar seu parecer"

        # Cartão (aprovado imediatamente em demo)
        elif metodo in [MetodoPagamento.CARTAO_CREDITO, MetodoPagamento.CARTAO_DEBITO]:
            if transacao.status.value == "aprovado":
                # Parecer aprovado! Retornar conteúdo
                resposta["parecer_completo"] = engine_pareceres.exportar_para_markdown(parecer)
                resposta["mensagem"] = "Pagamento aprovado! Seu parecer está pronto."

                # 5. Criar lead e distribuir para advogados
                lead = engine_marketplace.criar_lead(
                    tipo_caso=tipo.value,
                    urgencia=parecer.analise_gratuita.urgencia.value,
                    viabilidade=parecer.analise_gratuita.viabilidade.value,
                    cliente=DadosCliente(
                        nome=request.dados_cliente.get("nome", ""),
                        email=request.dados_cliente.get("email", ""),
                        telefone=request.dados_cliente.get("telefone", ""),
                        cidade=request.dados_cliente.get("cidade", "SP"),
                        estado=request.dados_cliente.get("estado", "SP")
                    ),
                    resumo_caso=parecer.analise_gratuita.resumo_caso,
                    respostas_quiz={r.pergunta_id: r.valor for r in request.respostas},
                    parecer_completo=engine_pareceres.exportar_para_markdown(parecer)
                )

                # Distribuir lead
                matches = engine_marketplace.distribuir_lead(lead.id)

                if matches:
                    resposta["advogados_disponiveis"] = len(matches)
                    resposta["advogados"] = [
                        {
                            "nome": engine_marketplace._advogados[m.advogado_id].nome_completo,
                            "oab": f"{engine_marketplace._advogados[m.advogado_id].oab_numero}/{engine_marketplace._advogados[m.advogado_id].oab_estado}",
                            "nota": engine_marketplace._advogados[m.advogado_id].estatisticas.nota_media,
                            "cidade": engine_marketplace._advogados[m.advogado_id].endereco.cidade if engine_marketplace._advogados[m.advogado_id].endereco else "N/A",
                            "telefone": engine_marketplace._advogados[m.advogado_id].telefone,
                            "email": engine_marketplace._advogados[m.advogado_id].email
                        }
                        for m in matches
                    ]
            else:
                resposta["mensagem"] = "Pagamento recusado. Tente outro cartão."

        return resposta

    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Erro ao processar: {str(e)}")

@app.post("/api/confirmar-pagamento/{transacao_id}")
def confirmar_pagamento(transacao_id: str, metodo: str):
    """Webhook para confirmar pagamento (PIX/Boleto)"""
    try:
        if metodo == "pix":
            sucesso = engine_pagamentos.confirmar_pagamento_pix(transacao_id)
        elif metodo == "boleto":
            sucesso = engine_pagamentos.confirmar_pagamento_boleto(transacao_id)
        else:
            raise HTTPException(400, "Método inválido")

        if not sucesso:
            raise HTTPException(404, "Transação não encontrada")

        # Obter transação
        transacao = engine_pagamentos.obter_transacao(transacao_id)

        # Se foi aprovada, retornar parecer
        if transacao.status.value == "aprovado":
            # Buscar parecer pela referencia_id
            return {
                "status": "aprovado",
                "mensagem": "Pagamento confirmado! Acesse seu parecer.",
                "parecer_liberado": True
            }

        return {"status": transacao.status.value}

    except Exception as e:
        raise HTTPException(500, str(e))

# =====================================================
# ENDPOINTS - ADVOGADOS
# =====================================================

@app.post("/api/advogados/cadastro")
def cadastrar_advogado(request: CadastroAdvogadoRequest):
    """Cadastro de novo advogado parceiro"""
    try:
        plano = PlanoAdvogado(request.plano)
        especialidades = [EspecialidadeAdvogado(e) for e in request.especialidades]

        endereco = EnderecoAdvogado(**request.endereco)

        advogado = engine_marketplace.cadastrar_advogado(
            oab_numero=request.oab_numero,
            oab_estado=request.oab_estado,
            nome_completo=request.nome_completo,
            email=request.email,
            telefone=request.telefone,
            especialidades=especialidades,
            endereco=endereco,
            plano=plano
        )

        # Criar assinatura
        assinatura = engine_pagamentos.criar_assinatura_advogado(
            usuario_id=advogado.id,
            tipo_plano=TipoProduto(f"assinatura_advogado_{plano.value}"),
            metodo=MetodoPagamento.CARTAO_CREDITO
        )

        return {
            "advogado_id": advogado.id,
            "status": advogado.status.value,
            "assinatura_id": assinatura.id,
            "valor_mensal": assinatura.valor_mensal,
            "mensagem": "Cadastro realizado! Aguarde aprovação."
        }

    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/advogados/dashboard/{advogado_id}")
def dashboard_advogado(advogado_id: str):
    """Dashboard do advogado"""
    dashboard = engine_marketplace.obter_dashboard_advogado(advogado_id)

    if not dashboard:
        raise HTTPException(404, "Advogado não encontrado")

    return dashboard

@app.get("/api/advogados/{advogado_id}/leads")
def listar_leads_advogado(advogado_id: str):
    """Lista leads do advogado"""
    matches = [m for m in engine_marketplace._matches if m.advogado_id == advogado_id]

    leads = []
    for match in matches:
        lead_data = engine_marketplace.obter_lead_para_advogado(advogado_id, match.lead_id)
        if lead_data:
            leads.append(lead_data)

    return {"total": len(leads), "leads": leads}

@app.post("/api/advogados/{advogado_id}/leads/{lead_id}/contatar")
def marcar_contato(advogado_id: str, lead_id: str):
    """Marca que advogado contatou o lead"""
    sucesso = engine_marketplace.marcar_lead_contatado(advogado_id, lead_id)

    if not sucesso:
        raise HTTPException(404, "Lead não encontrado")

    return {"status": "ok", "mensagem": "Lead marcado como contatado"}

@app.post("/api/advogados/avaliar")
def avaliar_advogado(request: AvaliarAdvogadoRequest):
    """Cliente avalia advogado"""
    sucesso = engine_marketplace.avaliar_advogado(
        advogado_id=request.advogado_id,
        cliente_id=request.cliente_id,
        lead_id=request.lead_id,
        nota=request.nota,
        comentario=request.comentario
    )

    if not sucesso:
        raise HTTPException(404, "Advogado não encontrado")

    return {"status": "ok", "mensagem": "Avaliação registrada"}

# =====================================================
# ENDPOINTS - BUSCA DE ADVOGADOS
# =====================================================

@app.get("/api/advogados/buscar")
def buscar_advogados(
    cidade: str,
    estado: str,
    especialidade: Optional[str] = None
):
    """Busca advogados por localização"""

    esp = EspecialidadeAdvogado(especialidade) if especialidade else None

    candidatos = engine_marketplace.buscar_advogados_por_localizacao(
        cidade=cidade,
        estado=estado,
        especialidade=esp,
        limite=5
    )

    return {
        "total": len(candidatos),
        "advogados": [
            {
                "id": c['advogado'].id,
                "nome": c['advogado'].nome_completo,
                "oab": f"{c['advogado'].oab_numero}/{c['advogado'].oab_estado}",
                "especialidades": [e.value for e in c['advogado'].especialidades],
                "nota_media": c['advogado'].estatisticas.nota_media,
                "total_avaliacoes": c['advogado'].estatisticas.total_avaliacoes,
                "cidade": c['advogado'].endereco.cidade if c['advogado'].endereco else None,
                "distancia_km": c['distancia_estimada'],
                "score": c['score'],
                "telefone": c['advogado'].telefone,
                "email": c['advogado'].email
            }
            for c in candidatos
        ]
    }

# =====================================================
# ENDPOINTS - ADMIN
# =====================================================

@app.get("/api/admin/estatisticas")
def estatisticas_gerais():
    """Estatísticas gerais da plataforma"""
    return {
        "total_transacoes": len(engine_pagamentos._transacoes),
        "total_advogados": len(engine_marketplace._advogados),
        "total_leads": len(engine_marketplace._leads),
        "total_assinaturas": len(engine_pagamentos._assinaturas),
        "receita_pareceres": sum(
            t.valor for t in engine_pagamentos._transacoes.values()
            if t.tipo_produto == TipoProduto.PARECER_CLIENTE and t.status.value == "aprovado"
        ),
        "receita_assinaturas_mes": sum(
            a.valor_mensal for a in engine_pagamentos._assinaturas.values()
            if a.status.value == "ativa"
        )
    }

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DOUTORA IA - ASSISTENTE JURIDICO PUBLICO")
    print("=" * 60)
    print(f"Versao: 1.0.0")
    print(f"Porta: 8116")
    print(f"Docs: http://localhost:8116/docs")
    print(f"")
    print(f"Recursos:")
    print(f"  - 10 tipos de casos juridicos")
    print(f"  - Analise gratuita com IA")
    print(f"  - Parecer completo: R$ 7,00")
    print(f"  - Marketplace de advogados")
    print(f"  - Planos para advogados: R$ 197/397/597/mes")
    print("=" * 60)
    print("")

    uvicorn.run(app, host="0.0.0.0", port=8116)
