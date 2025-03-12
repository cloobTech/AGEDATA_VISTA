from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routes import auth, project,data_processing,uploaded_file, user


app = FastAPI()


origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allow sending cookies in cross-origin requests
    # Allow all HTTP methods, you can specify specific methods if needed
    allow_methods=["*"],
    # Allow all headers, you can specify specific headers if needed
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(project.router)
app.include_router(data_processing.router)
app.include_router(uploaded_file.router)
app.include_router(user.router)


@app.get("/")
async def read_root():
    """Check server status"""
    return {"server_status": "Server is running fine..."}
