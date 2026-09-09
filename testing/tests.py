
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
        assert preprocessor.logger is logger, "Preprocessor should retain the exact Logger instance provided during construction"
        assert processed is document, "Initial preprocessing should return the existing Document instance unchanged"
        assert processed.content == document.content, "Initial preprocessing should preserve document content"
        assert processed.source == document.source, "Initial preprocessing should preserve document source"
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

    if failure > 0:
        print(red(f"There was {failure} failures, please fix."))
    else:
        print(green(f"All versions online! {success}/{tests}"))
