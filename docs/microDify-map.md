# microDify 架构图谱

## 组件关系流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HTTP 请求入口                                  │
│  Caddy :443 / Next.js :3000 ──rewrites──→ FastAPI :8000             │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   Middleware Stack       │
                    │  ┌────────────────────┐  │
                    │  │ RequestLogging     │  │  ← request_id 生成
                    │  │ + Runtime Metrics  │  │  ← total_requests++
                    │  └────────┬───────────┘  │  ← status_counts 分桶
                    │           │              │
                    │  ┌────────┴───────────┐  │
                    │  │ CORS              │  │
                    │  └────────┬───────────┘  │
                    │           │              │
                    └───────────┼──────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  auth/          │ │  provider/      │ │  (空 routing)    │
│                 │ │                 │ │                 │
│ POST /login ────┤ │ GET  /status ───┤ │ chat/           │
│  │              │ │ POST /test-chat │ │ agent/          │
│  │              │ │       │         │ │ workflow/       │
│  ▼              │ │       ▼         │ │ knowledge/      │
│ service.auth ───┤ │ LLMGateway ────┐│ │ prompt/         │
│  │      │       │ │   │            ││ │                 │
│  │      │       │ │   ▼            ││ └─────────────────┘
│  │      │       │ │ ProviderRegistry                 
│  │      │       │ │   ├─ OpenAI   ──→ DeepSeek API      
│  │      │       │ │   └─ Anthropic──→ DeepSeek API      
│  │      │       │ └─────────────────┘
│  │      │       │
│  ▼      ▼       │
│ User   Redis    │
│ Model  Client   │
│                 │
└────────┬────────┘
         │
    ┌────┴────┐        ┌─────────────┐
    │PostgreSQL│        │    Redis    │
    │  + pgvector       │  限流+队列   │
    │  17 tables│        │  localhost  │
    └──────────┘        └─────────────┘
```

---

## 运行时请求流转（以 POST /auth/login 为例）

```
1. HTTP Request
   │  POST /auth/login  {"email":"...","password":"..."}
   ▼
2. RequestLoggingMiddleware
   │  request_id = a3f8b2c1
   │  total_requests += 1
   ▼
3. Auth Router
   │  Depends(get_db)     → AsyncSession
   │  Depends(get_redis)  → RedisClient | None
   ▼
4. Rate Limit Check
   │  redis.incr("rate_limit:auth_login:login_failed:admin@...")
   │  超过 5 次 → 429
   ▼
5. Auth Service
   │  get_user_by_email(db, email)
   │  verify_password(plain, hashed)
   │  create_token(user_id) → JWT
   ▼
6. Result.ok(TokenResponse)
   │  {"code":200,"data":{"access_token":"eyJ..."}}
   ▼
7. RequestLoggingMiddleware (finally)
   │  status_counts["200"] += 1
   │  log: method=POST path=/auth/login status=200 duration_ms=45.2
   │  Response Header: X-Request-ID: a3f8b2c1
   ▼
8. HTTP Response
```
