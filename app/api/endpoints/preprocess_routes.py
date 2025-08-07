from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.preprocess_pdf import PDFPreProcessorPipeline

class PreprocessRoutes:
    def __init__(self):
        self.router = APIRouter(prefix="/preprocess")
        self.preprocess_pipeline = PDFPreProcessorPipeline()

        self._add_routes()
        
    def _add_routes(self):
        self.router.get("/preprocess-pdf")(self.preprocess_pdf)

    def preprocess_pdf(self):
        self.preprocess_pipeline.process_contracts()

        return JSONResponse(content={"message": "Contracts preprocessed successfully"})