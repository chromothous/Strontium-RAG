class Document:
    def __init__(self, content, source):
        if not isinstance(content, str) or not content:
            raise ValueError("Document content must be a non-empty string")
        if not isinstance(source, str) or not source:
            raise ValueError("Document source must be a non-empty string")
        self.content = content
        self.source = source