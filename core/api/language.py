from fastapi import APIRouter, HTTPException, Depends
router = APIRouter()


#endpoint to get available languages
@router.get("/v1/languages")
async def get_languages():
    return {"languages": ["en", "hi", "kn", "ml"]}

