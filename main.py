from time import sleep

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from typing import List, Any
from pydantic import BaseSettings, BaseModel

from parser import Parser


class Settings(BaseSettings):
    name: str = "AMR Parser"
    target: str = "local"
    version: str = "dev"
    allowed_origins: List[str] = ["http://localhost", "http://localhost:8080"]

    archive_path: str = "/app/external_data/raw_text_model.tar.gz"
    wordnet_path: str = "/app/external_data/wordnet3.0/dict/"
    lookup_path: str = "/app/external_data/lookup/lookupdata17/"
    am_tools_path: str = "/app/external_data/am-tools.jar"

    cuda_device: int = -1
    overrides: str = ""
    weights_file: str = None

    @property
    def short_name(self) -> str:
        return self.name.replace(" ", "_").lower()


settings = Settings()


class AMRParseRequest(BaseModel):
    sentence: str


class AMRParseResponse(BaseModel):
    amr: str


# Create the service and hide the documentation if it is deployed in production
app = FastAPI(
    title=settings.name,
    docs_url=None if settings.target == "docker" else "/docs",
    redoc_url=None if settings.target == "docker" else "/redoc",
)

# Configure CORS
if settings.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

parser = Parser(settings.archive_path, settings.cuda_device, settings.overrides, settings.weights_file,
                settings.lookup_path, settings.wordnet_path, settings.am_tools_path)


@app.post("/")
def parse(request: AMRParseRequest):
    return AMRParseResponse(amr=parser.parse(request.sentence.strip()))
