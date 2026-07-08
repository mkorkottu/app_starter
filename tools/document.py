from markitdown import MarkItDown, StreamInfo
from io import BytesIO
from pydantic import Field


def binary_document_to_markdown(
    binary_data: bytes = Field(description="Raw binary contents of the document to convert"),
    file_type: str = Field(description="File extension of the document, including the leading dot (e.g. '.docx', '.pdf')"),
) -> str:
    """Convert binary document data to markdown-formatted text.

    Reads raw document bytes (e.g. from a .docx or .pdf file) and returns
    their content as markdown text, preserving structure such as headings,
    lists, and tables where possible.

    When to use:
    - When you have a document's binary contents and need its text content
      as markdown for reading, summarizing, or further processing.
    - Supports formats handled by the markitdown library, including
      .docx and .pdf.

    When not to use:
    - When you already have plain text or markdown content.
    - For file formats not supported by markitdown.

    Examples:
    >>> with open("report.docx", "rb") as f:
    ...     data = f.read()
    >>> binary_document_to_markdown(data, ".docx")
    '# Report Title\\n\\nSome content...'
    """
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content
