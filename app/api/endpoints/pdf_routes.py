import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.gemini_service import GeminiService
import time

class PdfRoutes:
    def __init__(self):
        self.router = APIRouter(prefix="/pdf")
        self.gemini_service = GeminiService()

        self._add_routes()
    
    def _add_routes(self):
        self.router.get("/extract-clauses-and-summary")(self.extract_clauses_and_summary)

    def extract_clauses_and_summary(self):
        final_data = []

        print("Extracting clauses and summary...")

        with open("app/data/processed_contracts.json", "r") as f:
            contracts = json.load(f)

        for i, contract in enumerate(contracts):
            print(f"Processing contract {i+1} of {len(contracts)}")
            clauses = self.gemini_service.extract_clauses(contract["text"])
            summary = self.gemini_service.extract_summary(contract["text"])

            final_data.append({
                "contract_id": contract["contract_id"],
                "summary": summary.strip(),
                "termination_clause": clauses.termination_clause,
                "confidentiality_clause": clauses.confidentiality_clause,
                "liability_clause": clauses.liability_clause
            })

            if i>=8 and i%8 == 0:
                print(f"Sleeping for 10 seconds to avoid rate limit...")
                time.sleep(10)
                print(f"Continuing...")

            # break

        with open("output/final_output.json", "w") as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)

        return JSONResponse(content={
            "output_file": "output/final_output.json"
        })


