from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import state, feedback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(state.router)
app.include_router(feedback.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the EchoNexus Narrative State Management System"}
