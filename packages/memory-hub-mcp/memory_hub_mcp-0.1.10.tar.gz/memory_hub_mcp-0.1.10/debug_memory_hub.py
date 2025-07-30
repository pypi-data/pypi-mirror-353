#!/usr/bin/env python3
"""
Debug script to test Memory Hub components individually
"""

import asyncio
import httpx
import sys
sys.path.append('src')

from memory_hub.core.services import AppConfig, get_embedding, startup_event
from memory_hub.core.chunking import create_semantic_chunker
from memory_hub.core.models import MemoryItemIn
from memory_hub.core.handlers.memory_handlers import add_memory


async def test_chunking():
    """Test semantic chunking directly"""
    print("=== Testing Chunking ===")
    try:
        chunker = create_semantic_chunker(chunk_size=90)
        test_content = "This is a test content for debugging chunking embedding failure. It should be chunked properly."
        chunks = chunker(test_content)
        print(f"✓ Chunking successful: {len(chunks)} chunks generated")
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i}: {chunk[:50]}...")
        return chunks
    except Exception as e:
        print(f"✗ Chunking failed: {e}")
        return None


async def test_embedding(config: AppConfig):
    """Test embedding service directly"""
    print("\n=== Testing Embedding ===")
    try:
        async with httpx.AsyncClient() as client:
            test_text = "This is a test text for embedding"
            embedding = await get_embedding(test_text, client, config)
            print(f"✓ Embedding successful: {len(embedding)} dimensions")
            print(f"  First 5 values: {embedding[:5]}")
            return embedding
    except Exception as e:
        print(f"✗ Embedding failed: {e}")
        return None


async def test_qdrant_connection(config: AppConfig):
    """Test Qdrant connection"""
    print("\n=== Testing Qdrant Connection ===")
    try:
        await startup_event(config)
        collections = config.qdrant_client.get_collections()
        print(f"✓ Qdrant connection successful: {len(collections.collections)} collections")
        for collection in collections.collections:
            print(f"  Collection: {collection.name}")
        return True
    except Exception as e:
        print(f"✗ Qdrant connection failed: {e}")
        return False


async def test_full_add_memory(config: AppConfig):
    """Test full add_memory workflow"""
    print("\n=== Testing Full Add Memory ===")
    try:
        memory_item = MemoryItemIn(
            content="This is a debug test content for memory hub debugging. It contains enough text to test chunking and embedding.",
            metadata={
                "app_id": "DEBUG_TEST",
                "project_id": "chunking_embedding_debug",
                "type": "DEBUG_LOG_ANALYSIS"
            }
        )
        result = await add_memory(memory_item, config)
        print(f"✓ Add memory successful: {result.message}")
        return result
    except Exception as e:
        print(f"✗ Add memory failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Main test function"""
    print("Memory Hub Debug Test")
    print("=" * 50)
    
    # Create config
    config = AppConfig(
        qdrant_url="http://192.168.0.90:6333",
        lm_studio_url="http://192.168.0.90:1234/v1"
    )
    
    # Initialize HTTP client
    config.http_client = httpx.AsyncClient()
    
    try:
        # Test individual components
        chunks = await test_chunking()
        embedding = await test_embedding(config)
        qdrant_ok = await test_qdrant_connection(config)
        
        # If all components work, test full workflow
        if chunks and embedding and qdrant_ok:
            print("\n=== All components working, testing full workflow ===")
            await test_full_add_memory(config)
        else:
            print("\n=== Component failures detected ===")
            
    finally:
        await config.http_client.aclose()


if __name__ == "__main__":
    asyncio.run(main()) 