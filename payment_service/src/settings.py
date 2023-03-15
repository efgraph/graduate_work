from pydantic.env_settings import BaseSettings


class PostgresSettings(BaseSettings):
    user = "postgres"
    password = "password"
    host = "localhost"
    port = 5432
    db_payment = "payment"

    @property
    def dsn(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_payment}"

    class Config:
        env_prefix = "POSTGRES_"


class StripeSettings(BaseSettings):
    publishable_key = ""
    secret_key = ""

    class Config:
        env_prefix = "STRIPE_"


class Settings(BaseSettings):
    postgres = PostgresSettings()
    stripe = StripeSettings()


settings = Settings()
