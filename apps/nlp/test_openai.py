#!/usr/bin/env python3
"""
Quick test to verify OpenAI API connection and classification response.
Run: python test_openai.py
"""
import asyncio
import json
from pathlib import Path
from app.config import get_settings
import httpx

async def test_openai():
    settings = get_settings()
    
    if not settings.openai_api_key:
        print("❌ OPENAI_API_KEY not set in .env")
        return False
    
    print(f"✓ Using API key: {settings.openai_api_key[:20]}...")
    print(f"✓ Model: {settings.openai_model}")
    
    # Test payload
    payload_terms = [
        {"term": "S3", "kind": "acronym", "context": "The S3 Bucket stores files.", "hint": ""},
        {"term": "TLR", "kind": "acronym", "context": "Before TLR we check readiness.", "hint": ""},
        {"term": "GitHub", "kind": "entity", "context": "We use GitHub for version control.", "hint": ""},
    ]
    
    system = (
        "You are a classifier for technical jargon. For each term, classify it as one of: "
        "'team_specific' (unique to this team), 'standard_technical' (AWS/standard cloud/programming term), or 'noise'. "
        "Return ONLY valid JSON: {\"definitions\":[{\"term\":\"...\",\"definition\":\"...\","
        "\"confidence\":0.0,\"classification\":\"team_specific|standard_technical|noise\",\"aliases\":[]}]}"
    )
    
    user = json.dumps({"terms": payload_terms})
    
    url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    
    print(f"\n📤 Sending request to {url}...")
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(url, headers=headers, json=body)
            print(f"Status: {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"❌ Error: {resp.text}")
                return False
            
            content = resp.json()["choices"][0]["message"]["content"]
            print(f"\n✓ Response received:")
            print(json.dumps(json.loads(content), indent=2))
            
            data = json.loads(content)
            for d in data.get("definitions", []):
                term = d.get("term")
                classification = d.get("classification", "MISSING")
                print(f"\n  {term:15} → {classification}")
            
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_openai())
    exit(0 if result else 1)
