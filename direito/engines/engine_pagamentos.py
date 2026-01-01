"""
Engine de Pagamentos - Doutora IA
Sistema de pagamentos para clientes e advogados

Integrações:
- Mercado Pago (PIX, Boleto, Cartão)
- Stripe (Cartão internacional)

Produtos:
- Cliente: R$ 7,00 por parecer (pagamento único)
- Advogado: R$ 197/397/597 por mês (assinatura)

Versão: 1.0.0
Data: 31/12/2025
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import secrets


# =====================================================
# ENUMS
# =====================================================

class MetodoPagamento(Enum):
    """Métodos de pagamento"""
    PIX = "pix"
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    BOLETO = "boleto"


class StatusPagamento(Enum):
    """Status do pagamento"""
    PENDENTE = "pendente"  # Aguardando pagamento
    PROCESSANDO = "processando"  # Processando
    APROVADO = "aprovado"  # Pago com sucesso
    RECUSADO = "recusado"  # Recusado
    CANCELADO = "cancelado"  # Cancelado
    ESTORNADO = "estornado"  # Estornado


class TipoProduto(Enum):
    """Tipo de produto"""
    PARECER_CLIENTE = "parecer_cliente"  # R$ 7,00
    ASSINATURA_ADVOGADO_BASICO = "assinatura_advogado_basico"  # R$ 197/mês
    ASSINATURA_ADVOGADO_PROFISSIONAL = "assinatura_advogado_profissional"  # R$ 397/mês
    ASSINATURA_ADVOGADO_PREMIUM = "assinatura_advogado_premium"  # R$ 597/mês


class StatusAssinatura(Enum):
    """Status de assinatura"""
    ATIVA = "ativa"
    CANCELADA = "cancelada"
    SUSPENSA = "suspensa"
    VENCIDA = "vencida"


# =====================================================
# DATACLASSES - PAGAMENTO
# =====================================================

@dataclass
class DadosCartao:
    """Dados do cartão (tokenizado em produção)"""
    numero_mascarado: str  # Ex: **** **** **** 1234
    nome_titular: str
    validade_mes: int
    validade_ano: int
    token: Optional[str] = None  # Token do gateway


@dataclass
class DadosPix:
    """Dados PIX"""
    qr_code: str
    chave_pix: str
    qr_code_base64: Optional[str] = None
    validade_minutos: int = 30


@dataclass
class DadosBoleto:
    """Dados do boleto"""
    codigo_barras: str
    linha_digitavel: str
    url_pdf: str
    data_vencimento: str


@dataclass
class Transacao:
    """Transação de pagamento"""
    id: str
    tipo_produto: TipoProduto
    valor: float
    metodo_pagamento: MetodoPagamento
    status: StatusPagamento

    # Cliente/Advogado
    usuario_id: str
    usuario_email: str

    # Referência (parecer ou assinatura)
    referencia_id: str  # ID do parecer ou da assinatura

    # Dados do pagamento
    dados_cartao: Optional[DadosCartao] = None
    dados_pix: Optional[DadosPix] = None
    dados_boleto: Optional[DadosBoleto] = None

    # Timestamps
    data_criacao: str = field(default_factory=lambda: datetime.now().isoformat())
    data_aprovacao: Optional[str] = None
    data_vencimento: Optional[str] = None

    # Gateway
    gateway_id: Optional[str] = None  # ID da transação no gateway (Mercado Pago, Stripe)
    gateway_resposta: Optional[Dict] = None

    # Metadata
    ip_cliente: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class Assinatura:
    """Assinatura recorrente"""
    id: str
    usuario_id: str
    tipo_produto: TipoProduto
    valor_mensal: float
    metodo_pagamento: MetodoPagamento
    status: StatusAssinatura

    # Datas
    data_inicio: str
    data_proxima_cobranca: str
    data_cancelamento: Optional[str] = None

    # Histórico de pagamentos
    pagamentos: List[str] = field(default_factory=list)  # IDs das transações

    # Dados do cartão (para renovação)
    dados_cartao: Optional[DadosCartao] = None

    # Gateway
    assinatura_gateway_id: Optional[str] = None


@dataclass
class Cupom:
    """Cupom de desconto"""
    codigo: str
    desconto_percentual: Optional[float] = None
    desconto_fixo: Optional[float] = None
    valido_ate: Optional[str] = None
    usos_maximos: Optional[int] = None
    usos_atuais: int = 0
    ativo: bool = True


# =====================================================
# ENGINE PAGAMENTOS
# =====================================================

class EnginePagamentos:
    """Engine de pagamentos"""

    def __init__(self, modo_producao: bool = False):
        self.modo_producao = modo_producao
        self._transacoes: Dict[str, Transacao] = {}
        self._assinaturas: Dict[str, Assinatura] = {}
        self._cupons: Dict[str, Cupom] = {}
        self._contador_transacao = 10000
        self._contador_assinatura = 5000

        # Configurações de preços
        self._precos = {
            TipoProduto.PARECER_CLIENTE: 7.00,
            TipoProduto.ASSINATURA_ADVOGADO_BASICO: 197.00,
            TipoProduto.ASSINATURA_ADVOGADO_PROFISSIONAL: 397.00,
            TipoProduto.ASSINATURA_ADVOGADO_PREMIUM: 597.00
        }

        # Carregar cupons demo
        self._criar_cupons_demo()

    # =====================================================
    # PAGAMENTO ÚNICO (PARECERES)
    # =====================================================

    def criar_pagamento_parecer(
        self,
        usuario_id: str,
        usuario_email: str,
        parecer_id: str,
        metodo: MetodoPagamento,
        cupom: Optional[str] = None,
        dados_cartao: Optional[DadosCartao] = None
    ) -> Transacao:
        """Cria pagamento de R$ 7,00 para parecer"""

        valor = self._precos[TipoProduto.PARECER_CLIENTE]

        # Aplicar cupom
        if cupom:
            valor = self._aplicar_cupom(cupom, valor)

        self._contador_transacao += 1
        transacao_id = f"TXN-{datetime.now().strftime('%Y%m%d')}-{self._contador_transacao:06d}"

        # Criar transação
        transacao = Transacao(
            id=transacao_id,
            tipo_produto=TipoProduto.PARECER_CLIENTE,
            valor=valor,
            metodo_pagamento=metodo,
            status=StatusPagamento.PENDENTE,
            usuario_id=usuario_id,
            usuario_email=usuario_email,
            referencia_id=parecer_id,
            dados_cartao=dados_cartao
        )

        # Gerar dados de pagamento conforme método
        if metodo == MetodoPagamento.PIX:
            transacao.dados_pix = self._gerar_pix(valor)
            transacao.data_vencimento = (datetime.now() + timedelta(minutes=30)).isoformat()

        elif metodo == MetodoPagamento.BOLETO:
            transacao.dados_boleto = self._gerar_boleto(valor)
            transacao.data_vencimento = (datetime.now() + timedelta(days=3)).isoformat()

        elif metodo in [MetodoPagamento.CARTAO_CREDITO, MetodoPagamento.CARTAO_DEBITO]:
            # Em produção, processar com gateway
            if self.modo_producao:
                resultado = self._processar_cartao_gateway(transacao)
                transacao.status = resultado['status']
                transacao.gateway_id = resultado['gateway_id']
            else:
                # Modo demo: aprovar automaticamente
                transacao.status = StatusPagamento.APROVADO
                transacao.data_aprovacao = datetime.now().isoformat()
                transacao.gateway_id = f"DEMO-{secrets.token_hex(8)}"

        self._transacoes[transacao_id] = transacao
        return transacao

    def confirmar_pagamento_pix(self, transacao_id: str) -> bool:
        """Webhook: confirma pagamento PIX"""

        if transacao_id not in self._transacoes:
            return False

        txn = self._transacoes[transacao_id]

        if txn.metodo_pagamento != MetodoPagamento.PIX:
            return False

        txn.status = StatusPagamento.APROVADO
        txn.data_aprovacao = datetime.now().isoformat()

        return True

    def confirmar_pagamento_boleto(self, transacao_id: str) -> bool:
        """Webhook: confirma pagamento de boleto"""

        if transacao_id not in self._transacoes:
            return False

        txn = self._transacoes[transacao_id]

        if txn.metodo_pagamento != MetodoPagamento.BOLETO:
            return False

        txn.status = StatusPagamento.APROVADO
        txn.data_aprovacao = datetime.now().isoformat()

        return True

    # =====================================================
    # ASSINATURAS (ADVOGADOS)
    # =====================================================

    def criar_assinatura_advogado(
        self,
        usuario_id: str,
        tipo_plano: TipoProduto,
        metodo: MetodoPagamento,
        dados_cartao: Optional[DadosCartao] = None
    ) -> Assinatura:
        """Cria assinatura mensal para advogado"""

        if tipo_plano not in [
            TipoProduto.ASSINATURA_ADVOGADO_BASICO,
            TipoProduto.ASSINATURA_ADVOGADO_PROFISSIONAL,
            TipoProduto.ASSINATURA_ADVOGADO_PREMIUM
        ]:
            raise ValueError("Tipo de plano inválido")

        self._contador_assinatura += 1
        assinatura_id = f"SUB-{self._contador_assinatura:06d}"

        valor = self._precos[tipo_plano]

        assinatura = Assinatura(
            id=assinatura_id,
            usuario_id=usuario_id,
            tipo_produto=tipo_plano,
            valor_mensal=valor,
            metodo_pagamento=metodo,
            status=StatusAssinatura.ATIVA,
            data_inicio=datetime.now().isoformat(),
            data_proxima_cobranca=(datetime.now() + timedelta(days=30)).isoformat(),
            dados_cartao=dados_cartao
        )

        # Criar primeira cobrança
        primeira_cobranca = self._cobrar_assinatura(assinatura)

        if primeira_cobranca.status == StatusPagamento.APROVADO:
            assinatura.pagamentos.append(primeira_cobranca.id)
            self._assinaturas[assinatura_id] = assinatura
            return assinatura
        else:
            # Primeira cobrança falhou
            assinatura.status = StatusAssinatura.SUSPENSA
            self._assinaturas[assinatura_id] = assinatura
            return assinatura

    def _cobrar_assinatura(self, assinatura: Assinatura) -> Transacao:
        """Realiza cobrança da assinatura"""

        self._contador_transacao += 1
        transacao_id = f"TXN-{datetime.now().strftime('%Y%m%d')}-{self._contador_transacao:06d}"

        transacao = Transacao(
            id=transacao_id,
            tipo_produto=assinatura.tipo_produto,
            valor=assinatura.valor_mensal,
            metodo_pagamento=assinatura.metodo_pagamento,
            status=StatusPagamento.PROCESSANDO,
            usuario_id=assinatura.usuario_id,
            usuario_email=f"{assinatura.usuario_id}@email.com",
            referencia_id=assinatura.id,
            dados_cartao=assinatura.dados_cartao
        )

        # Processar com gateway
        if self.modo_producao:
            resultado = self._processar_cartao_gateway(transacao)
            transacao.status = resultado['status']
        else:
            # Demo: aprovar
            transacao.status = StatusPagamento.APROVADO
            transacao.data_aprovacao = datetime.now().isoformat()

        self._transacoes[transacao_id] = transacao
        return transacao

    def processar_renovacoes(self) -> List[Dict]:
        """Processa renovações de assinaturas (executar diariamente via CRON)"""

        hoje = datetime.now()
        renovacoes = []

        for assinatura in self._assinaturas.values():
            if assinatura.status != StatusAssinatura.ATIVA:
                continue

            data_proxima = datetime.fromisoformat(assinatura.data_proxima_cobranca)

            # Chegou a data de renovação?
            if data_proxima.date() <= hoje.date():
                # Cobrar
                transacao = self._cobrar_assinatura(assinatura)

                if transacao.status == StatusPagamento.APROVADO:
                    assinatura.pagamentos.append(transacao.id)
                    assinatura.data_proxima_cobranca = (hoje + timedelta(days=30)).isoformat()
                    renovacoes.append({
                        "assinatura_id": assinatura.id,
                        "usuario_id": assinatura.usuario_id,
                        "status": "sucesso",
                        "transacao_id": transacao.id
                    })
                else:
                    # Falha na cobrança
                    assinatura.status = StatusAssinatura.SUSPENSA
                    renovacoes.append({
                        "assinatura_id": assinatura.id,
                        "usuario_id": assinatura.usuario_id,
                        "status": "falha",
                        "transacao_id": transacao.id
                    })

        return renovacoes

    def cancelar_assinatura(self, assinatura_id: str) -> bool:
        """Cancela assinatura"""

        if assinatura_id not in self._assinaturas:
            return False

        assinatura = self._assinaturas[assinatura_id]
        assinatura.status = StatusAssinatura.CANCELADA
        assinatura.data_cancelamento = datetime.now().isoformat()

        return True

    def atualizar_plano_assinatura(
        self,
        assinatura_id: str,
        novo_tipo: TipoProduto
    ) -> bool:
        """Atualiza plano da assinatura (upgrade/downgrade)"""

        if assinatura_id not in self._assinaturas:
            return False

        assinatura = self._assinaturas[assinatura_id]
        assinatura.tipo_produto = novo_tipo
        assinatura.valor_mensal = self._precos[novo_tipo]

        return True

    # =====================================================
    # CUPONS
    # =====================================================

    def criar_cupom(
        self,
        codigo: str,
        desconto_percentual: Optional[float] = None,
        desconto_fixo: Optional[float] = None,
        valido_ate: Optional[str] = None,
        usos_maximos: Optional[int] = None
    ) -> Cupom:
        """Cria cupom de desconto"""

        cupom = Cupom(
            codigo=codigo.upper(),
            desconto_percentual=desconto_percentual,
            desconto_fixo=desconto_fixo,
            valido_ate=valido_ate,
            usos_maximos=usos_maximos
        )

        self._cupons[cupom.codigo] = cupom
        return cupom

    def _aplicar_cupom(self, codigo: str, valor: float) -> float:
        """Aplica cupom e retorna valor com desconto"""

        if codigo not in self._cupons:
            return valor

        cupom = self._cupons[codigo]

        # Verificar validade
        if not cupom.ativo:
            return valor

        if cupom.valido_ate:
            if datetime.now() > datetime.fromisoformat(cupom.valido_ate):
                return valor

        if cupom.usos_maximos and cupom.usos_atuais >= cupom.usos_maximos:
            return valor

        # Aplicar desconto
        if cupom.desconto_fixo:
            valor = max(0, valor - cupom.desconto_fixo)
        elif cupom.desconto_percentual:
            valor = valor * (1 - cupom.desconto_percentual / 100)

        cupom.usos_atuais += 1

        return valor

    # =====================================================
    # CONSULTAS
    # =====================================================

    def obter_transacao(self, transacao_id: str) -> Optional[Transacao]:
        """Obtém transação pelo ID"""
        return self._transacoes.get(transacao_id)

    def obter_assinatura(self, assinatura_id: str) -> Optional[Assinatura]:
        """Obtém assinatura pelo ID"""
        return self._assinaturas.get(assinatura_id)

    def listar_transacoes_usuario(self, usuario_id: str) -> List[Transacao]:
        """Lista transações de um usuário"""
        return [
            t for t in self._transacoes.values()
            if t.usuario_id == usuario_id
        ]

    def obter_extrato_assinatura(self, assinatura_id: str) -> Optional[Dict]:
        """Obtém extrato completo de uma assinatura"""

        if assinatura_id not in self._assinaturas:
            return None

        assinatura = self._assinaturas[assinatura_id]

        # Buscar todas as transações
        pagamentos = [
            self._transacoes[tid] for tid in assinatura.pagamentos
            if tid in self._transacoes
        ]

        return {
            "assinatura": assinatura,
            "pagamentos": pagamentos,
            "total_pago": sum(p.valor for p in pagamentos if p.status == StatusPagamento.APROVADO),
            "proxima_cobranca": assinatura.data_proxima_cobranca
        }

    # =====================================================
    # GATEWAY (SIMULADO)
    # =====================================================

    def _gerar_pix(self, valor: float) -> DadosPix:
        """Gera dados PIX (simulado)"""
        hash_valor = hashlib.md5(f"{valor}{datetime.now()}".encode()).hexdigest()

        return DadosPix(
            qr_code=f"00020126{hash_valor}",
            chave_pix="pagamentos@doutorai.com.br",
            validade_minutos=30
        )

    def _gerar_boleto(self, valor: float) -> DadosBoleto:
        """Gera boleto (simulado)"""
        codigo = secrets.token_hex(22)

        return DadosBoleto(
            codigo_barras=codigo,
            linha_digitavel=f"{codigo[:5]}.{codigo[5:10]} {codigo[10:15]}.{codigo[15:]}",
            url_pdf=f"https://api.doutorai.com.br/boletos/{codigo}.pdf",
            data_vencimento=(datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        )

    def _processar_cartao_gateway(self, transacao: Transacao) -> Dict:
        """Processa cartão via gateway (em produção: Mercado Pago ou Stripe)"""

        # Em produção, fazer request para API do gateway
        # Aqui retornamos simulação

        return {
            "status": StatusPagamento.APROVADO,
            "gateway_id": f"MP-{secrets.token_hex(10)}",
            "mensagem": "Pagamento aprovado"
        }

    def _criar_cupons_demo(self):
        """Cria cupons de demonstração"""

        # Cupom de lançamento
        self.criar_cupom(
            codigo="LANCAMENTO",
            desconto_percentual=50,
            valido_ate=(datetime.now() + timedelta(days=30)).isoformat(),
            usos_maximos=100
        )

        # Cupom fixo
        self.criar_cupom(
            codigo="PRIMEIRACOMPRA",
            desconto_fixo=3.50,  # R$ 7,00 - R$ 3,50 = R$ 3,50
            usos_maximos=1000
        )


# =====================================================
# FACTORY
# =====================================================

def criar_engine_pagamentos(producao: bool = False) -> EnginePagamentos:
    """Factory para criar engine de pagamentos"""
    return EnginePagamentos(modo_producao=producao)


# =====================================================
# TESTE
# =====================================================

if __name__ == "__main__":
    engine = criar_engine_pagamentos(producao=False)

    print("=== ENGINE DE PAGAMENTOS ===")

    # Teste 1: Pagamento de parecer com PIX
    print("\n1. PAGAMENTO PARECER (PIX)")
    txn_pix = engine.criar_pagamento_parecer(
        usuario_id="USR-001",
        usuario_email="cliente@email.com",
        parecer_id="PAR-202512-01001",
        metodo=MetodoPagamento.PIX
    )

    print(f"Transação: {txn_pix.id}")
    print(f"Valor: R$ {txn_pix.valor:.2f}")
    print(f"Status: {txn_pix.status.value}")
    if txn_pix.dados_pix:
        print(f"Chave PIX: {txn_pix.dados_pix.chave_pix}")
        print(f"QR Code: {txn_pix.dados_pix.qr_code[:30]}...")

    # Simular pagamento PIX
    engine.confirmar_pagamento_pix(txn_pix.id)
    print(f"Status após confirmação: {txn_pix.status.value}")

    # Teste 2: Pagamento de parecer com cupom
    print("\n2. PAGAMENTO PARECER COM CUPOM")
    txn_cupom = engine.criar_pagamento_parecer(
        usuario_id="USR-002",
        usuario_email="cliente2@email.com",
        parecer_id="PAR-202512-01002",
        metodo=MetodoPagamento.CARTAO_CREDITO,
        cupom="LANCAMENTO",
        dados_cartao=DadosCartao(
            numero_mascarado="**** **** **** 1234",
            nome_titular="MARIA SILVA",
            validade_mes=12,
            validade_ano=2027
        )
    )

    print(f"Valor original: R$ 7,00")
    print(f"Valor com desconto: R$ {txn_cupom.valor:.2f}")
    print(f"Status: {txn_cupom.status.value}")

    # Teste 3: Assinatura de advogado
    print("\n3. ASSINATURA ADVOGADO (PLANO PREMIUM)")
    assinatura = engine.criar_assinatura_advogado(
        usuario_id="ADV-001",
        tipo_plano=TipoProduto.ASSINATURA_ADVOGADO_PREMIUM,
        metodo=MetodoPagamento.CARTAO_CREDITO,
        dados_cartao=DadosCartao(
            numero_mascarado="**** **** **** 5678",
            nome_titular="JOAO SILVA",
            validade_mes=6,
            validade_ano=2028
        )
    )

    print(f"Assinatura: {assinatura.id}")
    print(f"Plano: {assinatura.tipo_produto.value}")
    print(f"Valor mensal: R$ {assinatura.valor_mensal:.2f}")
    print(f"Status: {assinatura.status.value}")
    print(f"Próxima cobrança: {assinatura.data_proxima_cobranca[:10]}")

    # Extrato
    extrato = engine.obter_extrato_assinatura(assinatura.id)
    print(f"Total pago até agora: R$ {extrato['total_pago']:.2f}")
    print(f"Cobranças realizadas: {len(extrato['pagamentos'])}")

    print("\n✅ Engine de Pagamentos funcionando!")
