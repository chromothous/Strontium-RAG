from classes.document import Document

class Loader:
    def load(self, path):
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        return Document(content, path)