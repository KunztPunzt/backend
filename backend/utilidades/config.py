from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
# Cargar .env y descarta cualquier clave extra
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

# Cada campo apunta a su variable de entorno mediante alias
    database_url: str            = Field(alias="DATABASE_URL")
    secret_key: str              = Field(alias="SECRET_KEY")
    jwt_algorithm: str           = Field(alias="ALGORITHM")
    jwt_expiration_hours: int    = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    mail_username: str           = Field(alias="MAIL_USERNAME")
    mail_password: str           = Field(alias="MAIL_PASSWORD")
    mail_from: str               = Field(alias="MAIL_FROM")
    mail_server: str             = Field(alias="MAIL_SERVER")
    mail_from_name: str          = Field(alias="MAIL_FROM_NAME")
    mail_port: int               = Field(alias="MAIL_PORT")

# Instancia una sola vez, al importar
settings = Settings()
