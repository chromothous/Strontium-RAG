import uuid

class Document:
    def __init__(self, content, source, metadata=None):
        if not isinstance(content, str) or not content:
            raise ValueError("Document content must be a non-empty string")
        if not isinstance(source, str) or not source:
            raise ValueError("Document source must be a non-empty string")
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("Document metadata must be a dictionary")
        self.id = str(uuid.uuid4())
        self.content = content
        self.source = source
        self.metadata = metadata if metadata is not None else {}