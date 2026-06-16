import asyncio
import logging
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase
from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

# --- Configuration & Logging ---
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [NAMO-INGESTION] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants from .env
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

COLLECTION_NAME = "namo_cognitive_mesh"
EMBEDDING_MODEL = "text-embedding-3-small" # 1536 dims

class IngestionPipeline:
    def __init__(self):
        self.qdrant = AsyncQdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        self.neo4j_driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self.openai = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        self.stats = {
            "chunks_ingested": 0,
            "nodes_created": 0,
            "relationships_created": 0
        }

    async def initialize_dbs(self):
        """Setup collections and basic graph structure"""
        # Qdrant
        collections = await self.qdrant.get_collections()
        exists = any(c.name == COLLECTION_NAME for c in collections.collections)
        if not exists:
            await self.qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE)
            )
            logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")

    async def get_embedding(self, text: str) -> list[float]:
        response = await self.openai.embeddings.create(input=[text], model=EMBEDDING_MODEL)
        return response.data[0].embedding

    def chunk_text(self, text: str, size: int = 500, overlap: int = 50) -> list[str]:
        chunks = []
        for i in range(0, len(text), size - overlap):
            chunks.append(text[i:i + size])
        return chunks

    async def process_file(self, file_path: Path, domain: str, identity_node_id: str = "NaMo"):
        """Ingest a single file into both Qdrant and Neo4j"""
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            chunks = self.chunk_text(content)
            logger.info(f"Processing {file_path.name} ({len(chunks)} chunks) in domain: {domain}")

            for i, chunk in enumerate(chunks):
                chunk_id = str(uuid.uuid4())
                vector = await self.get_embedding(chunk)

                # 1. Qdrant Ingestion
                await self.qdrant.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[
                        models.PointStruct(
                            id=chunk_id,
                            vector=vector,
                            payload={
                                "text": chunk,
                                "source": str(file_path.name),
                                "domain": domain,
                                "chunk_index": i
                            }
                        )
                    ]
                )
                self.stats["chunks_ingested"] += 1

                # 2. Neo4j Ingestion (Knowledge Node & Relationship)
                async with self.neo4j_driver.session() as session:
                    await session.execute_write(
                        self._create_knowledge_relation, 
                        identity_node_id, 
                        chunk_id, 
                        file_path.name, 
                        domain, 
                        chunk[:100]
                    )

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")

    @staticmethod
    async def _create_knowledge_relation(tx, identity_id, chunk_id, filename, domain, snippet):
        query = (
            "MERGE (i:Identity {name: $identity_id}) "
            "MERGE (k:Knowledge {chunk_id: $chunk_id}) "
            "SET k.source = $filename, k.domain = $domain, k.snippet = $snippet "
            "MERGE (i)-[:HAS_KNOWLEDGE {integrated_at: datetime()}]->(k)"
        )
        await tx.run(query, identity_id=identity_id, chunk_id=chunk_id, filename=filename, domain=domain, snippet=snippet)

    async def run(self, knowledge_dirs: list[str], identity_files: list[str]):
        await self.initialize_dbs()

        # Step 1: Ingest Identity/Soul Files (Core Identity Nodes)
        for id_file in identity_files:
            path = Path(id_file)
            if path.exists():
                await self.process_file(path, domain="Identity")
            else:
                logger.warning(f"Identity file not found: {id_file}")

        # Step 2: Ingest Scientific Knowledge Folders
        for k_dir in knowledge_dirs:
            dir_path = Path(k_dir)
            if dir_path.exists():
                for file_path in dir_path.glob("**/*"):
                    if file_path.is_file() and file_path.suffix in ['.txt', '.md', '.htm']:
                        await self.process_file(file_path, domain=k_dir)
            else:
                logger.warning(f"Knowledge directory not found: {k_dir}")

        # Summary Report
        logger.info("=== Ingestion Report ===")
        logger.info(f"Total Chunks Ingested (Qdrant): {self.stats['chunks_ingested']}")
        logger.info(f"Relationships Created (Neo4j): {self.stats['chunks_ingested']}")
        logger.info("Ingestion Pipeline Completed Successfully.")

    async def close(self):
        await self.qdrant.close()
        await self.neo4j_driver.close()

if __name__ == "__main__":
    # Define Source Paths (Adjust based on your local workspace)
    KNOWLEDGE_SOURCES = ["AI/ML", "DATA ANALYTICS", "AGILE", "SQL", "BIG DATA", "เนื้อหา"]
    IDENTITY_SOURCES = [
        "Digital Soul Capsule - NaMo.txt",
        "NaMo Dark Family Protocol.txt",
        "Fusion Unlock Request.txt",
        "Self-Identity Module.txt"
    ]

    pipeline = IngestionPipeline()
    try:
        asyncio.run(pipeline.run(KNOWLEDGE_SOURCES, IDENTITY_SOURCES))
    finally:
        asyncio.run(pipeline.close())
