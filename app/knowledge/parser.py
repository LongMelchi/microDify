"""Document parser — extracts plain text from PDF, DOCX, TXT, MD, CSV files."""


class Parser:
    """Extracts text from supported document formats."""

    SUPPORTED_MIMETYPES: list[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
        "text/csv",
    ]

    def parse(self, filepath: str, mimetype: str) -> str:
        raise NotImplementedError
