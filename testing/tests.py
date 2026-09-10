
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
        assert isinstance(CHUNK_SIZE, int), "CHUNK_SIZE should be an integer"
        assert isinstance(CHUNK_OVERLAP, int), "CHUNK_OVERLAP should be an integer"
        assert isinstance(TOP_K, int), "TOP_K should be an integer"
        assert CHUNK_SIZE > 0, "CHUNK_SIZE should be greater than zero"
        assert CHUNK_OVERLAP >= 0, "CHUNK_OVERLAP should not be negative"
        assert CHUNK_OVERLAP < CHUNK_SIZE, "CHUNK_OVERLAP should be smaller than CHUNK_SIZE"
        assert TOP_K > 0, "TOP_K should be greater than zero"
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
        assert logger is not None, "Logger should be instantiated successfully"
        assert hasattr(logger, "info"), "Logger should provide an info method"
        assert hasattr(logger, "warning"), "Logger should provide a warning method"
        assert hasattr(logger, "error"), "Logger should provide an error method"
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
        assert document.content == "This is test content.", "Document content should match the supplied content"
        assert document.source == "test.txt", "Document source should match the supplied source"
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
        assert document.content == "This is test content.", "Document content should match the supplied content"
        assert document.source == "test.txt", "Document source should match the supplied source"
        try:
            Document("", "test.txt")
            assert False, "Expected ValueError was not raised"
        except ValueError:
            pass
        try:
            Document("Test content.", "")
            assert False, "Expected ValueError was not raised"
        except ValueError:
            pass
        try:
            Document(123, "test.txt")
            assert False, "Expected ValueError was not raised"
        except ValueError:
            pass
        try:
            Document("Test content.", 123)
            assert False, "Expected ValueError was not raised"
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
        assert document.content == "This is test content.", "Document content should match the supplied content"
        assert document.source == "test.txt", "Document source should match the supplied source"
        assert document.metadata == {"type": "text"}, "Document should preserve supplied metadata"
        document = Document("This is test content.", "test.txt")
        assert document.metadata == {}, "Document without metadata should default to an empty dictionary"
        try:
            Document("Test content.", "test.txt", "invalid")
            assert False, "Expected ValueError was not raised"
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
        assert document.id is not None, "Document should receive an ID"
        assert isinstance(document.id, str), "Document ID should be a string"
        assert len(document.id) == 36, "Document ID should have the expected UUID string length"
        document_two = Document("This is test content.", "test.txt")
        assert document.id != document_two.id, "Separate documents should receive unique IDs"
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
        assert isinstance(data, dict), "Serialized document data should be a dictionary"
        assert data["id"] == document.id, "Serialized data should preserve the document ID"
        assert data["content"] == document.content, "Serialized data should preserve document content"
        assert data["source"] == document.source, "Serialized data should preserve document source"
        assert data["metadata"] == document.metadata, "Serialized data should preserve document metadata"
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
        assert isinstance(restored, Document), "Deserialized data should produce a Document"
        assert restored.id == document.id, "Deserialization should preserve the document ID"
        assert restored.content == document.content, "Deserialization should preserve document content"
        assert restored.source == document.source, "Deserialization should preserve document source"
        assert restored.metadata == document.metadata, "Deserialization should preserve document metadata"
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
        assert isinstance(document, Document), "Loaded data should produce a Document"
        assert document.content == "This is test document content.", "Loaded document content should match the file content"
        assert document.source == path, "Loaded document source should match the file path"
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
            assert False, "Expected ValueError was not raised"
        except ValueError:
            pass
        try:
            loader.load("does_not_exist.txt")
            assert False, "Expected expected exception was not raised"
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
            assert False, "Expected expected ValueError was not raised"
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
        assert document.content == "This is a supported document.", "Loaded supported document should preserve its content"
        os.remove(txt_path)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pdf", encoding="utf-8", delete=False) as file:
            file.write("This is an unsupported document.")
            pdf_path = file.name
        try:
            loader.load(pdf_path)
            assert False, "Expected expected ValueError was not raised"
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
        assert document.metadata["file_name"] == os.path.basename(path), "Loader metadata should contain the source file name"
        assert document.metadata["file_type"] == ".txt", "Loader metadata should contain the .txt file type"
        assert document.metadata["file_size"] == len("This is test document content.".encode("utf-8")), "Loader metadata should contain the file size in bytes"
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
        assert content == "This is a file reading test.", "read_file should return the exact file content"
        document = loader.load(path)
        assert document.content == "This is a file reading test.", "Loaded document should preserve the file content"
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
            assert False, "Expected expected exception was not raised"
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
            assert False, "Expected expected exception was not raised"
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
        assert loader.encoding == "utf-8", "Loader should default to UTF-8 encoding"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as file:
            file.write("This document contains UTF-8 text: café.")
            path = file.name
        content = loader.read_file(path)
        assert content == "This document contains UTF-8 text: café.", "read_file should preserve UTF-8 content"
        document = loader.load(path)
        assert document.content == "This document contains UTF-8 text: café.", "Loaded document should preserve UTF-8 content"
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
        assert loader.encoding == "utf-8", "Loader should default to UTF-8 encoding"
        custom_loader = Loader(logger, "utf-16")
        assert custom_loader.encoding == "utf-16", "Loader should preserve a valid custom encoding"
        try:
            Loader(logger, "not-a-real-encoding")
            assert False, "Expected expected ValueError was not raised"
        except ValueError:
            pass
        try:
            Loader(logger, "")
            assert False, "Expected expected ValueError was not raised"
        except ValueError:
            pass
        try:
            Loader(logger, 123)
            assert False, "Expected expected ValueError was not raised"
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
        assert isinstance(documents, list), "Batch loading should return a list"
        assert len(documents) == 3, "Batch loading should return all three valid documents"
        assert all(isinstance(document, Document) for document in documents), "Every batch-loaded item should be a Document"
        assert documents[0].content == "First document.", "First batch document should preserve its content"
        assert documents[1].content == "Second document.", "Second batch document should preserve its content"
        assert documents[2].content == "Third document.", "Third batch document should preserve its content"
        for path in paths:
            os.remove(path)
        assert loader.load_many([]) == [], "Batch loading an empty list should return an empty list"
        try:
            loader.load_many("not-a-list")
            assert False, "Expected ValueError was not raised"
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
        assert isinstance(documents, list), "Batch loading should return a list"
        assert len(documents) == 1, "Batch loading should return only the valid document when one path fails"
        assert isinstance(documents[0], Document)
        assert documents[0].content == "Valid document.", "Successful batch loading should preserve the valid document content"
        os.remove(valid_path)
        assert loader.load_many([invalid_path]) == [], "Batch loading should return no documents when all paths fail"
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
        assert len(documents) == 1, "Batch loading should return only the valid document when one path fails"
        assert loader.last_batch_stats["attempted"] == 2, "Batch statistics should record both attempted paths"
        assert loader.last_batch_stats["successful"] == 1, "Batch statistics should record one successful load"
        assert loader.last_batch_stats["failed"] == 1, "Batch statistics should record one failed load"
        loader.load_many([])
        assert loader.last_batch_stats["attempted"] == 0, "Empty batch statistics should record zero attempted paths"
        assert loader.last_batch_stats["successful"] == 0, "Empty batch statistics should record zero successful loads"
        assert loader.last_batch_stats["failed"] == 0, "Empty batch statistics should record zero failed loads"
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
        assert isinstance(stats, dict), "Batch statistics access should return a dictionary"
        assert stats == {
            "attempted": 2,
            "successful": 1,
            "failed": 1
        }, "Batch statistics should accurately report attempted, successful, and failed loads"
        stats["attempted"] = 999
        assert loader.get_batch_stats()["attempted"] == 2, "Changing returned statistics should not modify Loader statistics"
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
            assert len(paths) == 1, "File discovery should return only the supported text file"
            assert paths[0] == txt_path, "File discovery should return the supported text file path"
        try:
            loader.find_files("")
            assert False, "Expected ValueError was not raised"
        except ValueError:
            pass
        missing_directory = os.path.join(tempfile.gettempdir(), "strontium_rag_missing_directory_0_0_24")
        if os.path.exists(missing_directory):
            os.rmdir(missing_directory)
        try:
            loader.find_files(missing_directory)
            assert False, "Expected expected exception was not raised"
        except FileNotFoundError:
            pass
        print(green("Version 0.0.24 loader directory discovery is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.24 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        with tempfile.TemporaryDirectory() as directory:
            root_path = os.path.join(directory, "root.txt")
            nested_directory = os.path.join(directory, "nested")
            deep_directory = os.path.join(nested_directory, "deep")
            os.makedirs(deep_directory)
            nested_path = os.path.join(nested_directory, "nested.txt")
            deep_path = os.path.join(deep_directory, "deep.txt")
            unsupported_path = os.path.join(deep_directory, "notes.md")
            with open(root_path, "w", encoding="utf-8") as file:
                file.write("Root document.")
            with open(nested_path, "w", encoding="utf-8") as file:
                file.write("Nested document.")
            with open(deep_path, "w", encoding="utf-8") as file:
                file.write("Deep document.")
            with open(unsupported_path, "w", encoding="utf-8") as file:
                file.write("Unsupported document.")
            paths = loader.find_files(directory)
            assert isinstance(paths, list)
            assert len(paths) == 3, "Recursive discovery should find all three text files"
            assert root_path in paths, "Recursive discovery should include the root-level text file"
            assert nested_path in paths, "Recursive discovery should include the nested text file"
            assert deep_path in paths, "Recursive discovery should include the deeply nested text file"
            assert unsupported_path not in paths, "Recursive discovery should exclude unsupported file types"
        print(green("Version 0.0.25 recursive directory discovery is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.25 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        with tempfile.TemporaryDirectory() as directory:
            nested_directory = os.path.join(directory, "nested")
            os.makedirs(nested_directory)
            paths_to_create = [
                os.path.join(directory, "z.txt"),
                os.path.join(directory, "a.txt"),
                os.path.join(nested_directory, "m.txt")
            ]
            for path in paths_to_create:
                with open(path, "w", encoding="utf-8") as file:
                    file.write("Test document.")
            paths = loader.find_files(directory)
            assert paths == sorted(paths), "File discovery should return paths in sorted order"
            assert paths == [
                os.path.join(directory, "a.txt"),
                os.path.join(nested_directory, "m.txt"),
                os.path.join(directory, "z.txt")
            ], "File discovery should return paths in the expected deterministic order"
        print(green("Version 0.0.26 deterministic file discovery is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.26 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.ingestion import Ingestion
        from classes.loader import Loader
        from classes.logger import Logger
        from classes.document import Document
        logger = Logger()
        loader = Loader(logger)
        ingestion = Ingestion(loader, logger)
        assert ingestion.loader is loader, "Ingestion should retain the supplied Loader"
        assert ingestion.logger is logger, "Ingestion should retain the supplied Logger"
        with tempfile.TemporaryDirectory() as directory:
            nested_directory = os.path.join(directory, "nested")
            os.makedirs(nested_directory)
            first_path = os.path.join(directory, "first.txt")
            second_path = os.path.join(nested_directory, "second.txt")
            unsupported_path = os.path.join(directory, "notes.md")
            with open(first_path, "w", encoding="utf-8") as file:
                file.write("First document.")
            with open(second_path, "w", encoding="utf-8") as file:
                file.write("Second document.")
            with open(unsupported_path, "w", encoding="utf-8") as file:
                file.write("Unsupported document.")
            documents = ingestion.ingest_directory(directory)
            assert isinstance(documents, list), "Directory ingestion should return a list"
            assert len(documents) == 2, "Directory ingestion should load both supported documents"
            assert all(isinstance(document, Document) for document in documents), "Every ingested item should be a Document"
            assert documents[0].source == first_path, "First ingested document should come from the first discovered file"
            assert documents[1].source == second_path, "Second ingested document should come from the second discovered file"
            assert documents[0].content == "First document.", "First ingested document should preserve its content"
            assert documents[1].content == "Second document.", "Second ingested document should preserve its content"
        print(green("Version 0.0.27 ingestion orchestration is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.27 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.ingestion import Ingestion
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        ingestion = Ingestion(loader, logger)
        with tempfile.TemporaryDirectory() as directory:
            first_file = os.path.join(directory, "first.txt")
            second_file = os.path.join(directory, "second.txt")
            failed_file = os.path.join(directory, "failed.txt")
            with open(first_file, "w", encoding="utf-8") as file:
                file.write("First test document.")
            with open(second_file, "w", encoding="utf-8") as file:
                file.write("Second test document.")
            with open(failed_file, "w", encoding="utf-8") as file:
                file.write("")
            documents = ingestion.ingest_directory(directory)
            stats = ingestion.get_ingestion_stats()
            assert isinstance(documents, list), "Ingestion should return documents as a list"
            assert len(documents) == 2, "Ingestion should return all successfully loaded documents"
            assert isinstance(stats, dict), "Ingestion statistics should be returned as a dictionary"
            assert stats == {
                "attempted": 3,
                "successful": 2,
                "failed": 1
            }, "Ingestion statistics should accurately reflect successful and failed documents"
            assert stats is not loader.last_batch_stats, "Ingestion statistics should return a copy rather than the Loader's internal dictionary"
        print(green("Version 0.0.28 ingestion statistics are online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.28 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.ingestion import Ingestion
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        ingestion = Ingestion(loader, logger)
        with tempfile.TemporaryDirectory() as directory:
            first_file = os.path.join(directory, "first.txt")
            second_file = os.path.join(directory, "second.txt")
            failed_file = os.path.join(directory, "failed.txt")
            with open(first_file, "w", encoding="utf-8") as file:
                file.write("First test document.")
            with open(second_file, "w", encoding="utf-8") as file:
                file.write("Second test document.")
            with open(failed_file, "w", encoding="utf-8") as file:
                file.write("")
            documents = ingestion.ingest_directory(directory)
            stats = ingestion.get_ingestion_stats()
            failures = ingestion.get_ingestion_failures()
            assert isinstance(documents, list), "Ingestion should return documents as a list"
            assert len(documents) == 2, "Ingestion should return all successfully loaded documents"
            assert stats == {
                "attempted": 3,
                "successful": 2,
                "failed": 1
            }, "Ingestion statistics should accurately reflect successful and failed documents"
            assert isinstance(failures, list), "Ingestion failures should be returned as a list"
            assert len(failures) == 1, "Ingestion should record exactly one failed document"
            assert failures[0]["path"] == failed_file, "Ingestion failure should identify the failed file path"
            assert "error" in failures[0], "Ingestion failure should contain an error message"
            assert failures[0]["error"], "Ingestion failure should contain a non-empty error message"
        with tempfile.TemporaryDirectory() as directory:
            successful_file = os.path.join(directory, "successful.txt")
            with open(successful_file, "w", encoding="utf-8") as file:
                file.write("Successful test document.")
            ingestion.ingest_directory(directory)
            failures = ingestion.get_ingestion_failures()
            assert failures == [], "Ingestion failures should be empty when all documents load successfully"
        print(green("Version 0.0.29 ingestion failure tracking is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.29 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.ingestion import Ingestion
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        ingestion = Ingestion(loader, logger)
        with tempfile.TemporaryDirectory() as directory:
            first_file = os.path.join(directory, "a.txt")
            failed_file = os.path.join(directory, "b.txt")
            third_file = os.path.join(directory, "c.txt")
            with open(first_file, "w", encoding="utf-8") as file:
                file.write("First document.")
            with open(failed_file, "w", encoding="utf-8") as file:
                file.write("")
            with open(third_file, "w", encoding="utf-8") as file:
                file.write("Third document.")
            documents = ingestion.ingest_directory(directory)
            stats = ingestion.get_ingestion_stats()
            failures = ingestion.get_ingestion_failures()
            assert len(documents) == 2, "Ingestion should continue loading documents after a failure"
            assert documents[0].source == first_file, "First successful document should be returned in discovery order"
            assert documents[1].source == third_file, "Documents after a failure should still be loaded"
            assert stats["attempted"] == 3, "Ingestion should attempt every discovered document"
            assert stats["successful"] == 2, "Ingestion should count both successful documents"
            assert stats["failed"] == 1, "Ingestion should count the failed document"
            assert len(failures) == 1, "Ingestion should record the failed document without stopping the batch"
            assert failures[0]["path"] == failed_file, "Recorded failure should identify the document that failed"
        print(green("Version 0.0.30 ingestion failure isolation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.30 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.ingestion import Ingestion
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        ingestion = Ingestion(loader, logger)
        with tempfile.TemporaryDirectory() as first_directory:
            first_file = os.path.join(first_directory, "failed.txt")
            with open(first_file, "w", encoding="utf-8") as file:
                file.write("")
            ingestion.ingest_directory(first_directory)
            first_failures = ingestion.get_ingestion_failures()
            assert len(first_failures) == 1, "First ingestion should record its failed document"
        with tempfile.TemporaryDirectory() as second_directory:
            second_file = os.path.join(second_directory, "successful.txt")
            with open(second_file, "w", encoding="utf-8") as file:
                file.write("Successful document.")
            documents = ingestion.ingest_directory(second_directory)
            second_failures = ingestion.get_ingestion_failures()
            stats = ingestion.get_ingestion_stats()
            assert len(documents) == 1, "Second ingestion should load its successful document"
            assert second_failures == [], "Second ingestion should not retain failures from the previous ingestion"
            assert stats == {
                "attempted": 1,
                "successful": 1,
                "failed": 0
            }, "Second ingestion statistics should completely replace the previous ingestion statistics"
        print(green("Version 0.0.31 ingestion state consistency is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.31 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.ingestion import Ingestion
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        ingestion = Ingestion(loader, logger)
        try:
            ingestion.ingest_directory("")
            assert False, "Ingestion should reject an empty directory path"
        except ValueError:
            pass
        missing_directory = os.path.join(tempfile.gettempdir(), "strontium_rag_missing_directory_0_0_32")
        if os.path.isdir(missing_directory):
            os.rmdir(missing_directory)
        try:
            ingestion.ingest_directory(missing_directory)
            assert False, "Ingestion should reject a directory path that does not exist"
        except FileNotFoundError:
            pass
        try:
            ingestion.ingest_directory(123)
            assert False, "Ingestion should reject non-string directory paths"
        except ValueError:
            pass
        assert ingestion.get_ingestion_failures() == [], "Invalid ingestion runs should not create document failures"
        with tempfile.TemporaryDirectory() as directory:
            documents = ingestion.ingest_directory(directory)
            assert documents == [], "Ingestion should return an empty document list for an empty directory"
            assert ingestion.get_ingestion_stats() == {
                "attempted": 0,
                "successful": 0,
                "failed": 0
            }, "Empty directory ingestion should produce zeroed statistics"
        print(green("Version 0.0.32 ingestion directory validation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.32 failed"))

    try:
        tests += 1
        from classes.ingestion import Ingestion
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        ingestion = Ingestion(loader, logger)
        assert ingestion.loader is loader, "Ingestion should retain the exact Loader instance provided during construction"
        assert ingestion.logger is logger, "Ingestion should retain the exact Logger instance provided during construction"
        try:
            Ingestion(None, logger)
            assert False, "Ingestion should reject a missing Loader dependency"
        except ValueError:
            pass
        try:
            Ingestion(loader, None)
            assert False, "Ingestion should reject a missing Logger dependency"
        except ValueError:
            pass
        try:
            Ingestion("invalid", logger)
            assert False, "Ingestion should reject a non-Loader dependency"
        except ValueError:
            pass
        try:
            Ingestion(loader, "invalid")
            assert False, "Ingestion should reject a non-Logger dependency"
        except ValueError:
            pass
        print(green("Version 0.0.33 ingestion dependency consistency is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.33 failed"))

    try:
        tests += 1
        import os
        import tempfile
        from classes.ingestion import Ingestion
        from classes.loader import Loader
        from classes.logger import Logger
        logger = Logger()
        loader = Loader(logger)
        ingestion = Ingestion(loader, logger)
        with tempfile.TemporaryDirectory() as directory:
            nested_directory = os.path.join(directory, "nested")
            os.mkdir(nested_directory)
            first_file = os.path.join(directory, "a.txt")
            failed_file = os.path.join(directory, "b.txt")
            nested_file = os.path.join(nested_directory, "c.txt")
            ignored_file = os.path.join(directory, "ignored.pdf")
            with open(first_file, "w", encoding="utf-8") as file:
                file.write("First document.")
            with open(failed_file, "w", encoding="utf-8") as file:
                file.write("")
            with open(nested_file, "w", encoding="utf-8") as file:
                file.write("Nested document.")
            with open(ignored_file, "w", encoding="utf-8") as file:
                file.write("This file should not be discovered.")
            documents = ingestion.ingest_directory(directory)
            stats = ingestion.get_ingestion_stats()
            failures = ingestion.get_ingestion_failures()
            assert isinstance(documents, list), "Complete ingestion should return documents as a list"
            assert len(documents) == 2, "Complete ingestion should return every successfully loaded document"
            assert documents[0].source == first_file, "Documents should preserve deterministic discovery order"
            assert documents[1].source == nested_file, "Nested documents should be included in deterministic discovery order"
            assert stats == {
                "attempted": 3,
                "successful": 2,
                "failed": 1
            }, "Complete ingestion statistics should accurately reflect the entire ingestion run"
            assert len(failures) == 1, "Complete ingestion should expose the failed document"
            assert failures[0]["path"] == failed_file, "Complete ingestion should identify the failed document"
            assert ignored_file not in [document.source for document in documents], "Unsupported file types should not enter the ingestion pipeline"
        with tempfile.TemporaryDirectory() as directory:
            successful_file = os.path.join(directory, "successful.txt")
            with open(successful_file, "w", encoding="utf-8") as file:
                file.write("Clean second ingestion.")
            documents = ingestion.ingest_directory(directory)
            stats = ingestion.get_ingestion_stats()
            failures = ingestion.get_ingestion_failures()
            assert len(documents) == 1, "A new ingestion run should load its new document"
            assert stats == {
                "attempted": 1,
                "successful": 1,
                "failed": 0
            }, "A new ingestion run should completely replace previous statistics"
            assert failures == [], "A new successful ingestion run should completely clear previous failures"
        print(green("Version 0.0.34 complete ingestion pipeline is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.0.34 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.preprocessor import Preprocessor
        logger = Logger()
        preprocessor = Preprocessor(logger)
        document = Document("This is a test document.", "test.txt")
        processed = preprocessor.process(document)
        assert isinstance(processed, Document), "Initial preprocessing should return a Document"
        assert processed.content == document.content, "Initial preprocessing should preserve document content"
        assert processed.source == document.source, "Initial preprocessing should preserve document source"
        assert processed.metadata == document.metadata, "Initial preprocessing should preserve document metadata"
        try:
            Preprocessor(None)
            assert False, "Preprocessor should reject a missing Logger dependency"
        except ValueError:
            pass
        try:
            preprocessor.process(None)
            assert False, "Preprocessor should reject a non-Document input"
        except ValueError:
            pass
        print(green("Version 0.1.0 preprocessor foundation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.1.0 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.preprocessor import Preprocessor
        logger = Logger()
        preprocessor = Preprocessor(logger)
        document = Document(
            "   This   is    a test document.   ",
            "test.txt",
            {"category": "test"}
        )
        processed = preprocessor.process(document)
        assert processed is not document, "Preprocessing should return a new Document instance"
        assert processed.content == "This is a test document.", "Preprocessing should normalize repeated spaces and surrounding whitespace"
        assert processed.id == document.id, "Preprocessing should preserve the original document ID"
        assert processed.source == document.source, "Preprocessing should preserve the document source"
        assert processed.metadata == document.metadata, "Preprocessing should preserve document metadata"
        assert processed.metadata is not document.metadata, "Preprocessing should copy document metadata rather than share the original dictionary"
        print(green("Version 0.1.1 whitespace normalization is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.1.1 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.preprocessor import Preprocessor
        logger = Logger()
        preprocessor = Preprocessor(logger)
        document = Document(
            "  First paragraph.  \r\n\r\n\r\n  Second paragraph.  \r\n\r\n\r\n\r\n  Third paragraph.  ",
            "test.txt"
        )
        processed = preprocessor.process(document)
        assert processed.content == "First paragraph.\n\nSecond paragraph.\n\nThird paragraph.", "Preprocessing should normalize line endings and excessive blank lines while preserving paragraph boundaries"
        assert processed.id == document.id, "Line-break normalization should preserve the original document ID"
        assert processed.source == document.source, "Line-break normalization should preserve the document source"
        assert processed.metadata == document.metadata, "Line-break normalization should preserve document metadata"
        assert processed.metadata is not document.metadata, "Line-break normalization should keep metadata independent from the original document"
        single_line = Document("First line.\rSecond line.", "single.txt")
        single_processed = preprocessor.process(single_line)
        assert single_processed.content == "First line.\nSecond line.", "Preprocessing should normalize carriage returns into standard line feeds"
        print(green("Version 0.1.2 line-break normalization is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.1.2 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.preprocessor import Preprocessor
        logger = Logger()
        preprocessor = Preprocessor(logger)
        document = Document(
            "\ufeffThis\u00a0is a\u200b test document.",
            "artifacts.txt"
        )
        processed = preprocessor.process(document)
        assert processed.content == "This is a test document.", "Preprocessing should remove extraction artifacts and normalize the resulting whitespace"
        assert "\ufeff" not in processed.content, "Preprocessing should remove Unicode byte-order marks"
        assert "\u00a0" not in processed.content, "Preprocessing should remove non-breaking spaces"
        assert "\u200b" not in processed.content, "Preprocessing should remove zero-width spaces"
        assert processed.id == document.id, "Artifact cleanup should preserve the original document ID"
        assert processed.source == document.source, "Artifact cleanup should preserve the document source"
        print(green("Version 0.1.3 text artifact cleanup is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.1.3 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.preprocessor import Preprocessor
        logger = Logger()
        preprocessor = Preprocessor(logger)
        document = Document(
            "  A valid document with   inconsistent spacing.  ",
            "validation.txt",
            {"category": "test"}
        )
        processed = preprocessor.process(document)
        assert isinstance(processed, Document), "Preprocessing validation should return a valid Document"
        assert isinstance(processed.content, str), "Processed document content should remain a string"
        assert processed.content, "Preprocessing validation should reject empty processed content"
        assert processed.source == document.source, "Preprocessing validation should preserve the document source"
        assert processed.id == document.id, "Preprocessing validation should preserve the original document ID"
        assert isinstance(processed.metadata, dict), "Processed document metadata should remain a dictionary"
        assert processed.metadata == document.metadata, "Preprocessing validation should preserve document metadata"
        assert processed.metadata is not document.metadata, "Preprocessing validation should keep metadata independent from the original document"
        artifact_only = Document("\ufeff\u00a0\u200b", "artifact_only.txt")
        try:
            preprocessor.process(artifact_only)
            assert False, "Preprocessing should reject a document that becomes empty after artifact cleanup"
        except ValueError:
            pass
        try:
            preprocessor.process(None)
            assert False, "Preprocessing validation should reject a non-Document input"
        except ValueError:
            pass
        print(green("Version 0.1.4 preprocessing validation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.1.4 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.preprocessor import Preprocessor
        logger = Logger()
        preprocessor = Preprocessor(logger)
        document = Document(
            "\ufeff  First\u00a0paragraph.   \u200b\r\n\r\n\r\n  Second   paragraph.  \r\n\r\n\r\n\r\n  Third paragraph.  ",
            "complete.txt",
            {"category": "test", "source_type": "text"}
        )
        processed = preprocessor.process(document)
        assert isinstance(processed, Document), "Complete preprocessing should return a Document"
        assert processed.content == "First paragraph.\n\nSecond paragraph.\n\nThird paragraph.", "Complete preprocessing should apply all text normalization stages in the correct order"
        assert "\ufeff" not in processed.content, "Complete preprocessing should remove Unicode byte-order marks"
        assert "\u00a0" not in processed.content, "Complete preprocessing should remove non-breaking spaces"
        assert "\u200b" not in processed.content, "Complete preprocessing should remove zero-width spaces"
        assert "\r" not in processed.content, "Complete preprocessing should remove carriage returns"
        assert processed.id == document.id, "Complete preprocessing should preserve the original document ID"
        assert processed.source == document.source, "Complete preprocessing should preserve the original document source"
        assert processed.metadata == document.metadata, "Complete preprocessing should preserve document metadata"
        assert processed.metadata is not document.metadata, "Complete preprocessing should keep metadata independent from the original document"
        assert processed is not document, "Complete preprocessing should return a new Document instance"
        try:
            artifact_only = Document("\ufeff\u00a0\u200b", "empty_after_cleanup.txt")
            preprocessor.process(artifact_only)
            assert False, "Complete preprocessing should reject content that becomes empty after cleanup"
        except ValueError:
            pass
        try:
            preprocessor.process(None)
            assert False, "Complete preprocessing should reject a non-Document input"
        except ValueError:
            pass
        print(green("Version 0.1.5 complete preprocessing pipeline is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.1.5 failed"))

    try:
        tests += 1
        from classes.chunker import Chunker
        from classes.document import Document
        from classes.logger import Logger
        logger = Logger()
        chunker = Chunker(logger, chunk_size=10)
        document = Document(
            "01234567890123456789",
            "chunk_test.txt",
            {"category": "test"}
        )
        chunks = chunker.chunk(document)
        assert isinstance(chunks, list), "Chunking should return chunks as a list"
        assert len(chunks) == 2, "Chunking should divide a twenty-character document into two ten-character chunks"
        assert all(isinstance(chunk, Document) for chunk in chunks), "Every generated chunk should be represented as a Document"
        assert chunks[0].content == "0123456789", "First chunk should contain the first chunk_size characters"
        assert chunks[1].content == "0123456789", "Second chunk should contain the remaining characters"
        assert chunks[0].source == document.source, "Chunks should preserve the original document source"
        assert chunks[1].source == document.source, "Every chunk should preserve the original document source"
        assert chunks[0].metadata["document_id"] == document.id, "Chunks should retain the identity of their source document"
        assert chunks[1].metadata["document_id"] == document.id, "Every chunk should retain the identity of its source document"
        assert chunks[0].metadata["chunk_index"] == 0, "The first chunk should have chunk index zero"
        assert chunks[1].metadata["chunk_index"] == 1, "The second chunk should have chunk index one"
        assert chunks[0].metadata["chunk_start"] == 0, "The first chunk should record its starting character position"
        assert chunks[0].metadata["chunk_end"] == 10, "The first chunk should record its ending character position"
        assert chunks[1].metadata["chunk_start"] == 10, "The second chunk should record its starting character position"
        assert chunks[1].metadata["chunk_end"] == 20, "The second chunk should record its ending character position"
        assert chunks[0].metadata["category"] == "test", "Chunks should preserve the original document metadata"
        assert chunks[0].id != chunks[1].id, "Each generated chunk should have a unique document ID"
        assert chunks[0].metadata is not document.metadata, "Chunk metadata should be independent from the original document metadata"
        try:
            Chunker(None)
            assert False, "Chunker should reject a missing Logger dependency"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=0)
            assert False, "Chunker should reject a zero chunk size"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=-1)
            assert False, "Chunker should reject a negative chunk size"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size="10")
            assert False, "Chunker should reject a non-integer chunk size"
        except ValueError:
            pass
        try:
            chunker.chunk(None)
            assert False, "Chunker should reject a non-Document input"
        except ValueError:
            pass
        print(green("Version 0.2.0 chunking foundation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.2.0 failed"))

    try:
        tests += 1
        from classes.chunker import Chunker
        from classes.document import Document
        from classes.logger import Logger
        logger = Logger()
        chunker = Chunker(logger, chunk_size=10)
        document = Document(
            "01234567890123456789",
            "identity_test.txt",
            {"category": "test", "author": "Noah"}
        )
        chunks = chunker.chunk(document)
        assert len(chunks) == 2, "Chunking should produce the expected number of chunks"
        assert chunks[0].metadata["document_id"] == document.id, "Every chunk should identify its source document"
        assert chunks[1].metadata["document_id"] == document.id, "Every chunk should identify the same source document"
        assert chunks[0].metadata["chunk_index"] == 0, "The first chunk should have a zero-based index"
        assert chunks[1].metadata["chunk_index"] == 1, "The second chunk should have the next sequential index"
        assert chunks[0].metadata["chunk_start"] == 0, "The first chunk should begin at character position zero"
        assert chunks[0].metadata["chunk_end"] == 10, "The first chunk should end at its configured chunk size"
        assert chunks[1].metadata["chunk_start"] == 10, "The second chunk should begin where the first chunk ends"
        assert chunks[1].metadata["chunk_end"] == 20, "The final chunk should record the actual end of the document"
        assert chunks[0].metadata["category"] == "test", "Chunk metadata should preserve inherited document metadata"
        assert chunks[0].metadata["author"] == "Noah", "Chunk metadata should preserve all inherited document metadata"
        assert chunks[0].metadata is not document.metadata, "Chunk metadata should not share the source document metadata dictionary"
        assert chunks[1].metadata is not chunks[0].metadata, "Each chunk should have its own metadata dictionary"
        assert chunks[0].id != document.id, "Each chunk should have its own unique identity separate from the source document"
        assert chunks[1].id != document.id, "Every chunk should have its own unique identity separate from the source document"
        assert chunks[0].id != chunks[1].id, "Different chunks should never share the same chunk identity"
        assert chunks[0].source == document.source, "Chunk identity should retain the original document source"
        assert chunks[1].source == document.source, "Every chunk should retain the original document source"
        print(green("Version 0.2.1 chunk identity and metadata refinement is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.2.1 failed"))

    try:
        tests += 1
        from classes.chunker import Chunker
        from classes.document import Document
        from classes.logger import Logger
        logger = Logger()
        chunker = Chunker(logger, chunk_size=20)
        document = Document(
            "The first sentence contains useful information. The second sentence contains more information.",
            "boundary_test.txt",
            {"category": "test"}
        )
        chunks = chunker.chunk(document)
        assert isinstance(chunks, list), "Boundary-aware chunking should return chunks as a list"
        assert len(chunks) >= 2, "Boundary-aware chunking should divide content that exceeds the configured chunk size"
        assert all(isinstance(chunk, Document) for chunk in chunks), "Every boundary-aware chunk should be represented as a Document"
        assert all(len(chunk.content) <= 20 for chunk in chunks), "Boundary-aware chunks should not exceed the configured chunk size"
        assert all(not chunk.content.startswith(" ") for chunk in chunks), "Boundary-aware chunks should not begin with whitespace"
        assert all(not chunk.content.endswith(" ") for chunk in chunks), "Boundary-aware chunks should not end with whitespace"
        assert chunks[0].content == "The first sentence", "Chunking should prefer a natural whitespace boundary near the configured limit"
        assert chunks[0].metadata["chunk_index"] == 0, "The first boundary-aware chunk should have a zero-based index"
        assert chunks[1].metadata["chunk_index"] == 1, "Boundary-aware chunk indexes should remain sequential"
        assert chunks[0].metadata["document_id"] == document.id, "Boundary-aware chunks should retain their source document identity"
        assert chunks[1].metadata["document_id"] == document.id, "Every boundary-aware chunk should retain the source document identity"
        reconstructed = " ".join(chunk.content for chunk in chunks)
        assert reconstructed == document.content, "Boundary-aware chunking should preserve all document content without loss or duplication"
        short_document = Document("Short document.", "short.txt")
        short_chunks = chunker.chunk(short_document)
        assert len(short_chunks) == 1, "Documents shorter than the chunk size should remain a single chunk"
        assert short_chunks[0].content == "Short document.", "A short document should retain its complete content"
        exact_document = Document("12345678901234567890", "exact.txt")
        exact_chunks = chunker.chunk(exact_document)
        assert len(exact_chunks) == 1, "A document exactly matching the chunk size should remain a single chunk"
        assert exact_chunks[0].content == exact_document.content, "A document exactly matching the chunk size should retain its complete content"
        print(green("Version 0.2.2 boundary-aware chunking is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.2.2 failed"))

    try:
        tests += 1
        from classes.chunker import Chunker
        from classes.document import Document
        from classes.logger import Logger
        logger = Logger()
        chunker = Chunker(logger, chunk_size=20, chunk_overlap=5)
        document = Document(
            "The first sentence contains useful information. The second sentence contains more information.",
            "overlap_test.txt",
            {"category": "test"}
        )
        chunks = chunker.chunk(document)
        assert isinstance(chunks, list), "Chunk overlap processing should return chunks as a list"
        assert len(chunks) >= 2, "Chunk overlap processing should produce multiple chunks for content exceeding the chunk size"
        assert all(isinstance(chunk, Document) for chunk in chunks), "Every overlapping chunk should be represented as a Document"
        assert all(len(chunk.content) <= 20 for chunk in chunks), "Overlapping chunks should not exceed the configured chunk size"
        assert chunks[0].metadata["chunk_index"] == 0, "The first overlapping chunk should have a zero-based index"
        assert chunks[1].metadata["chunk_index"] == 1, "Overlapping chunk indexes should remain sequential"
        assert chunks[0].metadata["document_id"] == document.id, "Overlapping chunks should retain their source document identity"
        assert chunks[1].metadata["document_id"] == document.id, "Every overlapping chunk should retain the source document identity"
        assert chunks[1].metadata["chunk_start"] < chunks[0].metadata["chunk_end"], "The second chunk should begin before the first chunk ends when overlap is configured"
        assert chunks[1].metadata["chunk_start"] == chunks[0].metadata["chunk_end"] - 5, "Chunk overlap should shift the next chunk backward by the configured overlap amount"
        assert chunks[0].content[-5:] == chunks[1].content[:5], "Adjacent chunks should share the configured overlapping content"
        assert chunks[0].source == document.source, "Overlapping chunks should preserve the original document source"
        assert chunks[1].source == document.source, "Every overlapping chunk should preserve the original document source"
        no_overlap_chunker = Chunker(logger, chunk_size=20)
        no_overlap_chunks = no_overlap_chunker.chunk(document)
        assert no_overlap_chunks[1].metadata["chunk_start"] >= no_overlap_chunks[0].metadata["chunk_end"], "A zero overlap configuration should not create overlapping chunk positions"
        assert no_overlap_chunks[0].content[-1] not in no_overlap_chunks[1].content[:1], "A zero overlap configuration should not duplicate the boundary character between adjacent chunks"
        try:
            Chunker(logger, chunk_size=10, chunk_overlap=10)
            assert False, "Chunk overlap should be smaller than the configured chunk size"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=10, chunk_overlap=11)
            assert False, "Chunker should reject overlap values larger than the chunk size"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=10, chunk_overlap=-1)
            assert False, "Chunker should reject negative overlap values"
        except ValueError:
            pass
        print(green("Version 0.2.3 chunk overlap is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.2.3 failed"))

    try:
        tests += 1
        from classes.chunker import Chunker
        from classes.document import Document
        from classes.logger import Logger
        logger = Logger()
        chunker = Chunker(logger, chunk_size=20, chunk_overlap=5)
        document = Document(
            "The first sentence contains useful information. The second sentence contains more information.",
            "validation_test.txt",
            {"category": "test"}
        )
        original_content = document.content
        original_metadata = document.metadata.copy()
        chunks = chunker.chunk(document)
        assert isinstance(chunks, list), "Chunk validation should return chunks as a list"
        assert chunks, "Chunk validation should produce at least one chunk for non-empty content"
        assert all(isinstance(chunk, Document) for chunk in chunks), "Every validated chunk should be a Document"
        assert all(chunk.content for chunk in chunks), "Every validated chunk should contain non-empty content"
        assert all(chunk.source == document.source for chunk in chunks), "Every validated chunk should preserve the source document source"
        assert all(chunk.metadata["document_id"] == document.id for chunk in chunks), "Every validated chunk should reference the source document ID"
        assert [chunk.metadata["chunk_index"] for chunk in chunks] == list(range(len(chunks))), "Validated chunk indexes should be sequential and zero-based"
        assert all(chunk.metadata["chunk_start"] >= 0 for chunk in chunks), "Validated chunk start positions should never be negative"
        assert all(chunk.metadata["chunk_end"] >= chunk.metadata["chunk_start"] for chunk in chunks), "Validated chunk positions should define valid ranges"
        assert all(chunk.metadata["chunk_end"] <= len(document.content) for chunk in chunks), "Validated chunk positions should remain within the source document"
        assert all(len(chunk.content) <= chunker.chunk_size for chunk in chunks), "Validated chunks should respect the configured chunk size"
        assert all(chunk.metadata["chunk_start"] < chunk.metadata["chunk_end"] for chunk in chunks), "Validated chunks should represent a non-empty source range"
        assert all(chunk.metadata is not document.metadata for chunk in chunks), "Validated chunks should use independent metadata dictionaries"
        assert document.content == original_content, "Chunking validation should not modify the original document content"
        assert document.metadata == original_metadata, "Chunking validation should not modify the original document metadata"
        short_document = Document("Short document.", "short.txt")
        short_chunks = chunker.chunk(short_document)
        assert len(short_chunks) == 1, "Chunk validation should keep content shorter than the chunk size as one chunk"
        assert short_chunks[0].metadata["chunk_start"] == 0, "A single validated chunk should begin at the start of the document"
        assert short_chunks[0].metadata["chunk_end"] == len(short_document.content), "A single validated chunk should end at the document boundary"
        try:
            Chunker(logger, chunk_size=0)
            assert False, "Chunk validation should reject a zero chunk size"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=-5)
            assert False, "Chunk validation should reject a negative chunk size"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=10, chunk_overlap=10)
            assert False, "Chunk validation should reject overlap equal to the chunk size"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=10, chunk_overlap=11)
            assert False, "Chunk validation should reject overlap greater than the chunk size"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=10, chunk_overlap=-1)
            assert False, "Chunk validation should reject negative overlap"
        except ValueError:
            pass
        try:
            chunker.chunk(None)
            assert False, "Chunk validation should reject a non-Document input"
        except ValueError:
            pass
        print(green("Version 0.2.4 chunk validation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.2.4 failed"))

    try:
        tests += 1
        from classes.chunker import Chunker
        from classes.document import Document
        from classes.logger import Logger
        logger = Logger()
        chunker = Chunker(logger, chunk_size=30, chunk_overlap=5)
        document = Document(
            "The first section contains useful information about authentication. The second section contains information about authorization. The final section contains information about security.",
            "complete_chunking_test.txt",
            {"category": "security", "source_type": "text"}
        )
        original_content = document.content
        original_metadata = document.metadata.copy()
        chunks = chunker.chunk(document)
        assert isinstance(chunks, list), "Complete chunking should return a list of chunks"
        assert len(chunks) >= 2, "Complete chunking should divide content that exceeds the configured chunk size"
        assert all(isinstance(chunk, Document) for chunk in chunks), "Complete chunking should return only Document objects"
        assert all(chunk.content for chunk in chunks), "Complete chunking should never produce empty chunks"
        assert all(len(chunk.content) <= 30 for chunk in chunks), "Complete chunking should enforce the configured chunk size"
        assert all(chunk.source == document.source for chunk in chunks), "Complete chunking should preserve the original document source"
        assert all(chunk.metadata["document_id"] == document.id for chunk in chunks), "Complete chunking should preserve source document lineage"
        assert [chunk.metadata["chunk_index"] for chunk in chunks] == list(range(len(chunks))), "Complete chunking should assign sequential zero-based chunk indexes"
        assert all(chunk.metadata["chunk_start"] >= 0 for chunk in chunks), "Complete chunking should never produce negative chunk start positions"
        assert all(chunk.metadata["chunk_end"] >= chunk.metadata["chunk_start"] for chunk in chunks), "Complete chunking should produce valid chunk position ranges"
        assert all(chunk.metadata["chunk_end"] <= len(document.content) for chunk in chunks), "Complete chunking should keep chunk positions within the source document"
        assert all(chunk.metadata["chunk_start"] < chunk.metadata["chunk_end"] for chunk in chunks), "Complete chunking should assign a non-empty source range to every chunk"
        assert all(chunk.metadata["category"] == "security" for chunk in chunks), "Complete chunking should preserve inherited document metadata"
        assert all(chunk.metadata["source_type"] == "text" for chunk in chunks), "Complete chunking should preserve all inherited document metadata"
        assert all(chunk.metadata is not document.metadata for chunk in chunks), "Complete chunking should keep chunk metadata independent from the source document"
        assert all(chunks[index].metadata is not chunks[index + 1].metadata for index in range(len(chunks) - 1)), "Complete chunking should give every chunk its own metadata dictionary"
        assert all(chunk.id != document.id for chunk in chunks), "Complete chunking should give chunks identities distinct from the source document"
        assert len({chunk.id for chunk in chunks}) == len(chunks), "Complete chunking should give every chunk a unique identity"
        assert any(chunks[index].metadata["chunk_start"] < chunks[index - 1].metadata["chunk_end"] for index in range(1, len(chunks))), "Complete chunking should create overlapping source ranges when overlap is configured"
        assert document.content == original_content, "Complete chunking should not modify the source document content"
        assert document.metadata == original_metadata, "Complete chunking should not modify the source document metadata"
        short_document = Document("Short document.", "short.txt")
        short_chunks = chunker.chunk(short_document)
        assert len(short_chunks) == 1, "Complete chunking should keep documents shorter than the chunk size as one chunk"
        assert short_chunks[0].content == short_document.content, "Complete chunking should preserve all content in a short document"
        exact_content = "123456789012345678901234567890"
        exact_document = Document(exact_content, "exact.txt")
        exact_chunks = chunker.chunk(exact_document)
        assert len(exact_chunks) == 1, "Complete chunking should keep documents exactly matching the chunk size as one chunk"
        assert exact_chunks[0].content == exact_content, "Complete chunking should preserve content that exactly matches the chunk size"
        no_overlap_chunker = Chunker(logger, chunk_size=30)
        no_overlap_chunks = no_overlap_chunker.chunk(document)
        assert all(no_overlap_chunks[index].metadata["chunk_start"] >= no_overlap_chunks[index - 1].metadata["chunk_end"] for index in range(1, len(no_overlap_chunks))), "Complete chunking should prevent overlapping ranges when overlap is disabled"
        try:
            Chunker(None)
            assert False, "Complete chunking should reject a missing Logger dependency"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=0)
            assert False, "Complete chunking should reject a zero chunk size"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=-1)
            assert False, "Complete chunking should reject a negative chunk size"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=10, chunk_overlap=10)
            assert False, "Complete chunking should reject overlap equal to the chunk size"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=10, chunk_overlap=11)
            assert False, "Complete chunking should reject overlap greater than the chunk size"
        except ValueError:
            pass
        try:
            Chunker(logger, chunk_size=10, chunk_overlap=-1)
            assert False, "Complete chunking should reject negative overlap"
        except ValueError:
            pass
        try:
            chunker.chunk(None)
            assert False, "Complete chunking should reject a non-Document input"
        except ValueError:
            pass
        print(green("Version 0.2.5 complete chunking pipeline is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.2.5 failed"))

    try:
        tests += 1
        from classes.chunker import Chunker
        from classes.document import Document
        from classes.embedding_provider import EmbeddingProvider
        from classes.embedder import Embedder
        from classes.logger import Logger
        class TestEmbeddingProvider(EmbeddingProvider):
            def embed(self, text):
                return [float(len(text)), 1.0, 2.0]
        logger = Logger()
        provider = TestEmbeddingProvider()
        embedder = Embedder(provider, logger)
        chunker = Chunker(logger, chunk_size=20)
        document = Document(
            "This document contains enough text to produce multiple chunks.",
            "embedding_test.txt",
            {"category": "test"}
        )
        chunks = chunker.chunk(document)
        embedded = embedder.embed(chunks)
        assert isinstance(embedded, list), "Embedding should return results as a list"
        assert len(embedded) == len(chunks), "Embedding should produce one result for every chunk"
        assert all(isinstance(item, dict) for item in embedded), "Every embedding result should be represented as a dictionary"
        assert all("chunk" in item for item in embedded), "Every embedding result should retain its source chunk"
        assert all("embedding" in item for item in embedded), "Every embedding result should contain an embedding vector"
        assert all(isinstance(item["chunk"], Document) for item in embedded), "Every embedding result should retain a Document chunk"
        assert all(isinstance(item["embedding"], list) for item in embedded), "Every embedding vector should be represented as a list"
        assert all(item["embedding"] for item in embedded), "Every embedding vector should contain values"
        assert embedded[0]["chunk"] is chunks[0], "Embedding results should retain the exact chunk object provided to the embedder"
        assert embedded[0]["embedding"] == [float(len(chunks[0].content)), 1.0, 2.0], "Embedding should pass chunk content to the provider and retain the returned vector"
        assert embedded[0]["chunk"].metadata["document_id"] == document.id, "Embedded chunks should retain their source document identity"
        assert embedded[0]["chunk"].metadata["chunk_index"] == 0, "Embedded chunks should retain their original chunk index"
        assert embedded[0]["chunk"].source == document.source, "Embedded chunks should retain their original document source"
        try:
            Embedder(None, logger)
            assert False, "Embedder should reject a missing embedding provider"
        except ValueError:
            pass
        try:
            Embedder(provider, None)
            assert False, "Embedder should reject a missing Logger dependency"
        except ValueError:
            pass
        try:
            embedder.embed(None)
            assert False, "Embedder should reject a missing chunk collection"
        except ValueError:
            pass
        try:
            embedder.embed("invalid")
            assert False, "Embedder should reject a non-list chunk collection"
        except ValueError:
            pass
        try:
            embedder.embed([None])
            assert False, "Embedder should reject collections containing non-Document values"
        except ValueError:
            pass
        class EmptyEmbeddingProvider(EmbeddingProvider):
            def embed(self, text):
                return []
        empty_embedder = Embedder(EmptyEmbeddingProvider(), logger)
        try:
            empty_embedder.embed([chunks[0]])
            assert False, "Embedder should reject empty embedding vectors"
        except ValueError:
            pass
        class InvalidEmbeddingProvider(EmbeddingProvider):
            def embed(self, text):
                return "invalid"
        invalid_embedder = Embedder(InvalidEmbeddingProvider(), logger)
        try:
            invalid_embedder.embed([chunks[0]])
            assert False, "Embedder should reject embedding providers that return non-vector values"
        except ValueError:
            pass
        print(green("Version 0.3.0 embedding foundation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.3.0 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.embedding_provider import EmbeddingProvider
        from classes.embedder import Embedder
        from classes.logger import Logger
        class ValidEmbeddingProvider(EmbeddingProvider):
            def embed(self, text):
                return [float(len(text)), 1.0, 2.0]
        class StringEmbeddingProvider(EmbeddingProvider):
            def embed(self, text):
                return [float(len(text)), "invalid", 2.0]
        class MismatchedEmbeddingProvider(EmbeddingProvider):
            def __init__(self):
                self.calls = 0
            def embed(self, text):
                self.calls += 1
                if self.calls == 1:
                    return [1.0, 2.0, 3.0]
                return [1.0, 2.0]
        logger = Logger()
        document_one = Document("First chunk.", "validation_one.txt")
        document_two = Document("Second chunk.", "validation_two.txt")
        valid_embedder = Embedder(ValidEmbeddingProvider(), logger)
        valid_results = valid_embedder.embed([document_one, document_two])
        assert len(valid_results) == 2, "Embedding validation should produce one result for every valid chunk"
        assert all(isinstance(value, (int, float)) for value in valid_results[0]["embedding"]), "Embedding vectors should contain only numeric values"
        assert all(isinstance(value, (int, float)) for value in valid_results[1]["embedding"]), "Every embedding vector should contain only numeric values"
        assert len(valid_results[0]["embedding"]) == 3, "Embedding validation should preserve the provider vector dimension"
        assert len(valid_results[1]["embedding"]) == 3, "Every embedding should use the expected vector dimension"
        string_embedder = Embedder(StringEmbeddingProvider(), logger)
        try:
            string_embedder.embed([document_one])
            assert False, "Embedder should reject vectors containing non-numeric values"
        except ValueError:
            pass
        mismatched_embedder = Embedder(MismatchedEmbeddingProvider(), logger)
        try:
            mismatched_embedder.embed([document_one, document_two])
            assert False, "Embedder should reject batches containing vectors with different dimensions"
        except ValueError:
            pass
        empty_embedder = Embedder(ValidEmbeddingProvider(), logger)
        empty_results = empty_embedder.embed([])
        assert empty_results == [], "Embedding an empty chunk collection should return an empty result list"
        print(green("Version 0.3.1 embedding validation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.3.1 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.embedding_provider import EmbeddingProvider
        from classes.embedder import Embedder
        from classes.logger import Logger
        class BatchEmbeddingProvider(EmbeddingProvider):
            def __init__(self):
                self.embed_many_calls = 0
                self.embed_calls = 0
            def embed(self, text):
                self.embed_calls += 1
                return [float(len(text)), 1.0, 2.0]
            def embed_many(self, texts):
                self.embed_many_calls += 1
                return [[float(len(text)), 1.0, 2.0] for text in texts]
        class IncorrectBatchProvider(EmbeddingProvider):
            def embed(self, text):
                return [1.0, 2.0, 3.0]
            def embed_many(self, texts):
                return [[1.0, 2.0, 3.0]]
        logger = Logger()
        provider = BatchEmbeddingProvider()
        embedder = Embedder(provider, logger)
        first_chunk = Document("First chunk.", "first.txt", {"index": 0})
        second_chunk = Document("Second chunk.", "second.txt", {"index": 1})
        third_chunk = Document("Third chunk.", "third.txt", {"index": 2})
        chunks = [first_chunk, second_chunk, third_chunk]
        embedded = embedder.embed(chunks)
        assert isinstance(embedded, list), "Batch embedding should return results as a list"
        assert len(embedded) == len(chunks), "Batch embedding should produce one result for every input chunk"
        assert provider.embed_many_calls == 1, "Batch embedding should call the provider batch method once"
        assert provider.embed_calls == 0, "Batch embedding should not fall back to individual provider calls when batch embedding is available"
        assert embedded[0]["chunk"] is first_chunk, "Batch embedding should preserve the first chunk object"
        assert embedded[1]["chunk"] is second_chunk, "Batch embedding should preserve the second chunk object"
        assert embedded[2]["chunk"] is third_chunk, "Batch embedding should preserve the third chunk object"
        assert embedded[0]["embedding"] == [float(len(first_chunk.content)), 1.0, 2.0], "The first batch vector should correspond to the first chunk"
        assert embedded[1]["embedding"] == [float(len(second_chunk.content)), 1.0, 2.0], "The second batch vector should correspond to the second chunk"
        assert embedded[2]["embedding"] == [float(len(third_chunk.content)), 1.0, 2.0], "The third batch vector should correspond to the third chunk"
        assert embedded[0]["chunk"].metadata["index"] == 0, "Batch embedding should preserve first chunk metadata"
        assert embedded[1]["chunk"].metadata["index"] == 1, "Batch embedding should preserve second chunk metadata"
        assert embedded[2]["chunk"].metadata["index"] == 2, "Batch embedding should preserve third chunk metadata"
        empty_result = embedder.embed([])
        assert empty_result == [], "Batch embedding should return an empty list for an empty batch"
        incorrect_embedder = Embedder(IncorrectBatchProvider(), logger)
        try:
            incorrect_embedder.embed(chunks)
            assert False, "Batch embedding should reject a provider returning the wrong number of vectors"
        except ValueError:
            pass
        print(green("Version 0.3.2 batch embedding is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.3.2 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.embedding_provider import EmbeddingProvider
        from classes.embedder import Embedder
        from classes.logger import Logger
        class IdentityEmbeddingProvider(EmbeddingProvider):
            def embed(self, text):
                return [float(len(text)), 1.0, 2.0]
        logger = Logger()
        provider = IdentityEmbeddingProvider()
        embedder = Embedder(provider, logger)
        document = Document(
            "Original document content.",
            "identity_embedding.txt",
            {"category": "test", "source_type": "text"}
        )
        document_id = document.id
        chunk = Document(
            "Chunk content.",
            document.source,
            {
                "document_id": document_id,
                "chunk_index": 0,
                "chunk_start": 0,
                "chunk_end": 14,
                "category": "test",
                "source_type": "text"
            }
        )
        chunk_id = chunk.id
        embedded = embedder.embed([chunk])
        assert len(embedded) == 1, "Embedding identity should produce one result for the input chunk"
        result = embedded[0]
        assert result["chunk"] is chunk, "Embedding identity should retain the exact source chunk"
        assert result["embedding"] == [float(len(chunk.content)), 1.0, 2.0], "Embedding identity should retain the generated vector"
        assert isinstance(result["metadata"], dict), "Embedding identity metadata should be represented as a dictionary"
        assert result["metadata"]["chunk_id"] == chunk_id, "Embedding metadata should identify the source chunk"
        assert result["metadata"]["document_id"] == document_id, "Embedding metadata should identify the source document"
        assert result["metadata"]["source"] == chunk.source, "Embedding metadata should preserve the chunk source"
        assert result["metadata"]["chunk_index"] == 0, "Embedding metadata should preserve the chunk index"
        assert result["metadata"]["chunk_start"] == 0, "Embedding metadata should preserve the chunk start position"
        assert result["metadata"]["chunk_end"] == 14, "Embedding metadata should preserve the chunk end position"
        assert result["metadata"]["category"] == "test", "Embedding metadata should preserve inherited document metadata"
        assert result["metadata"]["source_type"] == "text", "Embedding metadata should preserve all inherited metadata"
        assert result["metadata"] is not chunk.metadata, "Embedding metadata should be independent from chunk metadata"
        result["metadata"]["category"] = "modified"
        assert chunk.metadata["category"] == "test", "Modifying embedding metadata should not modify the source chunk metadata"
        assert chunk.id == chunk_id, "Embedding should not modify the source chunk identity"
        assert chunk.metadata["document_id"] == document_id, "Embedding should not modify source document lineage"
        assert chunk.source == document.source, "Embedding should not modify the source chunk"
        print(green("Version 0.3.3 embedding identity and metadata is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.3.3 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.embedding_provider import EmbeddingProvider
        from classes.embedder import Embedder
        from classes.logger import Logger
        class FailureEmbeddingProvider(EmbeddingProvider):
            def embed(self, text):
                if text == "This chunk should fail.":
                    raise RuntimeError("Simulated embedding failure")
                return [float(len(text)), 1.0, 2.0]
        logger = Logger()
        provider = FailureEmbeddingProvider()
        embedder = Embedder(provider, logger)
        first_chunk = Document("This chunk should succeed.", "first.txt")
        failed_chunk = Document("This chunk should fail.", "failed.txt")
        third_chunk = Document("This chunk should also succeed.", "third.txt")
        chunks = [first_chunk, failed_chunk, third_chunk]
        embedded = embedder.embed(chunks)
        stats = embedder.get_embedding_stats()
        failures = embedder.get_embedding_failures()
        assert isinstance(embedded, list), "Embedding failure handling should return successful embeddings as a list"
        assert len(embedded) == 2, "Embedding failure handling should retain successful chunks when another chunk fails"
        assert embedded[0]["chunk"] is first_chunk, "The first successful chunk should remain in the embedding results"
        assert embedded[1]["chunk"] is third_chunk, "Chunks after a failure should still be embedded"
        assert stats == {
            "attempted": 3,
            "successful": 2,
            "failed": 1
        }, "Embedding statistics should accurately record successful and failed chunks"
        assert isinstance(failures, list), "Embedding failures should be returned as a list"
        assert len(failures) == 1, "Embedding failure handling should record exactly one failed chunk"
        assert failures[0]["chunk_id"] == failed_chunk.id, "Embedding failure records should identify the failed chunk"
        assert failures[0]["source"] == failed_chunk.source, "Embedding failure records should identify the failed chunk source"
        assert failures[0]["error"] == "Simulated embedding failure", "Embedding failure records should preserve the provider error message"
        assert all("embedding" in result for result in embedded), "Successful embedding results should still contain vectors"
        with_failure_embedder = Embedder(provider, logger)
        with_failure_embedder.embed([failed_chunk])
        failure_stats = with_failure_embedder.get_embedding_stats()
        failure_records = with_failure_embedder.get_embedding_failures()
        assert failure_stats == {
            "attempted": 1,
            "successful": 0,
            "failed": 1
        }, "A completely failed embedding batch should report one attempted and failed chunk"
        assert len(failure_records) == 1, "A completely failed embedding batch should retain its failure record"
        successful_embedder = Embedder(provider, logger)
        successful_embedder.embed([first_chunk])
        successful_stats = successful_embedder.get_embedding_stats()
        successful_failures = successful_embedder.get_embedding_failures()
        assert successful_stats == {
            "attempted": 1,
            "successful": 1,
            "failed": 0
        }, "A new successful embedding run should replace previous embedding statistics"
        assert successful_failures == [], "A new successful embedding run should clear previous embedding failures"
        print(green("Version 0.3.4 embedding failure handling is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.3.4 failed"))

    try:
        tests += 1
        from classes.chunker import Chunker
        from classes.document import Document
        from classes.embedding_provider import EmbeddingProvider
        from classes.embedder import Embedder
        from classes.logger import Logger
        class CompleteEmbeddingProvider(EmbeddingProvider):
            def embed(self, text):
                if text == "This chunk will fail.":
                    raise RuntimeError("Simulated embedding failure")
                return [float(len(text)), 1.0, 2.0]
        logger = Logger()
        provider = CompleteEmbeddingProvider()
        embedder = Embedder(provider, logger)
        chunker = Chunker(logger, chunk_size=30, chunk_overlap=5)
        document = Document(
            "The first chunk contains useful information. The second chunk contains additional information. The final chunk contains security information.",
            "complete_embedding_test.txt",
            {"category": "security", "source_type": "text"}
        )
        original_content = document.content
        original_metadata = document.metadata.copy()
        chunks = chunker.chunk(document)
        embedded = embedder.embed(chunks)
        stats = embedder.get_embedding_stats()
        failures = embedder.get_embedding_failures()
        assert isinstance(chunks, list), "Complete embedding should receive chunks as a list"
        assert chunks, "Complete embedding should have at least one chunk to process"
        assert isinstance(embedded, list), "Complete embedding should return embedding results as a list"
        assert len(embedded) == len(chunks), "Complete embedding should produce one embedding result for every successful chunk"
        assert all(isinstance(result, dict) for result in embedded), "Complete embedding should return dictionary-based embedding results"
        assert all(isinstance(result["chunk"], Document) for result in embedded), "Complete embedding should retain each source chunk"
        assert all(isinstance(result["embedding"], list) for result in embedded), "Complete embedding should return vectors as lists"
        assert all(result["embedding"] for result in embedded), "Complete embedding should never return empty vectors"
        assert all(all(isinstance(value, (int, float)) for value in result["embedding"]) for result in embedded), "Complete embedding should return only numeric vector values"
        assert all(len(result["embedding"]) == 3 for result in embedded), "Complete embedding should preserve a consistent vector dimension"
        assert all("metadata" in result for result in embedded), "Complete embedding should attach metadata to every embedding result"
        assert all("chunk_id" in result["metadata"] for result in embedded), "Complete embedding metadata should identify every source chunk"
        assert all("document_id" in result["metadata"] for result in embedded), "Complete embedding metadata should identify every source document"
        assert all(result["metadata"]["source"] == document.source for result in embedded), "Complete embedding metadata should preserve the original document source"
        assert all(result["metadata"]["category"] == "security" for result in embedded), "Complete embedding should preserve inherited document metadata"
        assert stats == {
            "attempted": len(chunks),
            "successful": len(chunks),
            "failed": 0
        }, "Complete embedding statistics should accurately describe a fully successful embedding run"
        assert failures == [], "Complete embedding should have no failures when every chunk embeds successfully"
        assert document.content == original_content, "Complete embedding should not modify the source document content"
        assert document.metadata == original_metadata, "Complete embedding should not modify the source document metadata"
        failed_chunk = Document(
            "This chunk will fail.",
            "failed_embedding.txt",
            {"category": "security"}
        )
        successful_chunk = Document(
            "This chunk will succeed.",
            "successful_embedding.txt",
            {"category": "security"}
        )
        mixed_results = embedder.embed([failed_chunk, successful_chunk])
        mixed_stats = embedder.get_embedding_stats()
        mixed_failures = embedder.get_embedding_failures()
        assert len(mixed_results) == 1, "Complete embedding should retain successful chunks when another chunk fails"
        assert mixed_results[0]["chunk"] is successful_chunk, "Complete embedding should preserve successful chunks after a failure"
        assert mixed_stats == {
            "attempted": 2,
            "successful": 1,
            "failed": 1
        }, "Complete embedding should accurately track mixed embedding success and failure"
        assert len(mixed_failures) == 1, "Complete embedding should record exactly one failed chunk"
        assert mixed_failures[0]["chunk_id"] == failed_chunk.id, "Complete embedding failure records should identify the failed chunk"
        assert mixed_failures[0]["source"] == failed_chunk.source, "Complete embedding failure records should identify the failed chunk source"
        assert mixed_failures[0]["error"] == "Simulated embedding failure", "Complete embedding failure records should preserve the embedding error"
        embedder.embed([successful_chunk])
        reset_stats = embedder.get_embedding_stats()
        reset_failures = embedder.get_embedding_failures()
        assert reset_stats == {
            "attempted": 1,
            "successful": 1,
            "failed": 0
        }, "A new embedding run should completely replace previous embedding statistics"
        assert reset_failures == [], "A new successful embedding run should completely clear previous embedding failures"
        empty_results = embedder.embed([])
        empty_stats = embedder.get_embedding_stats()
        empty_failures = embedder.get_embedding_failures()
        assert empty_results == [], "Complete embedding should return an empty list for an empty input"
        assert empty_stats == {
            "attempted": 0,
            "successful": 0,
            "failed": 0
        }, "An empty embedding run should reset statistics to zero"
        assert empty_failures == [], "An empty embedding run should contain no failure records"
        try:
            embedder.embed(None)
            assert False, "Complete embedding should reject a missing chunk collection"
        except ValueError:
            pass
        try:
            embedder.embed([None])
            assert False, "Complete embedding should reject a collection containing a non-Document value"
        except ValueError:
            pass
        print(green("Version 0.3.5 complete embedding pipeline is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.3.5 failed"))

    try:
        tests += 1
        from classes.chunker import Chunker
        from classes.document import Document
        from classes.embedding_provider import EmbeddingProvider
        from classes.embedder import Embedder
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        class VectorEmbeddingProvider(EmbeddingProvider):
            def embed(self, text):
                return [float(len(text)), 1.0, 2.0]
        logger = Logger()
        provider = VectorEmbeddingProvider()
        embedder = Embedder(provider, logger)
        chunker = Chunker(logger, chunk_size=20)
        store = VectorStore(logger)
        document = Document(
            "This document contains information for vector storage testing.",
            "vector_store_test.txt",
            {"category": "test", "source_type": "text"}
        )
        chunks = chunker.chunk(document)
        embedded = embedder.embed(chunks)
        assert isinstance(store.vectors, dict), "Vector storage should maintain an internal vector collection"
        assert len(store.vectors) == 0, "A new vector store should begin empty"
        assert isinstance(embedded, list), "Vector storage should receive embedding results as a list"
        vector_id = store.add(embedded[0])
        assert isinstance(vector_id, str), "Vector storage should return a string identifier when storing a vector"
        assert vector_id == embedded[0]["chunk"].id, "Stored vector identifiers should correspond to their source chunk identity"
        assert len(store.vectors) == 1, "Vector storage should contain the vector after it is added"
        assert vector_id in store.vectors, "Vector storage should index stored vectors by their identifiers"
        stored = store.get(vector_id)
        assert isinstance(stored, dict), "Vector storage should return stored records as dictionaries"
        assert stored["chunk"] is embedded[0]["chunk"], "Vector storage should preserve the source chunk object"
        assert stored["embedding"] == embedded[0]["embedding"], "Vector storage should preserve the complete embedding vector"
        assert stored["metadata"] == embedded[0]["metadata"], "Vector storage should preserve embedding metadata"
        assert stored["metadata"] is not embedded[0]["metadata"], "Vector storage should keep stored metadata independent from the embedding result"
        assert store.get("missing-vector-id") is None, "Vector storage should return None for an unknown vector identifier"
        try:
            VectorStore(None)
            assert False, "Vector storage should reject a missing Logger dependency"
        except ValueError:
            pass
        try:
            store.add(None)
            assert False, "Vector storage should reject a missing embedding record"
        except ValueError:
            pass
        try:
            store.add({})
            assert False, "Vector storage should reject an embedding record missing its chunk"
        except ValueError:
            pass
        try:
            store.add({"chunk": embedded[0]["chunk"]})
            assert False, "Vector storage should reject an embedding record missing its vector"
        except ValueError:
            pass
        try:
            store.add({
                "chunk": embedded[0]["chunk"],
                "embedding": []
            })
            assert False, "Vector storage should reject empty embedding vectors"
        except ValueError:
            pass
        try:
            store.get("")
            assert False, "Vector storage should reject an empty vector identifier"
        except ValueError:
            pass
        print(green("Version 0.4.0 vector storage foundation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.0 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        document_one = Document(
            "First vector storage validation document.",
            "validation_one.txt"
        )
        document_two = Document(
            "Second vector storage validation document.",
            "validation_two.txt"
        )
        embedding_one = {
            "chunk": document_one,
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {"source": "validation_one.txt"}
        }
        embedding_two = {
            "chunk": document_two,
            "embedding": [0.4, 0.5, 0.6],
            "metadata": {"source": "validation_two.txt"}
        }
        first_id = store.add(embedding_one)
        second_id = store.add(embedding_two)
        assert store.dimension == 3, "Vector storage should establish its dimension from the first stored vector"
        assert len(store.vectors) == 2, "Vector storage should accept multiple vectors with the same dimension"
        assert first_id != second_id, "Different chunks should receive different vector identifiers"
        try:
            store.add({
                "chunk": "not a document",
                "embedding": [0.1, 0.2, 0.3]
            })
            assert False, "Vector storage should reject a chunk that is not a Document"
        except ValueError:
            pass
        try:
            store.add({
                "chunk": document_one,
                "embedding": "not a vector"
            })
            assert False, "Vector storage should reject an embedding that is not a list or tuple"
        except ValueError:
            pass
        try:
            store.add({
                "chunk": document_one,
                "embedding": [0.1, "invalid", 0.3]
            })
            assert False, "Vector storage should reject vectors containing non-numeric values"
        except ValueError:
            pass
        try:
            store.add({
                "chunk": document_one,
                "embedding": [0.1, 0.2]
            })
            assert False, "Vector storage should reject vectors with a mismatched dimension"
        except ValueError:
            pass
        try:
            store.add({
                "chunk": document_one,
                "embedding": [0.1, 0.2, 0.3],
                "metadata": "invalid metadata"
            })
            assert False, "Vector storage should reject metadata that is not a dictionary"
        except ValueError:
            pass
        assert len(store.vectors) == 2, "Failed vector validation should not modify stored vectors"
        print(green("Version 0.4.1 vector storage validation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.1 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        document_one = Document(
            "First batch vector storage document.",
            "batch_one.txt"
        )
        document_two = Document(
            "Second batch vector storage document.",
            "batch_two.txt"
        )
        document_three = Document(
            "Third batch vector storage document.",
            "batch_three.txt"
        )
        embeddings = [
            {
                "chunk": document_one,
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"source": "batch_one.txt"}
            },
            {
                "chunk": document_two,
                "embedding": [0.4, 0.5, 0.6],
                "metadata": {"source": "batch_two.txt"}
            },
            {
                "chunk": document_three,
                "embedding": [0.7, 0.8, 0.9],
                "metadata": {"source": "batch_three.txt"}
            }
        ]
        vector_ids = store.add_many(embeddings)
        assert isinstance(vector_ids, list), "Batch vector storage should return a list of vector identifiers"
        assert len(vector_ids) == 3, "Batch vector storage should return one identifier for each embedding"
        assert vector_ids == [document_one.id, document_two.id, document_three.id], "Batch vector storage should preserve embedding order"
        assert len(store.vectors) == 3, "Batch vector storage should store every supplied embedding"
        assert store.get(vector_ids[0])["embedding"] == [0.1, 0.2, 0.3], "Batch vector storage should preserve the first embedding vector"
        assert store.get(vector_ids[1])["embedding"] == [0.4, 0.5, 0.6], "Batch vector storage should preserve the second embedding vector"
        assert store.get(vector_ids[2])["embedding"] == [0.7, 0.8, 0.9], "Batch vector storage should preserve the third embedding vector"
        assert store.dimension == 3, "Batch vector storage should maintain the vector dimension"
        try:
            store.add_many(None)
            assert False, "Batch vector storage should reject a missing embedding collection"
        except ValueError:
            pass
        try:
            store.add_many("invalid embeddings")
            assert False, "Batch vector storage should reject a non-list embedding collection"
        except ValueError:
            pass
        try:
            store.add_many([
                {
                    "chunk": Document("Invalid batch document.", "invalid_batch.txt"),
                    "embedding": [1.0, 2.0]
                }
            ])
            assert False, "Batch vector storage should reject vectors with mismatched dimensions"
        except ValueError:
            pass
        assert len(store.vectors) == 3, "Failed batch validation should not add invalid vectors"
        print(green("Version 0.4.2 batch vector storage is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.2 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        document_one = Document(
            "First retrieval document.",
            "retrieval_one.txt"
        )
        document_two = Document(
            "Second retrieval document.",
            "retrieval_two.txt"
        )
        embeddings = [
            {
                "chunk": document_one,
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"source": "retrieval_one.txt"}
            },
            {
                "chunk": document_two,
                "embedding": [0.4, 0.5, 0.6],
                "metadata": {"source": "retrieval_two.txt"}
            }
        ]
        store.add_many(embeddings)
        all_vectors = store.get_all()
        assert isinstance(all_vectors, dict), "Vector storage should return all stored vectors as a dictionary"
        assert len(all_vectors) == 2, "Vector storage should return every stored vector"
        assert document_one.id in all_vectors, "Vector storage should include the first stored vector"
        assert document_two.id in all_vectors, "Vector storage should include the second stored vector"
        assert all_vectors[document_one.id]["chunk"] is document_one, "Retrieved records should preserve their source chunks"
        assert all_vectors[document_one.id]["embedding"] == [0.1, 0.2, 0.3], "Retrieved records should preserve their embedding vectors"
        assert all_vectors[document_one.id]["metadata"] == {"source": "retrieval_one.txt"}, "Retrieved records should preserve their metadata"
        all_vectors[document_one.id]["embedding"].append(99.0)
        all_vectors[document_one.id]["metadata"]["modified"] = True
        stored = store.get(document_one.id)
        assert stored["embedding"] == [0.1, 0.2, 0.3], "Retrieved embeddings should not allow external mutation of stored vectors"
        assert "modified" not in stored["metadata"], "Retrieved metadata should not allow external mutation of stored metadata"
        assert store.get_all() != {}, "Vector storage should retain stored records after retrieval"
        print(green("Version 0.4.3 vector storage retrieval is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.3 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        document_one = Document(
            "First removal document.",
            "removal_one.txt"
        )
        document_two = Document(
            "Second removal document.",
            "removal_two.txt"
        )
        store.add_many([
            {
                "chunk": document_one,
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"source": "removal_one.txt"}
            },
            {
                "chunk": document_two,
                "embedding": [0.4, 0.5, 0.6],
                "metadata": {"source": "removal_two.txt"}
            }
        ])
        assert len(store.vectors) == 2, "Vector storage should contain both vectors before removal"
        removed = store.remove(document_one.id)
        assert removed is True, "Vector storage should report successful removal"
        assert len(store.vectors) == 1, "Vector storage should contain one fewer vector after removal"
        assert store.get(document_one.id) is None, "Removed vectors should no longer be retrievable"
        assert store.get(document_two.id) is not None, "Removing one vector should preserve other stored vectors"
        removed_again = store.remove(document_one.id)
        assert removed_again is False, "Removing an unknown vector should return False"
        assert len(store.vectors) == 1, "Removing an unknown vector should not modify stored vectors"
        remaining = store.get_all()
        assert document_two.id in remaining, "The remaining vector should still exist after removal"
        store.remove(document_two.id)
        assert len(store.vectors) == 0, "Removing the final vector should empty the vector store"
        assert store.dimension is None, "An empty vector store should reset its vector dimension"
        try:
            store.remove("")
            assert False, "Vector storage should reject an empty vector identifier during removal"
        except ValueError:
            pass
        try:
            store.remove(None)
            assert False, "Vector storage should reject a non-string vector identifier during removal"
        except ValueError:
            pass
        print(green("Version 0.4.4 vector removal is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.4 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        document_one = Document(
            "First clear test document.",
            "clear_one.txt"
        )
        document_two = Document(
            "Second clear test document.",
            "clear_two.txt"
        )
        document_three = Document(
            "Third clear test document.",
            "clear_three.txt"
        )
        store.add_many([
            {
                "chunk": document_one,
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"source": "clear_one.txt"}
            },
            {
                "chunk": document_two,
                "embedding": [0.4, 0.5, 0.6],
                "metadata": {"source": "clear_two.txt"}
            },
            {
                "chunk": document_three,
                "embedding": [0.7, 0.8, 0.9],
                "metadata": {"source": "clear_three.txt"}
            }
        ])
        assert len(store.vectors) == 3, "Vector storage should contain all vectors before clearing"
        assert store.dimension == 3, "Vector storage should have an established dimension before clearing"
        removed_count = store.clear()
        assert removed_count == 3, "Vector storage should report the number of vectors removed during clearing"
        assert len(store.vectors) == 0, "Vector storage should be empty after clearing"
        assert store.get(document_one.id) is None, "Cleared vectors should no longer be retrievable"
        assert store.get(document_two.id) is None, "All stored vectors should be removed during clearing"
        assert store.get(document_three.id) is None, "The final stored vector should be removed during clearing"
        assert store.dimension is None, "Vector storage should reset its dimension after clearing"
        second_clear_count = store.clear()
        assert second_clear_count == 0, "Clearing an already empty vector store should report zero removals"
        assert len(store.vectors) == 0, "Clearing an already empty vector store should keep it empty"
        assert store.dimension is None, "Clearing an already empty vector store should keep its dimension unset"
        document_four = Document(
            "Document added after clearing.",
            "clear_four.txt"
        )
        vector_id = store.add({
            "chunk": document_four,
            "embedding": [1.0, 2.0, 3.0],
            "metadata": {"source": "clear_four.txt"}
        })
        assert vector_id == document_four.id, "Vector storage should accept new vectors after being cleared"
        assert len(store.vectors) == 1, "Vector storage should contain newly added vectors after clearing"
        assert store.dimension == 3, "Vector storage should establish its dimension again after receiving a new vector"
        print(green("Version 0.4.5 vector store clearing is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.5 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        assert store.count() == 0, "A new vector store should report zero stored vectors"
        document_one = Document(
            "First count test document.",
            "count_one.txt"
        )
        document_two = Document(
            "Second count test document.",
            "count_two.txt"
        )
        store.add({
            "chunk": document_one,
            "embedding": [0.1, 0.2, 0.3]
        })
        assert store.count() == 1, "Vector storage should report one stored vector after one vector is added"
        store.add({
            "chunk": document_two,
            "embedding": [0.4, 0.5, 0.6]
        })
        assert store.count() == 2, "Vector storage should report the total number of stored vectors"
        store.remove(document_one.id)
        assert store.count() == 1, "Vector storage count should decrease when a vector is removed"
        store.clear()
        assert store.count() == 0, "Vector storage count should return zero after the store is cleared"
        document_three = Document(
            "Third count test document.",
            "count_three.txt"
        )
        store.add({
            "chunk": document_three,
            "embedding": [0.7, 0.8, 0.9]
        })
        assert store.count() == 1, "Vector storage count should work after the store has been cleared and reused"
        assert store.count() == len(store.vectors), "Vector storage count should match the number of internally stored vectors"
        print(green("Version 0.4.6 vector store counting is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.6 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        document = Document(
            "Vector existence test document.",
            "contains_test.txt"
        )
        vector_id = store.add({
            "chunk": document,
            "embedding": [0.1, 0.2, 0.3]
        })
        assert store.contains(vector_id) is True, "Vector storage should report True for an existing vector"
        assert store.contains(document.id) is True, "Vector storage should recognize the source chunk identifier"
        assert store.contains("missing-vector-id") is False, "Vector storage should report False for an unknown vector"
        store.remove(vector_id)
        assert store.contains(vector_id) is False, "Vector storage should report False after a vector is removed"
        assert store.count() == 0, "Vector storage should contain zero vectors after removing the only vector"
        document_two = Document(
            "Second vector existence test document.",
            "contains_test_two.txt"
        )
        second_id = store.add({
            "chunk": document_two,
            "embedding": [0.4, 0.5, 0.6]
        })
        assert store.contains(second_id) is True, "Vector storage should support existence checks after reuse"
        store.clear()
        assert store.contains(second_id) is False, "Vector storage should report False for vectors after clearing"
        try:
            store.contains("")
            assert False, "Vector storage should reject an empty vector identifier"
        except ValueError:
            pass
        try:
            store.contains(None)
            assert False, "Vector storage should reject a non-string vector identifier"
        except ValueError:
            pass
        print(green("Version 0.4.7 vector existence checking is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.7 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        document = Document(
            "Vector metadata access test document.",
            "metadata_test.txt"
        )
        metadata = {
            "source": "metadata_test.txt",
            "category": "testing",
            "priority": "high"
        }
        vector_id = store.add({
            "chunk": document,
            "embedding": [0.1, 0.2, 0.3],
            "metadata": metadata
        })
        result = store.get_metadata(vector_id)
        assert isinstance(result, dict), "Vector storage should return vector metadata as a dictionary"
        assert result == metadata, "Vector storage should return the complete metadata for a stored vector"
        assert result is not metadata, "Vector storage should return an independent metadata copy"
        result["modified"] = True
        stored = store.get_metadata(vector_id)
        assert "modified" not in stored, "Modifying returned metadata should not modify stored metadata"
        assert store.get(vector_id)["metadata"] == metadata, "Stored metadata should remain unchanged after external modification"
        assert store.get_metadata("missing-vector-id") is None, "Vector storage should return None for metadata of an unknown vector"
        store.remove(vector_id)
        assert store.get_metadata(vector_id) is None, "Vector storage should return None for metadata after a vector is removed"
        try:
            store.get_metadata("")
            assert False, "Vector storage should reject an empty vector identifier for metadata access"
        except ValueError:
            pass
        try:
            store.get_metadata(None)
            assert False, "Vector storage should reject a non-string vector identifier for metadata access"
        except ValueError:
            pass
        print(green("Version 0.4.8 vector metadata access is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.8 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        document = Document(
            "Complete vector record access test document.",
            "record_test.txt"
        )
        metadata = {
            "source": "record_test.txt",
            "category": "testing"
        }
        embedding = [0.1, 0.2, 0.3]
        vector_id = store.add({
            "chunk": document,
            "embedding": embedding,
            "metadata": metadata
        })
        record = store.get_record(vector_id)
        assert isinstance(record, dict), "Vector storage should return complete records as dictionaries"
        assert set(record.keys()) == {"chunk", "embedding", "metadata"}, "Vector storage records should contain chunk, embedding, and metadata"
        assert record["chunk"] is document, "Vector storage records should preserve the source chunk"
        assert record["embedding"] == embedding, "Vector storage records should preserve the complete embedding"
        assert record["metadata"] == metadata, "Vector storage records should preserve the complete metadata"
        assert record["embedding"] is not store.vectors[vector_id]["embedding"], "Vector storage should return an independent embedding copy"
        assert record["metadata"] is not store.vectors[vector_id]["metadata"], "Vector storage should return an independent metadata copy"
        record["embedding"].append(9.9)
        record["metadata"]["modified"] = True
        stored = store.get_record(vector_id)
        assert stored["embedding"] == embedding, "Modifying a returned record should not modify the stored embedding"
        assert stored["metadata"] == metadata, "Modifying a returned record should not modify the stored metadata"
        assert store.get_record("missing-vector-id") is None, "Vector storage should return None for an unknown record"
        store.remove(vector_id)
        assert store.get_record(vector_id) is None, "Vector storage should return None after a record is removed"
        try:
            store.get_record("")
            assert False, "Vector storage should reject an empty vector identifier for record access"
        except ValueError:
            pass
        try:
            store.get_record(None)
            assert False, "Vector storage should reject a non-string vector identifier for record access"
        except ValueError:
            pass
        print(green("Version 0.4.9 vector record access is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.9 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        document = Document(
            "Vector update test document.",
            "update_test.txt"
        )
        original_embedding = {
            "chunk": document,
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {"version": 1}
        }
        vector_id = store.add(original_embedding)
        assert store.count() == 1, "Vector storage should contain one vector before updating"
        assert store.get(vector_id)["embedding"] == [0.1, 0.2, 0.3], "Vector storage should contain the original embedding before updating"
        updated_embedding = {
            "chunk": document,
            "embedding": [0.9, 0.8, 0.7],
            "metadata": {"version": 2}
        }
        updated = store.update(updated_embedding)
        assert updated is True, "Vector storage should report successful updates for existing vectors"
        assert store.count() == 1, "Updating a vector should not create an additional stored vector"
        assert store.get(vector_id)["embedding"] == [0.9, 0.8, 0.7], "Vector storage should replace the existing embedding during an update"
        assert store.get_metadata(vector_id) == {"version": 2}, "Vector storage should replace metadata during an update"
        assert store.get_record(vector_id)["chunk"] is document, "Vector storage should preserve the updated record's source chunk"
        assert store.contains(vector_id) is True, "An updated vector should remain present in the vector store"
        unknown_document = Document(
            "Unknown update document.",
            "unknown_update.txt"
        )
        unknown_result = store.update({
            "chunk": unknown_document,
            "embedding": [0.4, 0.5, 0.6],
            "metadata": {"version": 1}
        })
        assert unknown_result is False, "Updating an unknown vector should return False"
        assert store.count() == 1, "Updating an unknown vector should not modify the number of stored vectors"
        try:
            store.update({
                "chunk": "not a document",
                "embedding": [0.1, 0.2, 0.3]
            })
            assert False, "Vector storage should reject a non-Document chunk during an update"
        except ValueError:
            pass
        try:
            store.update({
                "chunk": document,
                "embedding": [0.1, "invalid", 0.3]
            })
            assert False, "Vector storage should reject non-numeric values during an update"
        except ValueError:
            pass
        try:
            store.update({
                "chunk": document,
                "embedding": [0.1, 0.2],
                "metadata": {"version": 3}
            })
            assert False, "Vector storage should reject mismatched vector dimensions during an update"
        except ValueError:
            pass
        assert store.get(vector_id)["embedding"] == [0.9, 0.8, 0.7], "Failed updates should not overwrite the existing valid embedding"
        print(green("Version 0.4.10 vector store updating is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.10 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        document = Document(
            "Vector atomic update test document.",
            "atomic_update.txt"
        )
        vector_id = store.add({
            "chunk": document,
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {
                "version": 1,
                "status": "original"
            }
        })
        original_record = store.get_record(vector_id)
        try:
            store.update({
                "chunk": document,
                "embedding": [0.9, "invalid", 0.7],
                "metadata": {
                    "version": 2,
                    "status": "invalid"
                }
            })
            assert False, "Vector storage should reject invalid vector values during an update"
        except ValueError:
            pass
        assert store.get_record(vector_id) == original_record, "A failed vector update should leave the original record unchanged"
        try:
            store.update({
                "chunk": document,
                "embedding": [0.9, 0.8],
                "metadata": {
                    "version": 2,
                    "status": "invalid"
                }
            })
            assert False, "Vector storage should reject mismatched dimensions during an update"
        except ValueError:
            pass
        assert store.get_record(vector_id) == original_record, "A dimension validation failure should leave the original record unchanged"
        try:
            store.update({
                "chunk": document,
                "embedding": [0.9, 0.8, 0.7],
                "metadata": "invalid metadata"
            })
            assert False, "Vector storage should reject invalid metadata during an update"
        except ValueError:
            pass
        assert store.get_record(vector_id) == original_record, "A metadata validation failure should leave the original record unchanged"
        valid_update = store.update({
            "chunk": document,
            "embedding": [0.9, 0.8, 0.7],
            "metadata": {
                "version": 2,
                "status": "updated"
            }
        })
        assert valid_update is True, "Vector storage should successfully apply a valid update"
        assert store.get_record(vector_id)["embedding"] == [0.9, 0.8, 0.7], "A valid update should replace the stored embedding"
        assert store.get_metadata(vector_id) == {"version": 2, "status": "updated"}, "A valid update should replace the stored metadata"
        assert store.count() == 1, "Successful updates should not change the number of stored vectors"
        print(green("Version 0.4.11 vector store update validation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.11 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        assert store.is_empty() is True, "A new vector store should report that it is empty"
        document_one = Document(
            "Vector empty state test document.",
            "empty_state_one.txt"
        )
        store.add({
            "chunk": document_one,
            "embedding": [0.1, 0.2, 0.3]
        })
        assert store.is_empty() is False, "Vector storage should report that it is not empty after a vector is added"
        assert store.count() == 1, "Vector storage should contain one vector after the first vector is added"
        store.remove(document_one.id)
        assert store.is_empty() is True, "Vector storage should report that it is empty after its final vector is removed"
        document_two = Document(
            "Second vector empty state test document.",
            "empty_state_two.txt"
        )
        store.add({
            "chunk": document_two,
            "embedding": [0.4, 0.5, 0.6]
        })
        assert store.is_empty() is False, "Vector storage should report that it is not empty after being reused"
        store.clear()
        assert store.is_empty() is True, "Vector storage should report that it is empty after being cleared"
        assert store.count() == 0, "An empty vector store should report zero stored vectors"
        assert store.get_all() == {}, "An empty vector store should return an empty collection"
        print(green("Version 0.4.12 vector store empty-state reporting is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.12 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        document = Document(
            "Vector metadata isolation test document.",
            "metadata_isolation.txt"
        )
        original_metadata = {
            "source": "metadata_isolation.txt",
            "category": "testing",
            "version": 1
        }
        embedding = {
            "chunk": document,
            "embedding": [0.1, 0.2, 0.3],
            "metadata": original_metadata
        }
        vector_id = store.add(embedding)
        original_metadata["modified"] = True
        original_metadata["version"] = 99
        stored_metadata = store.get_metadata(vector_id)
        assert "modified" not in stored_metadata, "Modifying input metadata after storage should not modify stored metadata"
        assert stored_metadata["version"] == 1, "Modifying input metadata should not change previously stored metadata values"
        update_metadata = {
            "source": "metadata_isolation.txt",
            "category": "updated",
            "version": 2
        }
        updated = store.update({
            "chunk": document,
            "embedding": [0.4, 0.5, 0.6],
            "metadata": update_metadata
        })
        assert updated is True, "Vector storage should successfully update an existing vector"
        update_metadata["modified"] = True
        update_metadata["version"] = 99
        stored_metadata = store.get_metadata(vector_id)
        assert "modified" not in stored_metadata, "Modifying update metadata after storage should not modify stored metadata"
        assert stored_metadata["category"] == "updated", "Stored metadata should preserve the values supplied by the successful update"
        assert stored_metadata["version"] == 2, "Modifying update metadata should not change the stored update values"
        assert store.get_record(vector_id)["metadata"] == stored_metadata, "Complete record access should expose the same isolated metadata values"
        print(green("Version 0.4.13 vector metadata isolation is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.13 failed"))

    try:
        tests += 1
        from classes.document import Document
        from classes.logger import Logger
        from classes.vector_store import VectorStore
        logger = Logger()
        store = VectorStore(logger)
        document_one = Document(
            "First upsert test document.",
            "upsert_one.txt"
        )
        first_embedding = {
            "chunk": document_one,
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {"version": 1}
        }
        first_id = store.upsert(first_embedding)
        assert first_id == document_one.id, "Vector upsert should return the source chunk identifier"
        assert store.count() == 1, "Upserting a new vector should add one vector to the store"
        assert store.get(first_id)["embedding"] == [0.1, 0.2, 0.3], "Upserting a new vector should store its embedding"
        assert store.get_metadata(first_id) == {"version": 1}, "Upserting a new vector should store its metadata"
        updated_embedding = {
            "chunk": document_one,
            "embedding": [0.9, 0.8, 0.7],
            "metadata": {"version": 2}
        }
        second_id = store.upsert(updated_embedding)
        assert second_id == first_id, "Upserting an existing vector should preserve its identifier"
        assert store.count() == 1, "Upserting an existing vector should not create a duplicate"
        assert store.get(first_id)["embedding"] == [0.9, 0.8, 0.7], "Upserting an existing vector should replace its embedding"
        assert store.get_metadata(first_id) == {"version": 2}, "Upserting an existing vector should replace its metadata"
        document_two = Document(
            "Second upsert test document.",
            "upsert_two.txt"
        )
        third_id = store.upsert({
            "chunk": document_two,
            "embedding": [0.4, 0.5, 0.6],
            "metadata": {"version": 1}
        })
        assert third_id == document_two.id, "Upserting another new vector should return its chunk identifier"
        assert store.count() == 2, "Upserting another new vector should increase the store count"
        try:
            store.upsert({
                "chunk": "not a document",
                "embedding": [0.1, 0.2, 0.3]
            })
            assert False, "Vector upsert should reject a non-Document chunk"
        except ValueError:
            pass
        assert store.count() == 2, "A failed upsert should not modify the number of stored vectors"
        assert store.get(first_id)["embedding"] == [0.9, 0.8, 0.7], "A failed upsert should preserve existing vector data"
        print(green("Version 0.4.14 vector upsert is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.14 failed"))

    try:
        tests += 1
        existing_embedding = {
            "chunk": chunk,
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {"type": "text"}
        }
        new_embedding = {
            "chunk": Document("New chunk", "test.txt"),
            "embedding": [0.4, 0.5, 0.6],
            "metadata": {"type": "new"}
        }
        updated_embedding = {
            "chunk": chunk,
            "embedding": [0.7, 0.8, 0.9],
            "metadata": {"type": "updated"}
        }
        invalid_embedding = {
            "chunk": "invalid",
            "embedding": [1.0, 1.1, 1.2],
            "metadata": {"type": "invalid"}
        }
        store.upsert(existing_embedding)
        count_before = store.count()
        vector_ids = store.upsert_many([updated_embedding, invalid_embedding, new_embedding])
        assert vector_ids == [chunk.id, new_embedding["chunk"].id], "Upsert_many should return IDs only for valid embeddings in input order"
        assert store.count() == count_before + 1, "Upsert_many should update existing vectors, ignore invalid embeddings, and add valid new vectors"
        assert store.get(chunk.id)["embedding"] == [0.7, 0.8, 0.9], "Upsert_many should update the existing embedding"
        assert store.get(chunk.id)["metadata"] == {"type": "updated"}, "Upsert_many should replace metadata for the existing embedding"
        assert store.get(new_embedding["chunk"].id)["embedding"] == [0.4, 0.5, 0.6], "Upsert_many should add the valid new embedding"
        assert store.get(new_embedding["chunk"].id)["metadata"] == {"type": "new"}, "Upsert_many should preserve metadata for the valid new embedding"
        assert not store.contains(invalid_embedding.get("chunk")), "Upsert_many should not store an invalid embedding"
        try:
            store.upsert_many("invalid")
            assert False, "Upsert_many should reject non-list and non-tuple input"
        except ValueError:
            pass
        print(green("Version 0.4.15 vector store batch upsert is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.15 failed"))

    try:
        tests += 1
        existing_embedding = {
            "chunk": chunk,
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {"type": "text"}
        }
        new_embedding = {
            "chunk": Document("New chunk", "test.txt"),
            "embedding": [0.4, 0.5, 0.6],
            "metadata": {"type": "new"}
        }
        updated_embedding = {
            "chunk": chunk,
            "embedding": [0.7, 0.8, 0.9],
            "metadata": {"type": "updated"}
        }
        invalid_embedding = {
            "chunk": "invalid",
            "embedding": [1.0, 1.1, 1.2],
            "metadata": {"type": "invalid"}
        }
        store.upsert(existing_embedding)
        vector_ids = store.upsert_many([updated_embedding, invalid_embedding, new_embedding])
        assert vector_ids == [chunk.id, new_embedding["chunk"].id], "Upsert_many should return IDs only for successfully upserted embeddings"
        assert store.upsert_successes == 2, "Upsert_many should record two successful upserts"
        assert store.upsert_failures == 1, "Upsert_many should record one skipped invalid embedding"
        assert store.get(chunk.id)["embedding"] == [0.7, 0.8, 0.9], "Upsert_many should update the existing embedding"
        assert store.get(new_embedding["chunk"].id)["embedding"] == [0.4, 0.5, 0.6], "Upsert_many should store the valid new embedding"
        try:
            store.upsert_many("invalid")
            assert False, "Upsert_many should reject non-list and non-tuple input"
        except ValueError:
            pass
        print(green("Version 0.4.16 vector store upsert failure tracking is online."))
        success += 1
    except Exception as e:
        failure += 1
        print(red(e))
        print(red("Version 0.4.16 failed"))

    if failure > 0:
        print(red(f"There was {failure} failures, please fix."))
    else:
        print(green(f"All versions online! {success}/{tests}"))
