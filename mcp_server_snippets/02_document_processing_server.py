"""
MCP Server - Document Processing System
========================================
Enterprise document processing server for PDF, Word, Excel, and text files.
Provides text extraction, OCR, metadata extraction, and document analysis.

Industry Use Case: Legal Tech, Healthcare, Insurance, Document Management
"""

import asyncio
import json
import os
from typing import Any, Optional
from datetime import datetime
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Initialize MCP server
server = Server("document-processing-server")

# Configuration
CONFIG = {
    "storage_path": "./documents",
    "max_file_size_mb": 50,
    "supported_formats": [".pdf", ".docx", ".txt", ".csv", ".xlsx", ".md"],
    "ocr_enabled": True
}

# Document storage
document_store = {}
processing_history = []


def ensure_storage_directory():
    """Ensure document storage directory exists"""
    Path(CONFIG["storage_path"]).mkdir(parents=True, exist_ok=True)


def extract_text_from_file(file_path: str) -> dict:
    """Extract text content from various file formats"""
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext == ".txt" or file_ext == ".md":
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return {
                "success": True,
                "text": text,
                "pages": 1,
                "word_count": len(text.split())
            }
        
        elif file_ext == ".pdf":
            # Simulated PDF processing (in production, use PyPDF2 or pdfplumber)
            return {
                "success": True,
                "text": "Simulated PDF content extraction. In production, use PyPDF2 or pdfplumber.",
                "pages": 5,
                "word_count": 1250,
                "metadata": {
                    "author": "John Doe",
                    "creation_date": "2025-01-01"
                }
            }
        
        elif file_ext == ".docx":
            # Simulated Word processing (in production, use python-docx)
            return {
                "success": True,
                "text": "Simulated Word document content. In production, use python-docx library.",
                "pages": 3,
                "word_count": 850
            }
        
        elif file_ext == ".csv":
            # Simple CSV reading
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            lines = text.split('\n')
            return {
                "success": True,
                "text": text,
                "rows": len(lines),
                "format": "csv"
            }
        
        else:
            return {
                "success": False,
                "error": f"Unsupported file format: {file_ext}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def analyze_document(text: str) -> dict:
    """Analyze document content"""
    words = text.split()
    sentences = text.split('.')
    
    # Basic analysis
    analysis = {
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": len([s for s in sentences if s.strip()]),
        "paragraph_count": len(text.split('\n\n')),
        "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
        "reading_time_minutes": len(words) / 200,  # Average reading speed
    }
    
    # Simple keyword extraction (top 10 words)
    word_freq = {}
    for word in words:
        word_lower = word.lower().strip('.,!?;:')
        if len(word_lower) > 3:  # Ignore short words
            word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
    
    top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    analysis["top_keywords"] = [{"word": word, "count": count} for word, count in top_keywords]
    
    return analysis


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available document resources"""
    resources = [
        Resource(
            uri="docs://directory",
            name="Document Directory",
            mimeType="application/json",
            description="List of all processed documents"
        ),
        Resource(
            uri="docs://processing-history",
            name="Processing History",
            mimeType="application/json",
            description="History of document processing operations"
        ),
        Resource(
            uri="docs://statistics",
            name="Processing Statistics",
            mimeType="application/json",
            description="Overall statistics about processed documents"
        )
    ]
    
    # Add individual documents
    for doc_id, doc_info in document_store.items():
        resources.append(
            Resource(
                uri=f"docs://{doc_id}",
                name=doc_info["filename"],
                mimeType="application/json",
                description=f"Processed document: {doc_info['filename']}"
            )
        )
    
    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read document resources"""
    if uri == "docs://directory":
        directory = {
            "total_documents": len(document_store),
            "documents": [
                {
                    "id": doc_id,
                    "filename": doc_info["filename"],
                    "processed_at": doc_info["processed_at"],
                    "size_bytes": doc_info.get("size_bytes", 0)
                }
                for doc_id, doc_info in document_store.items()
            ]
        }
        return json.dumps(directory, indent=2)
    
    elif uri == "docs://processing-history":
        return json.dumps(processing_history[-50:], indent=2)  # Last 50 operations
    
    elif uri == "docs://statistics":
        stats = {
            "total_processed": len(document_store),
            "total_operations": len(processing_history),
            "formats_processed": {},
            "total_words_extracted": 0
        }
        
        for doc_info in document_store.values():
            ext = Path(doc_info["filename"]).suffix
            stats["formats_processed"][ext] = stats["formats_processed"].get(ext, 0) + 1
            if "analysis" in doc_info:
                stats["total_words_extracted"] += doc_info["analysis"].get("word_count", 0)
        
        return json.dumps(stats, indent=2)
    
    elif uri.startswith("docs://"):
        doc_id = uri.replace("docs://", "")
        if doc_id in document_store:
            return json.dumps(document_store[doc_id], indent=2)
        else:
            raise ValueError(f"Document not found: {doc_id}")
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available document processing tools"""
    return [
        Tool(
            name="upload_document",
            description="Upload and process a document. Supports PDF, Word, text, CSV, and Excel files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to upload"
                    },
                    "content": {
                        "type": "string",
                        "description": "Base64 encoded file content or text content"
                    },
                    "extract_text": {
                        "type": "boolean",
                        "description": "Extract text content from document",
                        "default": True
                    },
                    "analyze": {
                        "type": "boolean",
                        "description": "Perform content analysis",
                        "default": True
                    }
                },
                "required": ["filename", "content"]
            }
        ),
        Tool(
            name="extract_entities",
            description="Extract named entities (people, organizations, locations) from document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "ID of the processed document"
                    },
                    "entity_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["person", "organization", "location", "date", "money"]
                        },
                        "description": "Types of entities to extract"
                    }
                },
                "required": ["document_id"]
            }
        ),
        Tool(
            name="summarize_document",
            description="Generate a summary of the document content",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "ID of the processed document"
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum length of summary in words",
                        "default": 200
                    },
                    "style": {
                        "type": "string",
                        "enum": ["brief", "detailed", "bullet-points"],
                        "description": "Summary style",
                        "default": "brief"
                    }
                },
                "required": ["document_id"]
            }
        ),
        Tool(
            name="compare_documents",
            description="Compare two documents and identify similarities and differences",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id_1": {
                        "type": "string",
                        "description": "First document ID"
                    },
                    "document_id_2": {
                        "type": "string",
                        "description": "Second document ID"
                    },
                    "comparison_type": {
                        "type": "string",
                        "enum": ["content", "structure", "metadata"],
                        "description": "Type of comparison to perform"
                    }
                },
                "required": ["document_id_1", "document_id_2"]
            }
        ),
        Tool(
            name="search_documents",
            description="Search across all processed documents",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "search_fields": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["content", "filename", "metadata"]
                        },
                        "description": "Fields to search in"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="extract_tables",
            description="Extract tables from documents (PDF, Word, Excel)",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "ID of the processed document"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["json", "csv", "markdown"],
                        "description": "Format for extracted tables",
                        "default": "json"
                    }
                },
                "required": ["document_id"]
            }
        ),
        Tool(
            name="ocr_document",
            description="Perform OCR (Optical Character Recognition) on images within documents",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "ID of the processed document"
                    },
                    "language": {
                        "type": "string",
                        "description": "OCR language code (e.g., 'eng', 'spa')",
                        "default": "eng"
                    }
                },
                "required": ["document_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute document processing tools"""
    
    if name == "upload_document":
        filename = arguments.get("filename", "")
        content = arguments.get("content", "")
        extract_text = arguments.get("extract_text", True)
        analyze = arguments.get("analyze", True)
        
        # Generate document ID
        doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(document_store)}"
        
        # Simulate file storage
        doc_info = {
            "id": doc_id,
            "filename": filename,
            "processed_at": datetime.now().isoformat(),
            "size_bytes": len(content),
            "content": content[:500] + "..." if len(content) > 500 else content  # Store preview
        }
        
        # Extract text if requested
        if extract_text:
            # Simulate extraction based on file extension
            extraction = {
                "success": True,
                "text": content if filename.endswith('.txt') else "Extracted text content...",
                "word_count": len(content.split())
            }
            doc_info["extracted_text"] = extraction
        
        # Analyze if requested
        if analyze and extract_text:
            analysis = analyze_document(doc_info.get("extracted_text", {}).get("text", ""))
            doc_info["analysis"] = analysis
        
        # Store document
        document_store[doc_id] = doc_info
        
        # Log operation
        processing_history.append({
            "timestamp": datetime.now().isoformat(),
            "operation": "upload_document",
            "document_id": doc_id,
            "filename": filename,
            "status": "success"
        })
        
        result = {
            "status": "success",
            "document_id": doc_id,
            "filename": filename,
            "extracted_text": extract_text,
            "analyzed": analyze
        }
        
        if analyze:
            result["analysis_summary"] = doc_info.get("analysis", {})
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "extract_entities":
        document_id = arguments.get("document_id", "")
        entity_types = arguments.get("entity_types", ["person", "organization", "location"])
        
        if document_id not in document_store:
            return [TextContent(type="text", text=f"Error: Document '{document_id}' not found")]
        
        # Simulated entity extraction
        entities = {
            "document_id": document_id,
            "entities": [
                {"type": "person", "text": "John Smith", "confidence": 0.95},
                {"type": "organization", "text": "Acme Corp", "confidence": 0.92},
                {"type": "location", "text": "New York", "confidence": 0.88},
                {"type": "date", "text": "2025-12-05", "confidence": 0.90},
                {"type": "money", "text": "$1,500", "confidence": 0.87}
            ]
        }
        
        # Filter by requested types
        filtered_entities = [e for e in entities["entities"] if e["type"] in entity_types]
        entities["entities"] = filtered_entities
        
        return [TextContent(type="text", text=json.dumps(entities, indent=2))]
    
    elif name == "summarize_document":
        document_id = arguments.get("document_id", "")
        max_length = arguments.get("max_length", 200)
        style = arguments.get("style", "brief")
        
        if document_id not in document_store:
            return [TextContent(type="text", text=f"Error: Document '{document_id}' not found")]
        
        doc = document_store[document_id]
        
        # Simulated summarization
        if style == "brief":
            summary = f"This document '{doc['filename']}' contains important information. Key topics include business processes, technical specifications, and compliance requirements."
        elif style == "detailed":
            summary = f"Detailed Summary:\n\nThe document '{doc['filename']}' provides comprehensive coverage of multiple topics. It begins with an introduction to the subject matter, followed by detailed explanations of key concepts. The middle sections contain specific examples and use cases. The document concludes with recommendations and next steps."
        else:  # bullet-points
            summary = f"Summary of '{doc['filename']}':\n• Main topic: [Topic]\n• Key findings: [Findings]\n• Recommendations: [Recommendations]\n• Next steps: [Actions]"
        
        result = {
            "document_id": document_id,
            "summary": summary,
            "style": style,
            "length": len(summary.split())
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "compare_documents":
        doc_id_1 = arguments.get("document_id_1", "")
        doc_id_2 = arguments.get("document_id_2", "")
        comparison_type = arguments.get("comparison_type", "content")
        
        if doc_id_1 not in document_store:
            return [TextContent(type="text", text=f"Error: Document '{doc_id_1}' not found")]
        if doc_id_2 not in document_store:
            return [TextContent(type="text", text=f"Error: Document '{doc_id_2}' not found")]
        
        doc1 = document_store[doc_id_1]
        doc2 = document_store[doc_id_2]
        
        comparison = {
            "document_1": {"id": doc_id_1, "filename": doc1["filename"]},
            "document_2": {"id": doc_id_2, "filename": doc2["filename"]},
            "comparison_type": comparison_type,
            "similarity_score": 0.75,  # Simulated
            "differences": [
                "Document 1 is longer by 250 words",
                "Document 2 contains more technical terminology",
                "Both documents share 45% common keywords"
            ],
            "common_topics": ["business process", "implementation", "requirements"]
        }
        
        return [TextContent(type="text", text=json.dumps(comparison, indent=2))]
    
    elif name == "search_documents":
        query = arguments.get("query", "")
        search_fields = arguments.get("search_fields", ["content", "filename"])
        max_results = arguments.get("max_results", 10)
        
        # Simple search simulation
        results = []
        for doc_id, doc_info in document_store.items():
            score = 0
            
            if "content" in search_fields:
                if query.lower() in doc_info.get("content", "").lower():
                    score += 10
            
            if "filename" in search_fields:
                if query.lower() in doc_info["filename"].lower():
                    score += 5
            
            if score > 0:
                results.append({
                    "document_id": doc_id,
                    "filename": doc_info["filename"],
                    "relevance_score": score,
                    "snippet": doc_info.get("content", "")[:100] + "..."
                })
        
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        results = results[:max_results]
        
        search_result = {
            "query": query,
            "total_results": len(results),
            "results": results
        }
        
        return [TextContent(type="text", text=json.dumps(search_result, indent=2))]
    
    elif name == "extract_tables":
        document_id = arguments.get("document_id", "")
        output_format = arguments.get("output_format", "json")
        
        if document_id not in document_store:
            return [TextContent(type="text", text=f"Error: Document '{document_id}' not found")]
        
        # Simulated table extraction
        tables = {
            "document_id": document_id,
            "tables_found": 2,
            "output_format": output_format,
            "tables": [
                {
                    "table_number": 1,
                    "rows": 5,
                    "columns": 3,
                    "data": [
                        ["Name", "Age", "City"],
                        ["John", "30", "NYC"],
                        ["Jane", "25", "LA"]
                    ]
                }
            ]
        }
        
        return [TextContent(type="text", text=json.dumps(tables, indent=2))]
    
    elif name == "ocr_document":
        document_id = arguments.get("document_id", "")
        language = arguments.get("language", "eng")
        
        if document_id not in document_store:
            return [TextContent(type="text", text=f"Error: Document '{document_id}' not found")]
        
        # Simulated OCR
        ocr_result = {
            "document_id": document_id,
            "language": language,
            "images_processed": 3,
            "extracted_text": "This is simulated OCR text extracted from images in the document. In production, use Tesseract or cloud OCR services.",
            "confidence": 0.94
        }
        
        return [TextContent(type="text", text=json.dumps(ocr_result, indent=2))]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server"""
    ensure_storage_directory()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
