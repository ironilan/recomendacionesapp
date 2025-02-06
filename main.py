from fastapi import FastAPI, Request
from api import api
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(debug=True)
##app = FastAPI()

app.include_router(api)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    
    
    response = await call_next(request)
    print('hola desde el middleware')
    return response


origin = [
    "http://localhost:3000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api)


