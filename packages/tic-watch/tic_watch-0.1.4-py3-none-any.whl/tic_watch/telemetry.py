from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry import trace
from opentelemetry.sdk.trace import Span  # Needed to ensure we have SDK span
from jwt import decode as jwt_decode, InvalidTokenError
import os

def init_monitoring(app: FastAPI, service_name: str, connection_string: str):
    # Step 1: Set up OpenTelemetry Tracer
    resource = Resource.create({SERVICE_NAME: service_name})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Step 2: Configure Azure Monitor exporter
    exporter = AzureMonitorTraceExporter(connection_string=connection_string)
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

    # Step 3: Middleware to extract user ID from JWT and enrich telemetry
    class UserContextMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            user_id = "unknown"
            secret_key = os.getenv("secret_key")

            if token and secret_key:
                try:
                    payload = jwt_decode(token, secret_key, algorithms=["HS256"])
                    user_id = payload.get("sub") or payload.get("username", "unknown")
                except InvalidTokenError:
                    user_id = "unauthenticated"

            # Save in request state (optional for later use in routes)
            request.state.user_id = user_id

            # Inject into OpenTelemetry span attributes
            span = trace.get_current_span()
            if isinstance(span, Span):
                span.set_attribute("enduser.id", user_id)     # ✅ used by Azure for user_Id
                span.set_attribute("app.user_id", user_id)     # Optional: for customDimensions

            return await call_next(request)

    # Step 4: Register middlewares
    app.add_middleware(UserContextMiddleware)         # Your JWT user-enrichment middleware
    FastAPIInstrumentor.instrument_app(app)           # Auto-instrument FastAPI
    app.add_middleware(OpenTelemetryMiddleware)       # ASGI-level tracing

    @app.on_event("startup")
    async def startup_event():
        print(f"✅ Monitoring initialized for: {service_name}")
