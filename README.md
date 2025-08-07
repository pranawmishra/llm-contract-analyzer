# LLM Contract Analyzer

## Overview
This project implements a document processing pipeline that uses Large Language Models (LLMs) to analyze legal contracts, extract specific clauses, and summarize key terms.

## Dataset
This project uses the CUAD (Contract Understanding Atticus Dataset) - a publicly available dataset containing over 13,000 legal clauses from 510 contracts, annotated with 41 types of clauses. For this assignment, we use a subset of 50 contracts from the CUAD dataset.

## Features
- PDF text extraction and normalization
- Clause extraction (termination, confidentiality, liability)
- Contract summarization (100-150 words)
- FastAPI-based REST API

## Bonus Features (Optional Requirements)
✅ **Semantic Search**: Implemented semantic search over clauses using ```VoyageAI``` embeddings with ```ChromaDB``` vector storage  
✅ **Few-Shot Learning**: Enhanced clause extraction prompts with concrete examples for improved accuracy

### Semantic Search API Endpoints:
- `GET /semantic/create-embeddings` - Create embeddings for generated clauses
- `GET /semantic/search/{query}` - Search for documents using semantic similarity

## Approach Explanation

### Methodology Overview
This project implements a **two-stage document processing pipeline** that combines traditional PDF text extraction with modern LLM-based analysis to automatically process legal contracts.

### Stage 1: Document Preprocessing
**Objective**: Convert raw PDF contracts into clean, structured text data

**Process**:
1. **PDF Text Extraction**: Using PyMuPDF to extract raw text from PDF files
2. **Text Normalization**: 
   - Remove non-ASCII characters and PDF artifacts
   - Fix OCR errors and spacing issues
   - Normalize whitespace and punctuation
   - Remove headers/footers and page numbers
   - Normalize dates and monetary amounts
3. **Data Structuring**: Organize extracted text into JSON format with metadata

**Key Features**:
- Handles various PDF formats and quality levels
- Removes common contract artifacts (page numbers, headers, footers)
- Preserves document structure and content integrity
- Generates metadata (character count, word count, filename)

### Stage 2: LLM-Powered Analysis
**Objective**: Extract specific legal clauses and generate contract summaries using AI

**Process**:
1. **Clause Extraction**:
   - **Termination Clauses**: Identify conditions and procedures for contract termination
   - **Confidentiality Clauses**: Extract information protection and non-disclosure terms
   - **Liability Clauses**: Identify risk allocation and damage limitation provisions
   
2. **Contract Summarization**:
   - Generate 100-150 word summaries
   - Include purpose of agreement
   - Highlight key obligations of each party
   - Identify notable risks and penalties

**LLM Integration**:
- **Model**: Google Gemini 2.5 Flash
- **Prompt Engineering**: Structured prompts for consistent output
- **Response Format**: JSON schema for clause extraction, natural language for summaries
- **Error Handling**: Rate limiting and retry mechanisms

### Technical Approach

#### 1. **Modular Architecture**
- **Separation of Concerns**: Each component has a specific responsibility
- **Service Layer**: Business logic separated from API layer
- **Utils Layer**: Reusable helper functions
- **Data Layer**: Structured storage and retrieval

#### 2. **API-First Design**
- **RESTful Endpoints**: Clean, predictable API structure
- **Asynchronous Processing**: Non-blocking operations for large document sets
- **CORS Support**: Cross-origin resource sharing enabled
- **Health Checks**: System monitoring capabilities

#### 3. **Data Pipeline**
```
Raw PDFs → Text Extraction → Normalization → Structured JSON → LLM Analysis → Final Output
```

#### 4. **Quality Assurance**
- **Text Cleaning**: Multiple cleaning stages for optimal LLM input
- **Prompt Optimization**: Carefully crafted prompts for accurate extraction
- **Output Validation**: Structured response validation using Pydantic models
- **Error Handling**: Graceful failure handling and logging

### Key Innovations

1. **Intelligent Text Preprocessing**:
   - Advanced cleaning algorithms for legal document artifacts
   - Context-aware header/footer removal
   - OCR error correction

2. **Structured LLM Output**:
   - JSON schema enforcement for clause extraction
   - Consistent formatting across different contract types
   - Reliable parsing and validation

3. **Scalable Architecture**:
   - Batch processing capabilities
   - Rate limiting for API compliance
   - Modular design for easy extension

### Performance Considerations

- **Batch Processing**: Process multiple contracts efficiently
- **Rate Limiting**: Respect LLM API limits with intelligent delays
- **Memory Management**: Stream processing for large documents
- **Caching**: Intermediate results stored for reprocessing

### Accuracy and Reliability

- **Prompt Engineering**: Optimized prompts for legal document analysis
- **Error Handling**: Robust error handling for various failure scenarios
- **Validation**: Output validation using structured schemas
- **Testing**: Comprehensive testing of extraction accuracy

## Prerequisites

### Install uv (Project Management Tool)
This project uses `uv` for dependency management. Install it first:

**Windows:**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Alternative (using pip):**
```bash
pip install uv
```

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd llm-contract-analyzer
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Set up Google Gemini API credentials:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file in the project root:
     ```bash
     GOOGLE_API_KEY=your_api_key_here
     ```

4. Place contracts in `app/data/Contracts/`

## Usage
1. Start the FastAPI server:
   ```bash
   uv run python -m uvicorn app.main:app --reload
   ```
   or a simpler way
   ```bash
   uv run run.py
   ```

2. Preprocess contracts:
   ```bash
   curl http://localhost:8000/preprocess/preprocess-pdf
   ```

3. Extract clauses and summaries:
   ```bash
   curl http://localhost:8000/pdf/extract-clauses-and-summary
   ```

## Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF Contracts │    │   FastAPI App   │    │  Gemini LLM API │
│   (Input Data)  │───▶│   (Main App)    │───▶│   (External)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Processed JSON │
                       │   (Output)      │
                       └─────────────────┘
```


### Data Flow

1. **Input Processing**:
   - PDF contracts are placed in `app/data/Contracts/`
   - `preprocess_routes.py` triggers PDF preprocessing
   - `PDFPreProcessorPipeline` extracts and cleans text
   - Processed data saved to `app/data/processed_contracts.json`

2. **Analysis Pipeline**:
   - `pdf_routes.py` loads processed contracts
   - `GeminiService` sends text to Gemini LLM API
   - LLM extracts clauses and generates summaries
   - Results saved to `output/final_output.json`

3. **Key Components**:
   - **API Layer**: FastAPI with CORS middleware
   - **Service Layer**: Business logic for PDF processing and LLM interaction
   - **Utils**: Helper functions for prompt loading and file operations
   - **Data Layer**: JSON storage for processed contracts and results

### File Structure
```
app/
├── main.py                 # FastAPI application entry point
├── api/
│   ├── router.py          # API router configuration
│   └── endpoints/
│       ├── pdf_routes.py      # Contract analysis endpoints
│       └── preprocess_routes.py # PDF preprocessing endpoints
├── services/
│   ├── gemini_service.py      # LLM interaction service
│   └── preprocess_pdf.py      # PDF text extraction service
├── utils/
│   └── utils.py              # Helper functions
├── prompts/
│   ├── extract_clause_prompt.md    # LLM prompt for clause extraction
│   └── extract_summary_prompt.md   # LLM prompt for summarization
└── data/
    ├── Contracts/              # Input PDF contracts
    └── processed_contracts.json # Processed contract data
```