# handlers/health_handlers.py - Health check endpoint handler

from config import QDRANT_COLLECTION_NAME
from services import qdrant_client

async def health_check():
    """Health check endpoint."""
    try:
        # Get collection info including indexes
        collection_info = qdrant_client.get_collection(QDRANT_COLLECTION_NAME)
        indexed_fields = []
        if hasattr(collection_info, 'payload_schema') and collection_info.payload_schema:
            indexed_fields = list(collection_info.payload_schema.keys())
        
        # Get optimization status
        optimization_status = {
            "quantization_enabled": hasattr(collection_info.config, 'quantization_config') and collection_info.config.quantization_config is not None,
            "hnsw_optimized": True,  # We always set custom HNSW params
            "multitenancy_optimized": "app_id" in indexed_fields and "project_id" in indexed_fields
        }
        
        return {
            "status": "healthy",
            "qdrant_connected": qdrant_client is not None,
            "collection": QDRANT_COLLECTION_NAME,
            "indexed_fields": indexed_fields,
            "points_count": collection_info.points_count if hasattr(collection_info, 'points_count') else "unknown",
            "optimizations": optimization_status
        }
    except Exception as e:
        return {
            "status": "error",
            "qdrant_connected": False,
            "error": str(e)
        } 