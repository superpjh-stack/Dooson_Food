from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.local", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "두손푸드 AI-MES API"
    debug: bool = False

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "dooson_mes"
    db_user: str = "mes_user"
    db_password: str = ""

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Auth
    auth_secret: str = "change-me-in-production"
    auth_access_token_expire: int = 3600
    auth_refresh_token_expire: int = 604800

    # JWT
    jwt_secret: str = Field(default="change-me-in-production")
    jwt_expire_minutes: int = Field(default=60 * 24)  # 24 hours

    # Storage
    storage_endpoint: str = "http://localhost:9000"
    storage_access_key: str = ""
    storage_secret_key: str = ""
    storage_bucket_xray: str = "dooson-xray"
    storage_bucket_reports: str = "dooson-reports"

    # IoT / MQTT
    iot_mqtt_host: str = "localhost"
    iot_mqtt_port: int = 1883
    iot_mqtt_topic_prefix: str = "dooson/mes"

    # AI / LLM
    llm_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"
    ml_confidence_threshold: float = 0.6

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"]
    )


settings = Settings()
