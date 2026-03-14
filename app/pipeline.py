import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
try:
    from langchain_classic.chains import RetrievalQA
except Exception:
    from langchain.chains import RetrievalQA

try:
    from langchain_core.prompts import PromptTemplate
except Exception:
    from langchain.prompts import PromptTemplate 

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
CHROMA_DIR.mkdir(exist_ok=True)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash-lite")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

_embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
_llm = None


def _get_vectorstore() -> Chroma:
    return Chroma(
        collection_name="scholarai_docs",
        embedding_function=_embeddings,
        persist_directory=str(CHROMA_DIR),
    )


def _get_llm() -> ChatGoogleGenerativeAI:
    global _llm
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it in .env")
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.2,
        )
    return _llm


def index_document(pdf_path: str, user_id: str) -> dict:
    if not user_id:
        raise ValueError("user_id is required")
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)

    for i, chunk in enumerate(chunks):
        chunk.metadata["user_id"] = user_id
        chunk.metadata["chunk_index"] = i

    vs = _get_vectorstore()
    vs.add_documents(chunks)

    return {"chunks_indexed": len(chunks)}


def ask_question(question: str, user_id: str) -> str:
    if not question.strip():
        raise ValueError("question is required")
    if not user_id:
        raise ValueError("user_id is required")

    retriever = _get_vectorstore().as_retriever(
        search_kwargs={"k": TOP_K_RESULTS, "filter": {"user_id": user_id}}
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are ScholarAI, a research assistant.\n"
            "Answer only from the context below.\n"
            "If answer is not in context, say: "
            "'I could not find this in the uploaded documents.'\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n"
            "Answer:"
        ),
    )

    qa = RetrievalQA.from_chain_type(
        llm=_get_llm(),
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False,
    )

    result = qa.invoke({"query": question})
    return result["result"]


def delete_user_data(user_id: str) -> dict:
    if not user_id:
        raise ValueError("user_id is required")
    vs = _get_vectorstore()
    vs._collection.delete(where={"user_id": user_id})
    return {"deleted": True, "user_id": user_id}