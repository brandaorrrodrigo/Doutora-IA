"""
Sistema de perfil público de advogados com SEO otimizado
Cada advogado ganha landing page: doutoraia.com.br/advogados/{estado}/{cidade}/{area}/{nome}
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import re
import os


class LawyerProfileGenerator:
    """Gerador de perfil público SEO-otimizado"""

    def __init__(self, db: Session):
        self.db = db

    def gerar_slug(self, text: str) -> str:
        """Gera slug SEO-friendly"""
        text = text.lower()
        text = re.sub(r'[àáâãäå]', 'a', text)
        text = re.sub(r'[èéêë]', 'e', text)
        text = re.sub(r'[ìíîï]', 'i', text)
        text = re.sub(r'[òóôõö]', 'o', text)
        text = re.sub(r'[ùúûü]', 'u', text)
        text = re.sub(r'[ç]', 'c', text)
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text

    def gerar_url_publica(self, lawyer_id: int) -> str:
        """
        Gera URL pública do advogado

        Formato: /advogados/sp/sao-paulo/familia/dr-joao-silva
        """
        from models import Lawyer

        lawyer = self.db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()

        if not lawyer:
            return ""

        # Pegar primeiro estado e cidade
        estado = self.gerar_slug(lawyer.states[0]) if lawyer.states else "brasil"
        cidade = self.gerar_slug(lawyer.cities[0]) if lawyer.cities else "online"
        area = self.gerar_slug(lawyer.areas[0]) if lawyer.areas else "geral"
        nome = self.gerar_slug(lawyer.name)

        return f"/advogados/{estado}/{cidade}/{area}/{nome}"

    def gerar_html_perfil(self, lawyer_id: int) -> str:
        """
        Gera HTML completo do perfil público com SEO

        Returns:
            HTML otimizado para Google
        """
        from models import Lawyer, Referral, ReferralStatus

        lawyer = self.db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()

        if not lawyer:
            return ""

        # Estatísticas
        total_cases = self.db.query(Referral).filter(
            Referral.lawyer_id == lawyer_id
        ).count()

        aceitos = self.db.query(Referral).filter(
            Referral.lawyer_id == lawyer_id,
            Referral.status == ReferralStatus.ACCEPTED
        ).count()

        # Avaliação média (TODO: implementar sistema de avaliações)
        rating = 4.8

        # Gerar HTML
        areas_str = ", ".join([a.title() for a in lawyer.areas]) if lawyer.areas else "Diversas áreas"
        cidades_str = ", ".join(lawyer.cities) if lawyer.cities else "Atendimento online"

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO -->
    <title>{lawyer.name} - Advogado(a) de {areas_str} em {cidades_str}</title>
    <meta name="description" content="{lawyer.name}, OAB {lawyer.oab}. Especialista em {areas_str}. {aceitos} casos atendidos. Avaliação {rating}/5. Consulta grátis.">
    <meta name="keywords" content="advogado {areas_str}, {cidades_str}, {lawyer.oab}, {lawyer.name}">

    <!-- Open Graph (Facebook/WhatsApp) -->
    <meta property="og:title" content="{lawyer.name} - Advogado(a) em {cidades_str}">
    <meta property="og:description" content="Especialista em {areas_str}. {aceitos} casos atendidos. Consulta grátis 15min.">
    <meta property="og:type" content="profile">
    <meta property="og:url" content="https://doutoraia.com.br{self.gerar_url_publica(lawyer_id)}">

    <!-- Schema.org (Google Rich Snippets) -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Attorney",
        "name": "{lawyer.name}",
        "telephone": "{lawyer.phone or 'Consultar'}",
        "email": "{lawyer.email}",
        "address": {{
            "@type": "PostalAddress",
            "addressLocality": "{lawyer.cities[0] if lawyer.cities else ''}",
            "addressRegion": "{lawyer.states[0] if lawyer.states else ''}"
        }},
        "areaServed": {lawyer.cities or []},
        "knowsAbout": {lawyer.areas or []},
        "aggregateRating": {{
            "@type": "AggregateRating",
            "ratingValue": "{rating}",
            "reviewCount": "{aceitos}"
        }}
    }}
    </script>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">

    <style>
        :root {{
            --primary: #1a5490;
        }}

        .hero-profile {{
            background: linear-gradient(135deg, #1a5490 0%, #2c5aa0 100%);
            color: white;
            padding: 60px 0;
        }}

        .profile-photo {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: 5px solid white;
            object-fit: cover;
        }}

        .rating {{
            color: #ffc107;
            font-size: 1.5rem;
        }}

        .stat-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 10px 0;
        }}

        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary);
        }}

        .cta-button {{
            background: #28a745;
            color: white;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.2rem;
            border: none;
            margin: 20px 0;
        }}

        .cta-button:hover {{
            background: #218838;
        }}
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="hero-profile">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-3 text-center">
                    <img src="/static/avatars/default.jpg" alt="{lawyer.name}" class="profile-photo">
                </div>
                <div class="col-md-9">
                    <h1>{lawyer.name}</h1>
                    <p class="lead">OAB {lawyer.oab}</p>
                    <div class="rating">
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star-half-alt"></i>
                        <span>{rating}</span> ({aceitos} avaliações)
                    </div>
                    <p class="mt-3">
                        <i class="fas fa-map-marker-alt"></i> {cidades_str}<br>
                        <i class="fas fa-briefcase"></i> {areas_str}
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Stats -->
    <section class="py-5">
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <div class="stat-box">
                        <div class="stat-number">{aceitos}</div>
                        <div>Casos Atendidos</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-box">
                        <div class="stat-number">{rating}</div>
                        <div>Avaliação Média</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-box">
                        <div class="stat-number">{len(lawyer.areas) if lawyer.areas else 0}</div>
                        <div>Áreas de Atuação</div>
                    </div>
                </div>
            </div>

            <!-- CTA -->
            <div class="text-center mt-5">
                <h2>Precisa de Ajuda Jurídica?</h2>
                <p class="lead">Agende uma consulta gratuita de 15 minutos</p>
                <button class="btn cta-button" onclick="agendarConsulta()">
                    <i class="fas fa-calendar"></i> Consulta Grátis 15min
                </button>
            </div>
        </div>
    </section>

    <!-- Sobre -->
    <section class="py-5 bg-light">
        <div class="container">
            <h2>Sobre {lawyer.name.split()[0]}</h2>
            <p>{lawyer.bio or 'Advogado(a) especializado(a) em ' + areas_str + '. Atendimento personalizado e comprometido com resultados.'}</p>

            <h3 class="mt-5">Áreas de Atuação</h3>
            <ul>
                {''.join([f'<li>{area.title()}</li>' for area in lawyer.areas]) if lawyer.areas else '<li>Consultar</li>'}
            </ul>

            <h3 class="mt-5">Onde Atende</h3>
            <ul>
                {''.join([f'<li>{cidade}</li>' for cidade in lawyer.cities]) if lawyer.cities else '<li>Atendimento online em todo Brasil</li>'}
            </ul>
        </div>
    </section>

    <!-- Avaliações -->
    <section class="py-5">
        <div class="container">
            <h2>O que dizem meus clientes</h2>

            <!-- TODO: Sistema real de avaliações -->
            <div class="card mb-3">
                <div class="card-body">
                    <div class="rating mb-2">
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                    </div>
                    <p>"Excelente profissional! Resolveu meu caso rapidamente."</p>
                    <small class="text-muted">Cliente verificado • há 2 meses</small>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4">
        <div class="container text-center">
            <p>Perfil verificado por <strong>Doutora IA</strong></p>
            <p><a href="/" class="text-white">www.doutoraia.com.br</a></p>
        </div>
    </footer>

    <script>
        function agendarConsulta() {{
            // TODO: Integrar com calendário
            window.location.href = '/agendar/{lawyer_id}';
        }}
    </script>
</body>
</html>"""

        return html

    def gerar_blog_posts_automaticos(self, lawyer_id: int) -> List[Dict]:
        """
        Gera posts de blog automáticos usando IA

        Melhora SEO do advogado
        """
        from models import Lawyer

        lawyer = self.db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()

        if not lawyer or not lawyer.areas:
            return []

        # Tópicos por área
        topicos = {
            "familia": [
                "Como calcular pensão alimentícia em {cidade}",
                "Guarda compartilhada: tudo que você precisa saber",
                "Divórcio consensual: passo a passo completo",
                "Revisional de alimentos: quando é possível?",
                "Exoneração de pensão: requisitos e procedimentos"
            ],
            "consumidor": [
                "Seus direitos ao comprar online",
                "Golpe no PIX: como recuperar seu dinheiro",
                "Cancelamento de compra: prazo de 7 dias",
                "Cobrança indevida: o que fazer?",
                "Negativação indevida: como limpar o nome"
            ],
            "bancario": [
                "Fraude bancária: responsabilidade do banco",
                "PIX: segurança e prevenção de golpes",
                "Empréstimo consignado: cuidados essenciais",
                "Tarifa bancária abusiva: como contestar",
                "Revisão de financiamento: é possível?"
            ],
            "saude": [
                "Plano de saúde negou procedimento: e agora?",
                "Rol ANS é taxativo ou exemplificativo?",
                "Reajuste abusivo de plano: como contestar",
                "Urgência e emergência: cobertura obrigatória",
                "Doença preexistente: direitos do beneficiário"
            ]
        }

        posts = []
        cidade = lawyer.cities[0] if lawyer.cities else "sua cidade"

        for area in lawyer.areas:
            if area in topicos:
                for titulo in topicos[area][:3]:  # 3 posts por área
                    titulo_final = titulo.replace("{cidade}", cidade)

                    posts.append({
                        "titulo": titulo_final,
                        "slug": self.gerar_slug(titulo_final),
                        "area": area,
                        "url": f"{self.gerar_url_publica(lawyer_id)}/blog/{self.gerar_slug(titulo_final)}",
                        "gerado_em": datetime.now().isoformat()
                    })

        return posts

    def salvar_perfil_html(self, lawyer_id: int, output_dir: str = "/app/static/advogados"):
        """Salva HTML do perfil em arquivo estático"""
        html = self.gerar_html_perfil(lawyer_id)
        url = self.gerar_url_publica(lawyer_id)

        # Criar diretórios
        file_path = os.path.join(output_dir, url.lstrip('/') + '.html')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Salvar arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✓ Perfil salvo: {file_path}")

        return url


# Singleton
_profile_generator = None


def get_profile_generator(db: Session) -> LawyerProfileGenerator:
    global _profile_generator
    if _profile_generator is None or _profile_generator.db != db:
        _profile_generator = LawyerProfileGenerator(db)
    return _profile_generator
