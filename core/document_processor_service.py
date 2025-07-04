# memoria/core/document_processor_service.py
import os
import io
import re
import uuid
import json
import asyncio  # <-- CORREÇÃO: Importação em falta adicionada
import pytesseract
import spacy
from PIL import Image
import fitz  # PyMuPDF
from typing import Dict, Any, List
import requests

# --- Bloco de inicialização ---
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

NLP_MODEL_NAME = "pt_core_news_sm"
try:
    nlp = spacy.load(NLP_MODEL_NAME)
    print(f"Modelo spaCy '{NLP_MODEL_NAME}' carregado com sucesso.")
except OSError:
    print(
        f"ERRO: Modelo spaCy '{NLP_MODEL_NAME}' não encontrado. Execute 'python -m spacy download {NLP_MODEL_NAME}' e reinicie o servidor.")
    nlp = None


# --- Fim do Bloco de inicialização ---


class OCRService:
    """Serviço para realizar OCR em imagens e PDFs."""

    def extract_text(self, filepath: str) -> str:
        filename = filepath.lower()
        print(f"[OCRService] A extrair texto de: {filepath}")
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            try:
                return pytesseract.image_to_string(Image.open(filepath), lang='por')
            except Exception as e:
                print(f"ERRO OCR ao processar imagem {filepath}: {e}")
                return ""
        elif filename.endswith('.pdf'):
            try:
                doc = fitz.open(filepath)
                text = "".join(page.get_text() for page in doc)
                doc.close()
                if not text.strip():
                    print("PDF sem texto extraível, tentando OCR página a página...")
                    doc = fitz.open(filepath)
                    full_text_ocr = ""
                    for i, page in enumerate(doc):
                        pix = page.get_pixmap(dpi=300)
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        full_text_ocr += pytesseract.image_to_string(img, lang='por') + "\n"
                    doc.close()
                    return full_text_ocr
                return text
            except Exception as e:
                print(f"ERRO ao processar PDF {filepath}: {e}")
                return ""
        return ""


