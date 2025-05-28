from fastapi import FastAPI
from backend.api import endpoints  # Import the endpoints module

app = FastAPI(title="Natural Language to Chart API")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Natural Language to Chart API"}

# Include the API router
app.include_router(endpoints.router, prefix="/api", tags=["api"])

# To run this app (from nl_to_chart_tool/backend directory):
# uvicorn main:app --reload
