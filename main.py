# memoria/main.py

# Ponto de entrada principal da aplicação/API do agente com FastAPI.
import os
import sys
import shutil
import uuid
import uvicorn
import asyncio
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Body, Path, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Adicionar o diretório do projeto ao path para importações corretas
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importações de componentes
from config import ontology_config, sparql_api_config
from core.cataloger import Cataloger
from core.reference_linker import ReferenceLinker
from core.data_acquirer import DataAcquirer
from core.search_engine import SearchEngine
from core.chatbot_service import ChatbotService
from core.document_processor_service import DocumentProcessorService, OCRService, NLPService
from core.persistence_service import PersistenceService
from storage.sparql_api_client import SPARQLAPIClient

# --- Configuração FastAPI e CORS ---
app = FastAPI(
    title="MemoriA - API de Catalogação de Património Cultural",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, restrinja para o domínio do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuração de Pastas ---
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ONTOLOGY_FOLDER = ontology_config.ONTOLOGIES_DIR
ALLOWED_DOC_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
ALLOWED_ONTOLOGY_EXTENSIONS = {"owl", "ttl", "rdf", "xml", "json"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ONTOLOGY_FOLDER, exist_ok=True)

# --- Instanciação dos Serviços ---
guara_api_client = SPARQLAPIClient(
    api_base_url=sparql_api_config.API_BASE_URL,
    email=sparql_api_config.API_EMAIL,
    password=sparql_api_config.API_PASSWORD
)
persistence_service_instance = PersistenceService(guara_api_client)
reference_linker_instance = ReferenceLinker()
data_acquirer_instance = DataAcquirer()
search_engine_instance = SearchEngine()
cataloger_instance = Cataloger(
    ontology_config=ontology_config.ACTIVE_CONFIG,
    data_acquirer=data_acquirer_instance,
    reference_linker=reference_linker_instance
)
# CORREÇÃO: O ChatbotService precisa do cliente da API Guará para fazer buscas
chatbot_service_instance = ChatbotService(sparql_client=guara_api_client)
ocr_service_instance = OCRService()
nlp_service_instance = NLPService()
document_processor_instance = DocumentProcessorService(ocr_service_instance, nlp_service_instance)

# --- Evento de Startup ---
@app.on_event("startup")
async def startup_event():
    persistence_service_instance.start_worker()

# --- Modelos Pydantic ---
class CatalogItemRequest(BaseModel): item_data: Dict[str, Any]; source_info: Optional[Dict[str, Any]] = None
class CatalogItemResponse(BaseModel): status: str; message: str; item_uri_rdf: Optional[str] = None; linked_uris: List[str] = []
class SearchResponse(BaseModel): query: str; results: List[Dict[str, Any]]
class UpdateOntologyRequest(BaseModel): ontology_identifier: str
class UpdateOntologyResponse(BaseModel): status: str; message: str; active_ontology_file: Optional[str] = None; new_config_summary: Optional[Dict[str, Any]] = None
class AvailableOntologiesResponse(BaseModel): available_ontology_files: List[str]
class ChatbotRequest(BaseModel): message: str; repository_name: str; session_id: Optional[str] = None
class ChatbotResponse(BaseModel): reply: str; sources: Optional[List[Dict[str, Any]]] = None
class UploadResponse(BaseModel): filename: str; message: str
class CatalogedItem(BaseModel): entry_type: str; properties: Dict[str, Any]
class ProcessResultData(BaseModel): texto_extraido_amostra: str; itens_catalogados: List[CatalogedItem]
class DocumentProcessResponse(BaseModel): file_id: str; filename: str; status: str; data: Optional[ProcessResultData] = None; error: Optional[str] = None
class SaveRequest(BaseModel): items: List[CatalogedItem]; repository_name: str
class SaveResponse(BaseModel): task_id: str; message: str
class StatusResultItem(BaseModel): item_title: Optional[str] = None; status: str; message: str; uri: Optional[str] = None
class PersistenceStatusResponse(BaseModel): status: str; total_items: int; processed_items: int; results: List[StatusResultItem]; error: Optional[str] = None

# --- Funções Helper ---
async def save_uploaded_file_async(file: UploadFile, destination_folder: str) -> str:
    original_filename = os.path.basename(file.filename)
    safe_filename = f"{uuid.uuid4().hex}_{original_filename}"
    destination_path = os.path.join(destination_folder, safe_filename)
    with open(destination_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return safe_filename

# --- Rotas da API ---

@app.get("/api/v1/health", tags=["Status"], summary="Verifica o estado da API")
async def health_check_endpoint():
    return {"status": "ok", "message": "MemoriA API está operacional"}

@app.get("/api/v1/config/ontology", tags=["Ontologia"], summary="Obtém a configuração da ontologia ativa")
async def get_ontology_config_endpoint():
    return ontology_config.ACTIVE_CONFIG.copy()

@app.get("/api/v1/config/ontologies/available", response_model=AvailableOntologiesResponse, tags=["Ontologia"], summary="Lista os ficheiros de ontologia disponíveis")
async def list_available_ontologies():
    try:
        files = ontology_config.find_available_ontology_files(list(ALLOWED_ONTOLOGY_EXTENSIONS))
        return AvailableOntologiesResponse(available_ontology_files=files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/config/ontologies/upload", response_model=UploadResponse, tags=["Ontologia"], summary="Faz upload de um ficheiro de ontologia")
async def upload_ontology_file(ontology_file: UploadFile = File(...)):
    if not ontology_file.filename or ontology_file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_ONTOLOGY_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Tipo de ficheiro não permitido.")
    safe_filename = await save_uploaded_file_async(ontology_file, ONTOLOGY_FOLDER)
    return UploadResponse(filename=os.path.basename(ontology_file.filename), message=f"Ficheiro '{os.path.basename(ontology_file.filename)}' carregado.")

@app.put("/api/v1/config/ontology", response_model=UpdateOntologyResponse, tags=["Ontologia"], summary="Atualiza a ontologia ativa")
async def update_ontology_config_endpoint(request_data: UpdateOntologyRequest):
    global cataloger_instance
    try:
        new_config = ontology_config.load_ontology_config(request_data.ontology_identifier)
        ontology_config.ACTIVE_CONFIG = new_config
        ontology_config.update_global_config_vars()
        cataloger_instance = Cataloger(ontology_config=new_config, data_acquirer=data_acquirer_instance, reference_linker=reference_linker_instance)
        return UpdateOntologyResponse(status="sucesso", message=f"Ontologia ativa definida para '{request_data.ontology_identifier}'.", new_config_summary=new_config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/catalog", response_model=CatalogItemResponse, tags=["Catalogação"], summary="Cataloga um novo item (manual)")
async def catalog_item_endpoint(request_data: CatalogItemRequest):
    result = cataloger_instance.catalog_item(request_data.item_data, request_data.source_info)
    return CatalogItemResponse(status="sucesso", message="Item processado.", **result)

@app.get("/api/v1/search", response_model=SearchResponse, tags=["Busca"], summary="Realiza uma busca no acervo")
async def search_items_endpoint(query: str = Query(...)):
    results = search_engine_instance.search(query, ["local"])
    return SearchResponse(query=query, results=results or [])

@app.post("/api/v1/chatbot", response_model=ChatbotResponse, tags=["Chatbot"], summary="Interage com o chatbot RAG")
async def chatbot_endpoint(request_data: ChatbotRequest):
    if not request_data.repository_name:
        raise HTTPException(status_code=400, detail="O nome do repositório é obrigatório.")
    try:
        reply, sources = await chatbot_service_instance.process_message(user_message=request_data.message, repository_name=request_data.repository_name)
        return ChatbotResponse(reply=reply, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no chatbot: {e}")

@app.post("/api/v1/documents/process", response_model=DocumentProcessResponse, tags=["Documentos"], summary="Processa um documento para extração")
async def upload_and_process_document(document: UploadFile = File(...)):
    if not document.filename or document.filename.rsplit('.', 1)[1].lower() not in ALLOWED_DOC_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Tipo de ficheiro não permitido.")
    file_id = await save_uploaded_file_async(document, UPLOAD_FOLDER)
    filepath = os.path.join(UPLOAD_FOLDER, file_id)
    processed_data = await document_processor_instance.process_document_for_multiple_items(filepath, ontology_config.ACTIVE_CONFIG)
    if "error" in processed_data:
        return JSONResponse(status_code=500, content={"file_id": file_id, "filename": document.filename, "status": "error", "error": processed_data["error"]})
    return DocumentProcessResponse(file_id=file_id, filename=document.filename, status="completed", data=processed_data)

@app.get("/api/v1/repositories", response_model=List[Dict[str, Any]], tags=["Repositórios"], summary="Lista os repositórios disponíveis")
async def list_repositories_endpoint():
    repos = guara_api_client.list_repositories()
    if not repos:
        raise HTTPException(status_code=404, detail="Nenhum repositório encontrado ou falha na comunicação com a API Guará.")
    formatted_repos = []
    for r in repos:
        repo_name = r.get('nome', {}).get('value')
        repo_uri = r.get('uri', {}).get('value')
        if repo_name and repo_uri:
            dataset_name = repo_uri.split('#')[-1]
            formatted_repos.append({"name": repo_name, "dataset_id": dataset_name})
    return formatted_repos

@app.post("/api/v1/persistence/save", response_model=SaveResponse, status_code=202, tags=["Persistência"], summary="Envia itens para a fila de catalogação")
async def save_items_to_repository(request: SaveRequest):
    repo_dataset_id = request.repository_name
    repo_config = {
        "repository_update_url": f"http://localhost:3030/{repo_dataset_id}/update",
        "repository_query_url": f"http://localhost:3030/{repo_dataset_id}/query",
        "repository_base_uri": f"http://localhost:3030/{repo_dataset_id}#"
    }
    task_id = str(uuid.uuid4())
    await persistence_service_instance.add_to_queue(items=[item.dict() for item in request.items], repo_config=repo_config, task_id=task_id)
    return SaveResponse(task_id=task_id, message=f"{len(request.items)} itens adicionados à fila de processamento.")

@app.get("/api/v1/persistence/status/{task_id}", response_model=PersistenceStatusResponse, tags=["Persistência"], summary="Verifica o estado de uma tarefa")
async def get_persistence_status(task_id: str):
    status = persistence_service_instance.processing_status.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    return status

# --- Inicialização ---
if __name__ == "__main__":
    print("A iniciar o servidor FastAPI do MemoriA...")
    uvicorn.run("main:app", host="localhost", port=5080, reload=True)