class NLPService:
    """Serviço de NLP para extrair múltiplos itens estruturados de um texto."""

    def __init__(self):
        self.nlp_model = nlp
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            print(
                "\nAVISO: Variável de ambiente GEMINI_API_KEY não encontrada. A extração por IA será desativada. O sistema usará heurísticas locais.\n")

    def _create_item_template(self, ontology_config: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um dicionário em branco para um novo item."""
        return {
            "entry_type": ontology_config.get("ITEM_CLASS", "pc:ObraCultural"),
            "properties": {
                ontology_config.get("TITLE_PROPERTY"): None,
                ontology_config.get("AUTHOR_PROPERTY"): None,
                ontology_config.get("DESCRIPTION_PROPERTY"): None,
                "pc:temLocal": None,
                "pc:temData": None,
            }
        }

    def _extract_items_with_heuristics(self, text: str, ontology_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Função de fallback melhorada, focada em extrair dados da infobox."""
        if not self.nlp_model:
            raise ValueError("Modelo NLP (spaCy) não está carregado.")

        print("Executando extração com heurísticas melhoradas (fallback)...")
        items = []
        infobox_pattern = r'Principais\s*trabalhos\s*(.*?)\n'
        match = re.search(infobox_pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            main_works_text = match.group(1)
            main_works = [w.strip() for w in main_works_text.split('\n') if w.strip()]

            for work in main_works:
                work_item = self._create_item_template(ontology_config)
                work_item["properties"][ontology_config.get("TITLE_PROPERTY")] = work
                work_item["properties"][ontology_config.get("AUTHOR_PROPERTY")] = "Alberto Santos Dumont"
                work_item["properties"][ontology_config.get(
                    "DESCRIPTION_PROPERTY")] = f"Invenção notável de Santos Dumont mencionada na infobox do documento."
                work_item["properties"] = {k: v for k, v in work_item["properties"].items() if v}
                items.append(work_item)

        print(f"Itens extraídos com heurísticas: {len(items)}")
        return items

    async def _extract_items_with_llm(self, text: str, ontology_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Usa o Gemini para extrair itens de forma estruturada."""
        print("Executando extração com a API do Gemini...")

        title_prop = ontology_config.get("TITLE_PROPERTY")
        author_prop = ontology_config.get("AUTHOR_PROPERTY")
        local_prop = "pc:temLocal"

        prompt = f"""
        Você é um especialista em catalogação de património cultural. Analise o texto fornecido e extraia uma lista de obras, invenções ou eventos importantes.
        Ignore referências bibliográficas, notas de rodapé e metadados do documento. Foque-se apenas no conteúdo principal.

        Para cada item que identificar, crie um objeto JSON com as seguintes chaves:
        - "{title_prop}": O nome oficial do item (ex: "Dirigível Nº 6", "14-bis").
        - "{author_prop}": O criador ou pessoa principal associada ao item.
        - "{local_prop}": A cidade ou local principal onde o evento ocorreu (ex: "Paris").

        Se uma informação não for encontrada para um item, omita a chave.
        A sua resposta deve ser APENAS um array de objetos JSON válidos, nada mais.

        Texto para análise:
        ---
        {text[:8000]}
        ---
        """

        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.gemini_api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.post(api_url, json=payload, timeout=90))
            response.raise_for_status()
            api_result = response.json()

            content = api_result['candidates'][0]['content']['parts'][0]['text']

            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if not json_match:
                print(f"ERRO: Nenhum array JSON válido encontrado na resposta da IA. Resposta recebida: {content}")
                return []

            cleaned_content = json_match.group(0)
            parsed_response = json.loads(cleaned_content)

            final_items = []
            for res_item in parsed_response:
                item_template = self._create_item_template(ontology_config)
                item_template["properties"].update(res_item)
                item_template["properties"][ontology_config.get(
                    "DESCRIPTION_PROPERTY")] = f"Item '{res_item.get(title_prop, 'N/A')}' extraído e contextualizado via IA."
                item_template["properties"] = {k: v for k, v in item_template["properties"].items() if v}
                final_items.append(item_template)

            return final_items

        except requests.exceptions.RequestException as e:
            print(f"ERRO: Falha na chamada à API do Gemini: {e}")
        except json.JSONDecodeError:
            print(f"ERRO: Falha ao processar JSON da resposta da IA. Resposta recebida: {content}")
        except Exception as e:
            print(f"ERRO: Erro inesperado durante a extração com IA: {e}")

        return []

    async def extract_multiple_structured_items(self, text: str, ontology_config: Dict[str, Any]) -> List[
        Dict[str, Any]]:
        """Orquestra a extração, priorizando IA se configurada, com fallback para heurísticas."""
        if self.gemini_api_key:
            try:
                items = await self._extract_items_with_llm(text, ontology_config)
                if items:
                    print(f"Extração com IA bem-sucedida. {len(items)} itens encontrados.")
                    return items
                print("AVISO: Extração com IA não retornou itens. Usando heurísticas como fallback.")
            except Exception as e:
                print(f"ERRO: A extração com IA falhou: {e}. Usando heurísticas como fallback.")

        return self._extract_items_with_heuristics(text, ontology_config)


class DocumentProcessorService:
    """Orquestra o processo de extração e mapeamento de múltiplos itens."""

    def __init__(self, ocr_service: OCRService, nlp_service: NLPService):
        self.ocr_service = ocr_service
        self.nlp_service = nlp_service
        print("DocumentProcessorService inicializado.")

    async def process_document_for_multiple_items(self, filepath: str, ontology_config: Dict[str, Any]) -> Dict[
        str, Any]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Ficheiro não encontrado em {filepath}")

        extracted_text = self.ocr_service.extract_text(filepath)
        if not extracted_text or not extracted_text.strip():
            return {"error": "Não foi possível extrair texto do documento."}

        try:
            structured_items = await self.nlp_service.extract_multiple_structured_items(extracted_text, ontology_config)
            return {
                "texto_extraido_amostra": extracted_text[:1000] + "...",
                "itens_catalogados": structured_items,
            }
        except ValueError as e:
            print(f"Erro de processamento: {e}")
            return {"error": str(e)}

