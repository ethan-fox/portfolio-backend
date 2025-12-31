from pathlib import Path

from src.model.view.content_view import ContentView


class ContentService:
    def __init__(self, content_dir: str = "static"):
        self.content_dir = Path(content_dir).resolve()

    def get_about(self) -> ContentView | None:
        file_path = self.content_dir / "about.md"

        if not file_path.exists() or not file_path.is_file():
            return None

        content = file_path.read_text(encoding="utf-8")

        return ContentView(content=content, format="markdown")

    def get_how_to_play(self) -> ContentView | None:
        file_path = self.content_dir / "how-to-play.md"

        if not file_path.exists() or not file_path.is_file():
            return None

        content = file_path.read_text(encoding="utf-8")

        return ContentView(content=content, format="markdown")
