from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .define import define_terms
from .extractors import extract_candidates
from .schemas import ExtractRequest, ExtractResponse

app = FastAPI(title="Hackday Acronyms NLP", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "nlp"}


@app.post("/nlp/extract", response_model=ExtractResponse)
async def nlp_extract(body: ExtractRequest) -> ExtractResponse:
    settings = get_settings()
    text = (body.text or "").strip()
    if not text:
        return ExtractResponse(candidates=[])
    candidates = extract_candidates(text, noun_phrase_min_freq=settings.noun_phrase_min_freq)
    defined = await define_terms(candidates)
    return ExtractResponse(candidates=defined)
