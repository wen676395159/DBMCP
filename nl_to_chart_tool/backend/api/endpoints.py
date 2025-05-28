from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

# Assuming llm_service is in backend/llm/llm_service.py
from backend.llm.llm_service import get_sql_from_llm, LlmType, DEFAULT_LLM_PROVIDER, LLM_CONFIG

router = APIRouter()

class QueryRequest(BaseModel):
    natural_language_query: str
    llm_provider: Optional[LlmType] = Field(DEFAULT_LLM_PROVIDER, description="The LLM provider to use.")
    model_name: Optional[str] = Field(None, description="Specific model name for the chosen provider.")

class SqlResponse(BaseModel):
    natural_language_query: str
    llm_provider_used: LlmType
    model_used: str
    sql_query: str 
    error_message: Optional[str] = None

@router.post("/query", response_model=SqlResponse)
async def process_query(request: QueryRequest):
    chosen_llm_provider = request.llm_provider if request.llm_provider else DEFAULT_LLM_PROVIDER

    print(f"API endpoint received query: '{request.natural_language_query}' for LLM: {chosen_llm_provider}, Model: {request.model_name or 'default'}")

    actual_model_name = request.model_name
    if not actual_model_name:
        if chosen_llm_provider in LLM_CONFIG and "default_model" in LLM_CONFIG[chosen_llm_provider]:
            actual_model_name = LLM_CONFIG[chosen_llm_provider]["default_model"]
        else:
            actual_model_name = "unknown_default" 

    generated_sql = await get_sql_from_llm(
        natural_language_query=request.natural_language_query,
        llm_provider=chosen_llm_provider,
        model_name=request.model_name
    )

    final_model_used = actual_model_name # Initialize with actual_model_name
    # If final_model_used is None (shouldn't happen if actual_model_name logic is correct)
    # or if it's "unknown_default", try to set a more specific default.
    if not final_model_used or final_model_used == "unknown_default":
        if chosen_llm_provider in LLM_CONFIG:
            final_model_used = LLM_CONFIG[chosen_llm_provider]["default_model"]
        else: # Should not happen if chosen_llm_provider is valid LlmType
            final_model_used = "default"


    response_data = {
        "natural_language_query": request.natural_language_query,
        "llm_provider_used": chosen_llm_provider,
        "model_used": final_model_used,
        "sql_query": generated_sql
    }

    if generated_sql.startswith("Error:"):
        print(f"LLM processing error for query '{request.natural_language_query}': {generated_sql}")
        # As per instructions, error_message field is not populated from generated_sql here.
        # The error string itself will be in the sql_query field. SqlResponse.error_message will be None.
    else:
        print(f"Successfully generated SQL for query '{request.natural_language_query}': {generated_sql}")

    return SqlResponse(**response_data)
