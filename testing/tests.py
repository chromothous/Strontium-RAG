
def green(text):
    return f"\033[32m{text}\033[0m"

def red(text):
    return f"\033[31m{text}\033[0m"

def full_test():
    tests = 0
    success = 0
    failure = 0

    try:
        tests += 1
        import classes
        import constants
        import testing
        print(green("Version 0.0.1 project foundation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.1 failed"))

    try:
        tests += 1
        from constants.rag import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K
        assert isinstance(CHUNK_SIZE, int)
        assert isinstance(CHUNK_OVERLAP, int)
        assert isinstance(TOP_K, int)
        assert CHUNK_SIZE > 0
        assert CHUNK_OVERLAP >= 0
        assert CHUNK_OVERLAP < CHUNK_SIZE
        assert TOP_K > 0
        print(green("Version 0.0.2 RAG constants are online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.2 failed"))

    try:
        tests += 1
        from classes.logger import Logger
        logger = Logger()
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        logger.info("Information message test.")
        logger.warning("Warning message test.")
        logger.error("Error message test.")
        print(green("Version 0.0.3 logger is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.3 failed"))

    try:
        tests += 1
        from classes.document import Document
        document = Document("This is test content.", "test.txt")
        assert document.content == "This is test content."
        assert document.source == "test.txt"
        print(green("Version 0.0.4 document is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.4 failed"))

    try:
        tests += 1
        from classes.document import Document
        document = Document("This is test content.", "test.txt")
        assert document.content == "This is test content."
        assert document.source == "test.txt"
        try:
            Document("", "test.txt")
            assert False
        except ValueError:
            pass
        try:
            Document("Test content.", "")
            assert False
        except ValueError:
            pass
        try:
            Document(123, "test.txt")
            assert False
        except ValueError:
            pass
        try:
            Document("Test content.", 123)
            assert False
        except ValueError:
            pass
        print(green("Version 0.0.5 document validation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.5 failed"))

    try:
        tests += 1
        from classes.document import Document
        document = Document("This is test content.", "test.txt", {"type": "text"})
        assert document.content == "This is test content."
        assert document.source == "test.txt"
        assert document.metadata == {"type": "text"}
        document = Document("This is test content.", "test.txt")
        assert document.metadata == {}
        try:
            Document("Test content.", "test.txt", "invalid")
            assert False
        except ValueError:
            pass
        print(green("Version 0.0.6 document metadata is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.6 failed"))

    try:
        tests += 1
        from classes.document import Document
        document = Document("This is test content.", "test.txt")
        assert document.id is not None
        assert isinstance(document.id, str)
        assert len(document.id) == 36
        document_two = Document("This is test content.", "test.txt")
        assert document.id != document_two.id
        print(green("Version 0.0.7 document identity is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.7 failed"))

    try:
        tests += 1
        from classes.document import Document
        document = Document("This is test content.", "test.txt", {"type": "text"})
        data = document.to_dict()
        assert isinstance(data, dict)
        assert data["id"] == document.id
        assert data["content"] == document.content
        assert data["source"] == document.source
        assert data["metadata"] == document.metadata
        print(green("Version 0.0.8 document serialization is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.8 failed"))

    try:
        tests += 1
        from classes.document import Document
        document = Document("This is test content.", "test.txt", {"type": "text"})
        data = document.to_dict()
        restored = Document.from_dict(data)
        assert isinstance(restored, Document)
        assert restored.id == document.id
        assert restored.content == document.content
        assert restored.source == document.source
        assert restored.metadata == document.metadata
        print(green("Version 0.0.9 document deserialization is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.9 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.document import Document
        from classes.logger import Logger
        logger = Logger()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as file:
            file.write("This is test document content.")
            path = file.name
        loader = Loader(logger)
        document = loader.load(path)
        assert isinstance(document, Document)
        assert document.content == "This is test document content."
        assert document.source == path
        os.remove(path)
        print(green("Version 0.0.10 text file loader is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.10 failed"))

    try:
        tests += 1
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        try:
            loader.load("")
            assert False
        except ValueError:
            pass
        try:
            loader.load("does_not_exist.txt")
            assert False
        except FileNotFoundError:
            pass
        print(green("Version 0.0.11 loader validation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.11 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as file:
            path = file.name
        try:
            loader.load(path)
            assert False
        except ValueError:
            pass
        os.remove(path)
        print(green("Version 0.0.12 empty document handling is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.12 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as file:
            file.write("This is a supported document.")
            txt_path = file.name
        document = loader.load(txt_path)
        assert document.content == "This is a supported document."
        os.remove(txt_path)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pdf", encoding="utf-8", delete=False) as file:
            file.write("This is an unsupported document.")
            pdf_path = file.name
        try:
            loader.load(pdf_path)
            assert False
        except ValueError:
            pass
        os.remove(pdf_path)
        print(green("Version 0.0.13 document type validation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.13 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as file:
            file.write("This is test document content.")
            path = file.name
        document = loader.load(path)
        assert document.metadata["file_name"] == os.path.basename(path)
        assert document.metadata["file_type"] == ".txt"
        assert document.metadata["file_size"] == len("This is test document content.".encode("utf-8"))
        os.remove(path)
        print(green("Version 0.0.14 loader metadata is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.14 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as file:
            file.write("This is a file reading test.")
            path = file.name
        content = loader.read_file(path)
        assert content == "This is a file reading test."
        document = loader.load(path)
        assert document.content == "This is a file reading test."
        os.remove(path)
        print(green("Version 0.0.15 loader file reading is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.15 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        path = os.path.join(tempfile.gettempdir(), "strontium_rag_missing_file.txt")
        if os.path.exists(path):
            os.remove(path)
        try:
            loader.read_file(path)
            assert False
        except FileNotFoundError:
            pass
        print(green("Version 0.0.16 loader error handling is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.16 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        path = os.path.join(tempfile.gettempdir(), "strontium_rag_missing_file.txt")
        if os.path.exists(path):
            os.remove(path)
        try:
            loader.read_file(path)
            assert False
        except FileNotFoundError:
            pass
        print(green("Version 0.0.17 loader read failure logging is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.17 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        assert loader.encoding == "utf-8"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as file:
            file.write("This document contains UTF-8 text: café.")
            path = file.name
        content = loader.read_file(path)
        assert content == "This document contains UTF-8 text: café."
        document = loader.load(path)
        assert document.content == "This document contains UTF-8 text: café."
        os.remove(path)
        print(green("Version 0.0.18 loader encoding handling is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.18 failed"))

    try:
        tests += 1
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        assert loader.encoding == "utf-8"
        custom_loader = Loader(logger, "utf-16")
        assert custom_loader.encoding == "utf-16"
        try:
            Loader(logger, "not-a-real-encoding")
            assert False
        except ValueError:
            pass
        try:
            Loader(logger, "")
            assert False
        except ValueError:
            pass
        try:
            Loader(logger, 123)
            assert False
        except ValueError:
            pass
        print(green("Version 0.0.19 loader encoding validation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.19 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        from classes.document import Document
        logger = Logger()
        loader = Loader(logger)
        paths = []
        for content in ["First document.", "Second document.", "Third document."]:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as file:
                file.write(content)
                paths.append(file.name)
        documents = loader.load_many(paths)
        assert isinstance(documents, list)
        assert len(documents) == 3
        assert all(isinstance(document, Document) for document in documents)
        assert documents[0].content == "First document."
        assert documents[1].content == "Second document."
        assert documents[2].content == "Third document."
        for path in paths:
            os.remove(path)
        assert loader.load_many([]) == []
        try:
            loader.load_many("not-a-list")
            assert False
        except ValueError:
            pass
        print(green("Version 0.0.20 loader batch loading is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.20 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        from classes.document import Document
        logger = Logger()
        loader = Loader(logger)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as file:
            file.write("Valid document.")
            valid_path = file.name
        invalid_path = os.path.join(tempfile.gettempdir(), "strontium_rag_missing_0_0_21.txt")
        if os.path.exists(invalid_path):
            os.remove(invalid_path)
        documents = loader.load_many([valid_path, invalid_path])
        assert isinstance(documents, list)
        assert len(documents) == 1
        assert isinstance(documents[0], Document)
        assert documents[0].content == "Valid document."
        os.remove(valid_path)
        assert loader.load_many([invalid_path]) == []
        print(green("Version 0.0.21 loader batch failure handling is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.21 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as file:
            file.write("First document.")
            valid_path = file.name
        invalid_path = os.path.join(tempfile.gettempdir(), "strontium_rag_missing_0_0_22.txt")
        if os.path.exists(invalid_path):
            os.remove(invalid_path)
        documents = loader.load_many([valid_path, invalid_path])
        assert len(documents) == 1
        assert loader.last_batch_stats["attempted"] == 2
        assert loader.last_batch_stats["successful"] == 1
        assert loader.last_batch_stats["failed"] == 1
        loader.load_many([])
        assert loader.last_batch_stats["attempted"] == 0
        assert loader.last_batch_stats["successful"] == 0
        assert loader.last_batch_stats["failed"] == 0
        os.remove(valid_path)
        print(green("Version 0.0.22 loader batch statistics are online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.22 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as file:
            file.write("Batch statistics test.")
            valid_path = file.name
        invalid_path = os.path.join(tempfile.gettempdir(), "strontium_rag_missing_0_0_23.txt")
        if os.path.exists(invalid_path):
            os.remove(invalid_path)
        loader.load_many([valid_path, invalid_path])
        stats = loader.get_batch_stats()
        assert isinstance(stats, dict)
        assert stats == {
            "attempted": 2,
            "successful": 1,
            "failed": 1
        }
        stats["attempted"] = 999
        assert loader.get_batch_stats()["attempted"] == 2
        os.remove(valid_path)
        print(green("Version 0.0.23 loader batch statistics access is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.23 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        with tempfile.TemporaryDirectory() as directory:
            txt_path = os.path.join(directory, "document.txt")
            pdf_path = os.path.join(directory, "document.pdf")
            other_path = os.path.join(directory, "notes.md")
            with open(txt_path, "w", encoding="utf-8") as file:
                file.write("Text document.")
            with open(pdf_path, "w", encoding="utf-8") as file:
                file.write("PDF placeholder.")
            with open(other_path, "w", encoding="utf-8") as file:
                file.write("Markdown placeholder.")
            paths = loader.find_files(directory)
            assert isinstance(paths, list)
            assert len(paths) == 1
            assert paths[0] == txt_path
        try:
            loader.find_files("")
            assert False
        except ValueError:
            pass
        missing_directory = os.path.join(tempfile.gettempdir(), "strontium_rag_missing_directory_0_0_24")
        if os.path.exists(missing_directory):
            os.rmdir(missing_directory)
        try:
            loader.find_files(missing_directory)
            assert False
        except FileNotFoundError:
            pass
        print(green("Version 0.0.24 loader directory discovery is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.24 failed"))

    if failure > 0:
        print(red(f"There was {failure} failures, please fix."))
    else:
        print(green(f"All versions online! {success}/{tests}"))