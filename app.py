from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
app = FastAPI(title="Production FastAPI with Rate Limiter")

# Startup and shutdown events for Redis + FastAPILimiter
@app.on_event("startup")
async def startup():
    try:
        r = redis.from_url(
            "redis://127.0.0.1:6379",
            encoding="utf-8",
            decode_responses=True
        )
        await FastAPILimiter.init(r)
        print("✅ Connected to Redis successfully.")
    except Exception as e:
        print("❌ Failed to connect to Redis:", e)

@app.on_event("shutdown")
async def shutdown():
    await FastAPILimiter.close()
    print("🛑 Redis connection closed.")

# Public route (rate limit per IP)
@app.get("/public", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def public_route():
    return {"message": "Public endpoint — 10 requests per minute allowed"}

# API key authentication
async def get_api_key(request: Request):
    api_key = request.headers.get("x-api-key")
    if api_key not in {"key123", "key456"}:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

# Private route (rate limit per key)
@app.get("/private", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def private_route(api_key: str = Depends(get_api_key)):
    return {"message": f"Private route for API key {api_key}"}

# Custom rate-limit handler
@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "retry_after": request.headers.get("Retry-After", "60"),
            "message": "Please try again later."
        },
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
