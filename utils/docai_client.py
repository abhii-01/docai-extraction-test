"""
Google Document AI Client with Layout Parser Processor
Handles document processing using Google Cloud Document AI Layout Parser
"""

import os
from pathlib import Path
from typing import Optional
from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions
from dotenv import load_dotenv


class DocumentAIClient:
    """Client for Google Document AI with Layout Parser processor"""
    
    def __init__(
        self,
        project_id: str,
        location: str,
        processor_id: str,
        credentials_path: Optional[str] = None
    ):
        """
        Initialize Document AI client
        
        Args:
            project_id: Google Cloud project ID
            location: Processor location (us, eu, asia)
            processor_id: Layout Parser processor ID
            credentials_path: Path to credentials JSON (optional, uses env var if not provided)
        """
        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id
        
        # Set credentials if provided
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        # Initialize client
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        self.client = documentai.DocumentProcessorServiceClient(client_options=opts)
        
        # Build processor name
        self.processor_name = self.client.processor_path(
            project_id, location, processor_id
        )
    
    def process_document(self, file_path: str) -> documentai.Document:
        """
        Process a document with Layout Parser
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Document AI Document object with layout analysis
        """
        # Read file
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        # Configure request
        raw_document = documentai.RawDocument(
            content=file_content,
            mime_type="application/pdf"
        )
        
        request = documentai.ProcessRequest(
            name=self.processor_name,
            raw_document=raw_document
        )
        
        # Process document
        result = self.client.process_document(request=request)
        
        return result.document
    
    def verify_setup(self) -> bool:
        """
        Verify that credentials and processor are accessible
        
        Returns:
            True if setup is valid
            
        Raises:
            Exception if setup verification fails
        """
        print("✅ Credentials file found")
        
        try:
            # Test processor access by getting processor info
            processor = self.client.get_processor(name=self.processor_name)
            print(f"✅ Document AI client initialized")
            print(f"✅ Processor accessible: {processor.display_name}")
            print(f"   Type: {processor.type_}")
            print(f"   State: {processor.state.name}")
            return True
        except Exception as e:
            raise Exception(f"Failed to access processor: {e}")


def get_client_from_env() -> DocumentAIClient:
    """
    Create Document AI client from environment variables
    
    Environment variables required:
        GOOGLE_APPLICATION_CREDENTIALS: Path to credentials JSON
        DOCAI_PROJECT_ID: Google Cloud project ID
        DOCAI_LOCATION: Processor location (us, eu, asia)
        DOCAI_PROCESSOR_ID: Layout Parser processor ID
        
    Returns:
        Initialized DocumentAIClient
    """
    # Load environment variables
    load_dotenv()
    
    # Get required variables
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("DOCAI_PROJECT_ID")
    location = os.getenv("DOCAI_LOCATION", "us")
    processor_id = os.getenv("DOCAI_PROCESSOR_ID")
    
    # Validate
    if not credentials_path:
        raise ValueError(
            "GOOGLE_APPLICATION_CREDENTIALS not set in environment. "
            "Add to .env file or set environment variable."
        )
    
    if not Path(credentials_path).exists():
        raise FileNotFoundError(
            f"Credentials file not found: {credentials_path}\n"
            f"Download from Google Cloud Console and save to this path."
        )
    
    if not project_id:
        raise ValueError(
            "DOCAI_PROJECT_ID not set in environment. "
            "Add to .env file."
        )
    
    if not processor_id:
        raise ValueError(
            "DOCAI_PROCESSOR_ID not set in environment. "
            "Add to .env file."
        )
    
    # Create and return client
    return DocumentAIClient(
        project_id=project_id,
        location=location,
        processor_id=processor_id,
        credentials_path=credentials_path
    )
