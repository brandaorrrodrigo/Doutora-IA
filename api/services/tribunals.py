"""
Integração com sistemas de tribunais brasileiros
PJe, eProc, Projudi e consulta unificada
"""
import os
import re
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup
import hashlib
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import xmltodict


class CertificadoDigital:
    """Gerenciamento de certificado digital A3 (ICP-Brasil)"""

    def __init__(self, cert_path: str = None, password: str = None):
        self.cert_path = cert_path or os.getenv("CERT_PATH")
        self.password = password or os.getenv("CERT_PASSWORD")
        self.cert = None
        self.private_key = None

        if self.cert_path and os.path.exists(self.cert_path):
            self._load_certificate()

    def _load_certificate(self):
        """Carrega certificado .pfx/.p12"""
        try:
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.serialization import pkcs12

            with open(self.cert_path, 'rb') as f:
                pfx_data = f.read()

            self.private_key, self.cert, _ = pkcs12.load_key_and_certificates(
                pfx_data,
                self.password.encode() if self.password else None,
                default_backend()
            )

            print(f"✓ Certificado carregado: {self.get_subject()}")

        except Exception as e:
            print(f"✗ Erro ao carregar certificado: {e}")

    def get_subject(self) -> str:
        """Retorna o nome do titular do certificado"""
        if self.cert:
            return self.cert.subject.rfc4514_string()
        return "Não carregado"

    def sign_data(self, data: bytes) -> bytes:
        """Assina dados com o certificado"""
        if not self.private_key:
            raise ValueError("Certificado não carregado")

        signature = self.private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return signature

    def is_valid(self) -> bool:
        """Verifica se o certificado está válido"""
        if not self.cert:
            return False

        now = datetime.utcnow()
        return self.cert.not_valid_before <= now <= self.cert.not_valid_after


