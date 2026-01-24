from docxtpl import DocxTemplate
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DocxComposer:
    def __init__(self):
        # Templates directory - now points to correct location
        self.templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'static')

        os.makedirs(self.output_dir, exist_ok=True)
    
    def compose_peca(
        self,
        tipo_peca: str,
        metadados: Dict[str, Any],
        carrinho_citacoes: List[Dict[str, Any]]
    ) -> str:
        """
        Generate legal document (peça) from template
        
        Args:
            tipo_peca: Template type (inicial_familia_alimentos, etc.)
            metadados: Document metadata (foro, vara, autor, reu, etc.)
            carrinho_citacoes: Citations selected by user
            
        Returns:
            Path to generated DOCX
        """
        template_file = f"{tipo_peca}.docx"
        template_path = os.path.join(self.templates_dir, template_file)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        # Load template
        doc = DocxTemplate(template_path)
        
        # Prepare context
        context = self._prepare_context(metadados, carrinho_citacoes)
        
        # Render
        doc.render(context)
        
        # Save
        output_filename = f"{tipo_peca}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        output_path = os.path.join(self.output_dir, output_filename)
        
        doc.save(output_path)
        logger.info(f"Generated DOCX: {output_path}")
        
        return output_path
    
    def _prepare_context(
        self,
        metadados: Dict[str, Any],
        carrinho_citacoes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare Jinja context for template rendering"""

        # Separate citations by type
        fundamentos_legais = []
        regulacao_ans = []
        jurisprudencia = []
        doutrina = []

        for cit in carrinho_citacoes:
            tipo = cit.get("tipo", "")
            formatted = {
                "titulo": cit.get("titulo", ""),
                "texto": cit.get("texto", ""),
                "tribunal": cit.get("tribunal", ""),
                "numero": cit.get("numero", ""),
                "ementa": cit.get("ementa", ""),
                "tipo": tipo,
                "orgao": cit.get("orgao", ""),
                "area": cit.get("area", "")
            }

            if tipo in ["lei", "sumula", "tema"]:
                fundamentos_legais.append(formatted)
            elif tipo == "regulatorio":
                regulacao_ans.append(formatted)
            elif tipo == "juris":
                jurisprudencia.append(formatted)
            elif tipo == "doutrina":
                doutrina.append(formatted)

        # Format date in Portuguese
        data_extenso = datetime.now().strftime("%d de %B de %Y")
        meses_pt = {
            "January": "janeiro", "February": "fevereiro", "March": "março",
            "April": "abril", "May": "maio", "June": "junho",
            "July": "julho", "August": "agosto", "September": "setembro",
            "October": "outubro", "November": "novembro", "December": "dezembro"
        }
        for en, pt in meses_pt.items():
            data_extenso = data_extenso.replace(en, pt)

        # Build comprehensive context with all template variables
        context = {
            **metadados,
            "fundamentos_legais": fundamentos_legais,
            "regulacao_ans": regulacao_ans,
            "jurisprudencia": jurisprudencia,
            "doutrina": doutrina,
            "data": data_extenso,
            "data_extenso": data_extenso,
            "data_curta": datetime.now().strftime("%d/%m/%Y"),
            # Ensure default pedidos if not provided
            "pedidos": metadados.get("pedidos", [
                "A citação da parte Ré para responder à presente ação",
                "A procedência do pedido nos termos requeridos",
                "A condenação da parte Ré ao pagamento de custas processuais e honorários advocatícios"
            ])
        }

        return context
    
    def convert_to_pdf(self, docx_path: str) -> str:
        """Convert DOCX to PDF (requires LibreOffice or similar)"""
        try:
            import subprocess
            
            pdf_path = docx_path.replace('.docx', '.pdf')
            
            # Try using LibreOffice
            subprocess.run([
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', os.path.dirname(pdf_path),
                docx_path
            ], check=True, timeout=30)
            
            if os.path.exists(pdf_path):
                logger.info(f"Converted to PDF: {pdf_path}")
                return pdf_path
            else:
                logger.warning("PDF conversion failed, returning DOCX path")
                return docx_path
                
        except Exception as e:
            logger.warning(f"Could not convert to PDF: {e}. Returning DOCX.")
            return docx_path

# Global instance
docx_composer = DocxComposer()
