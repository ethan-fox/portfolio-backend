from pydantic import BaseModel


class ContentView(BaseModel):
    content: str
    format: str = "markdown"
