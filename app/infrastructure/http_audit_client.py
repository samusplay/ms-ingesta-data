import os
import httpx

class HttpAuditClient:
    """Cliente HTTP para enviar eventos al microservicio de auditoría."""
    
    def __init__(self):
        # Asume que en Docker Compose ms-auditoria corre en el puerto 8000
        self.audit_url = os.getenv("AUDIT_API_URL", "http://ms-auditoria:8000/api/v1/events")

    async def send_audit_event(self, reference_id: str, trace_id: str, summary: str, status: str = "SUCCESS"):
        payload = {
            "event_type": "DATA_INGESTION_COMPLETED",
            "service_name": "ms-ingestion",
            "reference_id": str(reference_id),
            "trace_id": str(trace_id),
            "event_summary": summary,
            "status": status
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.audit_url, json=payload, timeout=5.0)
                response.raise_for_status()
            except Exception as e:
                print(f"⚠️ Error enviando evento a auditoría desde Ingesta: {e}")
