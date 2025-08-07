from fastapi import APIRouter, status
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
        try:
            self.preprocess_pipeline.process_contracts()

            return JSONResponse(content={"message": "Contracts preprocessed successfully"})
        except Exception as e:
            print(f"Error preprocessing contracts: {e}")
            return JSONResponse(content={"error": "Error preprocessing contracts"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)