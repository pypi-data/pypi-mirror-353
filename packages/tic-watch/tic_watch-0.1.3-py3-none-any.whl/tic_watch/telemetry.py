from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry import trace
from jwt import decode as jwt_decode, InvalidTokenError
import os

def init_monitoring(app: FastAPI, service_name: str, connection_string: str):
    # Step 1: Setup basic tracing
    resource = Resource.create({SERVICE_NAME: service_name})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Step 2: Create Azure Monitor Exporter
    exporter = AzureMonitorTraceExporter(connection_string=connection_string)
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

    # Step 3: Middleware to extract token and inject user info
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
                    user_id = "invalid"

            # Store in request.state
            request.state.user_id = user_id

            # Inject into span context
            span = trace.get_current_span()
            if span:
                span.set_attribute("app.user_id", user_id)  # Custom dimension
                # Set Azure Application Insights-recognized user_Id
                span.set_attribute("ai.user.id", user_id)    # ✅ This is key

            return await call_next(request)

    # Step 4: Attach middleware before OpenTelemetry
    app.add_middleware(UserContextMiddleware)
    FastAPIInstrumentor.instrument_app(app)
    app.add_middleware(OpenTelemetryMiddleware)

    @app.on_event("startup")
    async def startup_event():
        print(f"✅ Monitoring initialized for: {service_name}")