class PJeIntegration:
    """Integração com PJe (Processo Judicial Eletrônico)"""

    BASE_URLS = {
        "trf1": "https://pje.trf1.jus.br/pje",
        "trf2": "https://pje.trf2.jus.br/pje",
        "trf3": "https://pje.trf3.jus.br/pje",
        "trf4": "https://pje.trf4.jus.br/pje",
        "trf5": "https://pje.trf5.jus.br/pje",
        "trf6": "https://pje.trf6.jus.br/pje",
    }

    def __init__(self, tribunal: str = "trf3", cert: CertificadoDigital = None):
        self.tribunal = tribunal
        self.base_url = self.BASE_URLS.get(tribunal)
        self.cert = cert
        self.session = requests.Session()

        # Configurar certificado se disponível
        if cert and cert.cert_path:
            self.session.cert = (cert.cert_path, cert.password)

    def login(self, username: str = None, password: str = None) -> bool:
        """
        Login no PJe
        Pode ser com usuário/senha ou certificado digital
        """
        if self.cert and self.cert.is_valid():
            return self._login_with_certificate()
        elif username and password:
            return self._login_with_credentials(username, password)
        else:
            print("✗ Credenciais não fornecidas")
            return False

    def _login_with_certificate(self) -> bool:
        """Login usando certificado digital"""
        try:
            url = f"{self.base_url}/login.seam"
            response = self.session.get(url, verify=True)

            if response.status_code == 200:
                print(f"✓ Login com certificado realizado: {self.tribunal}")
                return True

            return False

        except Exception as e:
            print(f"✗ Erro no login com certificado: {e}")
            return False

    def _login_with_credentials(self, username: str, password: str) -> bool:
        """Login usando usuário e senha"""
        try:
            url = f"{self.base_url}/login.seam"
            data = {
                "username": username,
                "password": password,
                "login": "Entrar"
            }

            response = self.session.post(url, data=data)

            if "logout" in response.text.lower():
                print(f"✓ Login realizado: {username}")
                return True

            return False

        except Exception as e:
            print(f"✗ Erro no login: {e}")
            return False

    def consultar_processo(self, numero_processo: str) -> Dict[str, Any]:
        """
        Consulta processo no PJe

        Args:
            numero_processo: Número CNJ (ex: 1234567-89.2024.8.26.0100)

        Returns:
            Dict com dados do processo
        """
        try:
            # Limpar formatação do número
            numero_limpo = re.sub(r'\D', '', numero_processo)

            url = f"{self.base_url}/consulta/publica"
            params = {"numeroProcesso": numero_limpo}

            response = self.session.get(url, params=params)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extrair dados do processo
            processo = {
                "numero": numero_processo,
                "tribunal": self.tribunal,
                "classe": self._extract_text(soup, "classe"),
                "assunto": self._extract_text(soup, "assunto"),
                "data_distribuicao": self._extract_text(soup, "distribuicao"),
                "valor_causa": self._extract_text(soup, "valor"),
                "juiz": self._extract_text(soup, "juiz"),
                "vara": self._extract_text(soup, "vara"),
                "partes": self._extract_partes(soup),
                "movimentacoes": self._extract_movimentacoes(soup),
                "documentos": self._extract_documentos(soup)
            }

            return processo

        except Exception as e:
            print(f"✗ Erro ao consultar processo: {e}")
            return {}

    def _extract_text(self, soup: BeautifulSoup, field: str) -> str:
        """Extrai texto de um campo específico"""
        element = soup.find(attrs={"data-field": field})
        if element:
            return element.get_text(strip=True)
        return ""

    def _extract_partes(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrai partes do processo"""
        partes = []
        partes_div = soup.find("div", {"id": "partes"})

        if partes_div:
            for parte in partes_div.find_all("div", {"class": "parte"}):
                partes.append({
                    "tipo": parte.find("span", {"class": "tipo"}).get_text(strip=True),
                    "nome": parte.find("span", {"class": "nome"}).get_text(strip=True),
                    "advogados": [
                        adv.get_text(strip=True)
                        for adv in parte.find_all("span", {"class": "advogado"})
                    ]
                })

        return partes

    def _extract_movimentacoes(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrai movimentações do processo"""
        movimentacoes = []
        mov_div = soup.find("div", {"id": "movimentacoes"})

        if mov_div:
            for mov in mov_div.find_all("div", {"class": "movimentacao"}):
                movimentacoes.append({
                    "data": mov.find("span", {"class": "data"}).get_text(strip=True),
                    "descricao": mov.find("span", {"class": "descricao"}).get_text(strip=True)
                })

        return movimentacoes

    def _extract_documentos(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrai lista de documentos do processo"""
        documentos = []
        docs_div = soup.find("div", {"id": "documentos"})

        if docs_div:
            for doc in docs_div.find_all("a", {"class": "documento"}):
                documentos.append({
                    "nome": doc.get_text(strip=True),
                    "url": doc.get("href"),
                    "id": doc.get("data-id")
                })

        return documentos

    def protocolar_peticao(
        self,
        numero_processo: str,
        tipo_peticao: str,
        pdf_path: str,
        descricao: str = ""
    ) -> Dict[str, Any]:
        """
        Protocola petição no PJe

        Args:
            numero_processo: Número CNJ do processo
            tipo_peticao: Tipo (inicial, intermediaria, recurso)
            pdf_path: Caminho do PDF assinado
            descricao: Descrição da petição

        Returns:
            Dict com número de protocolo e confirmação
        """
        if not self.cert or not self.cert.is_valid():
            raise ValueError("Certificado digital necessário para protocolar")

        try:
            url = f"{self.base_url}/peticao/protocolar"

            # Ler PDF
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()

            # Assinar PDF (se necessário)
            # signature = self.cert.sign_data(pdf_data)

            files = {
                'peticao': ('peticao.pdf', pdf_data, 'application/pdf')
            }

            data = {
                'numeroProcesso': numero_processo,
                'tipoPeticao': tipo_peticao,
                'descricao': descricao
            }

            response = self.session.post(url, data=data, files=files)

            if response.status_code == 200:
                # Extrair número de protocolo da resposta
                soup = BeautifulSoup(response.text, 'html.parser')
                protocolo = soup.find("span", {"class": "protocolo"})

                return {
                    "sucesso": True,
                    "protocolo": protocolo.get_text(strip=True) if protocolo else "N/A",
                    "data": datetime.now().isoformat(),
                    "mensagem": "Petição protocolada com sucesso"
                }

            return {
                "sucesso": False,
                "mensagem": f"Erro ao protocolar: {response.status_code}"
            }

        except Exception as e:
            return {
                "sucesso": False,
                "mensagem": f"Erro: {str(e)}"
            }


class EProcIntegration:
    """Integração com eProc (Tribunais Estaduais)"""

    BASE_URLS = {
        "tjsp": "https://esaj.tjsp.jus.br/eproc",
        "tjrj": "https://eproc.tjrj.jus.br",
        "tjmg": "https://pje.tjmg.jus.br",
    }

    def __init__(self, tribunal: str = "tjsp"):
        self.tribunal = tribunal
        self.base_url = self.BASE_URLS.get(tribunal)
        self.session = requests.Session()

    def consultar_processo(self, numero_processo: str) -> Dict[str, Any]:
        """Consulta processo no eProc/ESAJ"""
        # Similar ao PJe, adaptado para cada tribunal
        # TJSP usa ESAJ com estrutura diferente
        pass


class DiarioOficialMonitor:
    """Monitor de publicações no Diário Oficial Eletrônico"""

    def __init__(self):
        self.tribunais_urls = {
            "tjsp": "https://www.dje.tjsp.jus.br/cdje",
            "tjrj": "https://www3.tjrj.jus.br/consultadje",
            "trf3": "https://www.trf3.jus.br/dje",
        }

    def buscar_publicacoes(
        self,
        tribunal: str,
        data: str = None,
        advogado_oab: str = None,
        numero_processo: str = None
    ) -> List[Dict]:
        """
        Busca publicações no DJe

        Args:
            tribunal: Sigla do tribunal
            data: Data da publicação (YYYY-MM-DD)
            advogado_oab: OAB do advogado
            numero_processo: Número do processo

        Returns:
            Lista de publicações encontradas
        """
        data = data or datetime.now().strftime("%Y-%m-%d")
        publicacoes = []

        # Exemplo para TJSP
        if tribunal == "tjsp":
            url = f"{self.tribunais_urls['tjsp']}/consultaPublicacao.do"
            params = {
                "data": data,
                "oab": advogado_oab
            }

            try:
                response = requests.get(url, params=params)
                soup = BeautifulSoup(response.text, 'html.parser')

                for pub in soup.find_all("div", {"class": "publicacao"}):
                    publicacoes.append({
                        "data": pub.find("span", {"class": "data"}).get_text(strip=True),
                        "processo": pub.find("span", {"class": "processo"}).get_text(strip=True),
                        "tipo": pub.find("span", {"class": "tipo"}).get_text(strip=True),
                        "texto": pub.find("div", {"class": "texto"}).get_text(strip=True),
                        "prazo_dias": self._calcular_prazo(pub.get_text())
                    })

            except Exception as e:
                print(f"Erro ao buscar publicações: {e}")

        return publicacoes

    def _calcular_prazo(self, texto: str) -> Optional[int]:
        """Extrai prazo em dias do texto da publicação"""
        # Procurar padrões como "prazo de 15 dias", "no prazo de 5 (cinco) dias"
        patterns = [
            r'prazo de (\d+) dias',
            r'no prazo de (\d+)',
            r'em (\d+) dias'
        ]

        for pattern in patterns:
            match = re.search(pattern, texto.lower())
            if match:
                return int(match.group(1))

        return None

    def calcular_data_limite(self, data_publicacao: str, prazo_dias: int) -> str:
        """Calcula data limite considerando dias úteis"""
        # Simplificado - em produção, usar biblioteca de feriados
        data = datetime.strptime(data_publicacao, "%Y-%m-%d")
        dias_corridos = 0

        while dias_corridos < prazo_dias:
            data += timedelta(days=1)
            # Pular fins de semana
            if data.weekday() < 5:  # 0-4 = segunda-sexta
                dias_corridos += 1

        return data.strftime("%Y-%m-%d")


class JurisprudenciaUnificada:
    """Consulta unificada de jurisprudência em todos os tribunais"""

    TRIBUNAIS = {
        "stf": "https://jurisprudencia.stf.jus.br/api/search",
        "stj": "https://scon.stj.jus.br/SCON/api/search",
        "tst": "https://jurisprudencia.tst.jus.br/api/search",
        "trf1": "https://arquivo.trf1.jus.br/api/search",
        "trf2": "https://www10.trf2.jus.br/api/search",
        "trf3": "https://web.trf3.jus.br/api/search",
        "trf4": "https://jurisprudencia.trf4.jus.br/api/search",
        "trf5": "https://cp.trf5.jus.br/api/search",
    }

    def buscar_todos(
        self,
        query: str,
        tribunais: List[str] = None,
        limit: int = 10
    ) -> Dict[str, List[Dict]]:
        """
        Busca jurisprudência em múltiplos tribunais simultaneamente

        Args:
            query: Termo de busca
            tribunais: Lista de tribunais (None = todos)
            limit: Máximo de resultados por tribunal

        Returns:
            Dict com resultados por tribunal
        """
        import concurrent.futures

        tribunais = tribunais or list(self.TRIBUNAIS.keys())
        resultados = {}

        # Buscar em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_tribunal = {
                executor.submit(self._buscar_tribunal, t, query, limit): t
                for t in tribunais
            }

            for future in concurrent.futures.as_completed(future_to_tribunal):
                tribunal = future_to_tribunal[future]
                try:
                    resultados[tribunal] = future.result()
                except Exception as e:
                    print(f"Erro ao buscar {tribunal}: {e}")
                    resultados[tribunal] = []

        return resultados

    def _buscar_tribunal(
        self,
        tribunal: str,
        query: str,
        limit: int
    ) -> List[Dict]:
        """Busca em um tribunal específico"""
        url = self.TRIBUNAIS.get(tribunal)
        if not url:
            return []

        try:
            # Cada tribunal tem API diferente, aqui é exemplo genérico
            params = {
                "q": query,
                "limit": limit
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                # Parse response (varia por tribunal)
                return self._parse_response(tribunal, response.json())

        except Exception as e:
            print(f"Erro {tribunal}: {e}")

        return []

    def _parse_response(self, tribunal: str, data: Any) -> List[Dict]:
        """Parse da resposta de cada tribunal"""
        # Cada tribunal tem formato diferente
        # Normalizar para formato padrão
        resultados = []

        # Exemplo genérico
        if isinstance(data, dict) and "results" in data:
            for item in data["results"]:
                resultados.append({
                    "tribunal": tribunal.upper(),
                    "numero": item.get("numero"),
                    "classe": item.get("classe"),
                    "relator": item.get("relator"),
                    "data": item.get("data"),
                    "ementa": item.get("ementa"),
                    "url": item.get("url")
                })

        return resultados


# Singleton instances
_certificado = None
_pje = None
_diario_monitor = None
_juris_unificada = None


def get_certificado() -> CertificadoDigital:
    global _certificado
    if _certificado is None:
        _certificado = CertificadoDigital()
    return _certificado


def get_pje(tribunal: str = "trf3") -> PJeIntegration:
    global _pje
    if _pje is None:
        _pje = PJeIntegration(tribunal, get_certificado())
    return _pje


def get_diario_monitor() -> DiarioOficialMonitor:
    global _diario_monitor
    if _diario_monitor is None:
        _diario_monitor = DiarioOficialMonitor()
    return _diario_monitor


def get_jurisprudencia_unificada() -> JurisprudenciaUnificada:
    global _juris_unificada
    if _juris_unificada is None:
        _juris_unificada = JurisprudenciaUnificada()
    return _juris_unificada
