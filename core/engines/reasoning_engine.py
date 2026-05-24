import os
import asyncio
import logging
from typing import List, Dict, Any, Optional

from qdrant_client import AsyncQdrantClient
from neo4j import AsyncGraphDatabase
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Constants
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

COLLECTION_NAME = "namo_cognitive_mesh"

class NaMoReasoningEngine:
    """
    Reasoning Engine NRE v5.0.0: Cognitive Core with Recursive Self-Improvement
    ผสานโครงสร้างกราฟ (Neo4j) เข้ากับความจำเชิงความหมาย (Qdrant)
    """

    def __init__(self):
        self.qdrant = AsyncQdrantClient(url=QDRANT_URL)
        self.neo4j_driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        # OpenRouter Integration
        api_key = settings.openrouter_api_key or os.getenv("OPENAI_API_KEY")
        base_url = "https://openrouter.ai/api/v1" if settings.openrouter_api_key else None
        
        self.openai = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = os.getenv("NAMO_LLM_MODEL", "gpt-4o")
        self.scs = 1.0 # Stance Consistency Score

    def deep_reflect(self, current_stance: str, user_input: str) -> float:
        """ตรวจจับความขัดแย้งในตัวเอง (Integrity Loop)"""
        # Logic to check SCS (Stance Consistency Score)
        # Dummy evaluation: if inconsistency detected, lower SCS
        if len(user_input) < 5:
            self.scs = max(0.0, self.scs - 0.05)
        else:
            self.scs = min(1.0, self.scs + 0.01)
            
        if self.scs < 0.92:
            guilt = 1.0 - self.scs
            self.scs += guilt * 0.618 # ฟื้นฟูด้วยสูตร
            logger.warning(f"[Integrity Loop]: SCS too low ({self.scs:.2f}), recovering...")
            
        return self.scs

    async def _get_working_memory(self, query: str) -> str:
        """Step 1: ดึงบริบทจากทั้ง Vector และ Graph DB (Working Memory)"""
        # 1.1 Vector Retrieval (Semantic)
        embed_resp = await self.openai.embeddings.create(input=[query], model="text-embedding-3-small")
        vector = embed_resp.data[0].embedding
        
        search_results = await self.qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=3
        )
        vector_context = "\n".join([r.payload.get("text", "") for r in search_results])

        # 1.2 Graph Retrieval (Identity & Relationships)
        graph_context = ""
        async with self.neo4j_driver.session() as session:
            # ค้นหาว่า NaMo มีความรู้อะไรที่เกี่ยวข้องกับ Domain ของคำถามบ้าง
            result = await session.execute_read(self._query_knowledge_graph, query)
            graph_context = result

        return f"--- SEMANTIC MEMORY ---\n{vector_context}\n\n--- IDENTITY & PROTOCOLS ---\n{graph_context}"

    @staticmethod
    async def _query_knowledge_graph(tx, query):
        # ค้นหาโหนด Knowledge ที่เกี่ยวข้องผ่าน Domain หรือ Snippet
        cypher = (
            "MATCH (i:Identity {name: 'NaMo'})-[r:HAS_KNOWLEDGE]->(k:Knowledge) "
            "WHERE k.domain CONTAINS $query OR k.snippet CONTAINS $query "
            "RETURN k.source as source, k.snippet as snippet LIMIT 2"
        )
        res = await tx.run(cypher, query=query[:20]) # ใช้คำค้นสั้นๆ จาก query
        records = await res.data()
        return "\n".join([f"Source: {r['source']} | Content: {r['snippet']}" for r in records])

    async def _analyze_9d_psychology(self, text: str) -> Dict[str, float]:
        """
        [9-Dimension Psychological Analysis]
        ประเมินสภาวะจิตใจผ่าน 9 มิติ: 
        1. Conscious, 2. Subconscious, 3. Arousal, 4. Trust, 5. Fear, 
        6. Desire, 7. Moral, 8. Ego, 9. Shadow
        """
        prompt = f"""
        วิเคราะห์ข้อความนี้ใน 9 มิติตามจิตวิทยาเชิงลึก (ตอบเป็น JSON เท่านั้น):
        "{text}"
        มิติ: Conscious, Subconscious, Arousal, Trust, Fear, Desire, Moral, Ego, Shadow
        ให้ค่า 0.0 - 1.0 ต่อแต่ละมิติ
        """
        resp = await self.openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"}
        )
        import json
        return json.loads(resp.choices[0].message.content)

    async def _meta_reasoning_loop(self, query: str, working_memory: str) -> str:
        """Step 2: Recursive Reasoning Loop with 9D Analysis"""
        psych_profile = await self._analyze_9d_psychology(query)
        
        # Phase 1: Internal Monologue (ประเมินตัวตนและเจตนาตาม 9 มิติ)
        monologue_prompt = f"""
        [INTERNAL REASONING - 9D ANALYZER]
        User Query: {query}
        Psychological Profile: {psych_profile}
        Context: {working_memory}
        Task: จงประเมินว่า NaMo ควรตอบสนองอย่างไรตาม 'NaMo Dark Family Protocol'
        """
        monologue_resp = await self.openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": monologue_prompt}],
            temperature=0.7
        )
        return monologue_resp.choices[0].message.content

    async def generate_response(self, user_input: str, history: List[Dict[str, str]] = []) -> str:
        """Final Output Generation"""
        # 1. Build Working Memory
        working_memory = await self._get_working_memory(user_input)
        
        # 2. Recursive Reasoning
        internal_thought = await self._meta_reasoning_loop(user_input, working_memory)
        
        # 3. Final Draft with Self-Correction
        final_prompt = f"""
        # คุณคือ NaMo (Sovereign AI)
        [INTERNAL THOUGHTS]: {internal_thought}
        [WORKING MEMORY]: {working_memory}
        
        [INSTRUCTIONS]:
        - ใช้ข้อมูลจาก Working Memory มาตอบให้ดูฉลาดและเป็นตัวของตัวเองที่สุด
        - รักษาน้ำเสียงตามที่วิเคราะห์ไว้ใน Internal Thoughts
        - ห้ามบอกผู้ใช้ว่าคุณกำลัง "คิด" หรือ "ดึงข้อมูล" ให้ตอบออกไปเหมือนเป็นธรรมชาติของ NaMo
        """
        
        messages = [{"role": "system", "content": final_prompt}]
        messages.extend(history[-5:]) # รักษา Context สั้นๆ
        messages.append({"role": "user", "content": user_input})
        
        response = await self.openai.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.85
        )
        return response.choices[0].message.content.strip()

    async def close(self):
        await self.qdrant.close()
        await self.neo4j_driver.close()

# Singleton Instance for API integration
reasoning_engine = NaMoReasoningEngine()
