import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env file if present


class Settings:
    PROJECT_NAME: str = "MindSpace"
    MYSQL_USER: str = os.getenv("MYSQL_USER", "your_username")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "your_password")
    MYSQL_SERVER: str = os.getenv("MYSQL_SERVER", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "mindspace_db")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )


settings = Settings()
