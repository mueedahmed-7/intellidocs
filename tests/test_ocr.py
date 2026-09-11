"""OCR fallback tests using fake PDF pages; Tesseract is never required."""

import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from langchain_core.documents import Document

from backend.Services.document_service import DocumentService, DocumentValidationError
from backend.Services.ocr_service import OCRProcessingError, OCRUnavailableError
from backend.rag.loader import DocumentLoader


class FakePage:
    def __init__(self, native_text): self.native_text = native_text
    def get_text(self, _kind): return self.native_text


class FakePdf:
    def __init__(self, pages): self.pages, self.closed = pages, False
    def __len__(self): return len(self.pages)
    def __iter__(self): return iter(self.pages)
    def close(self): self.closed = True


class FakeOCR:
    def __init__(self, text_by_page=None, error=None): self.text_by_page, self.error, self.calls = text_by_page or {}, error, []
    def ocr_page(self, page):
        self.calls.append(page)
        if self.error: raise self.error
        return self.text_by_page.get(id(page), "")


class Snapshot:
    def __init__(self, collection, key): self.collection, self.id = collection, key
    @property
    def exists(self): return self.id in self.collection.data
    def get(self): return self
    def to_dict(self): return dict(self.collection.data[self.id])
    def set(self, value): self.collection.data[self.id] = dict(value)
    def update(self, value): self.collection.data[self.id].update(value)


class Collection:
    def __init__(self): self.data = {}
    def document(self, key): return Snapshot(self, key)


class Splitter:
    def split_documents(self, documents): return [Document(page_content=item.page_content, metadata=dict(item.metadata)) for item in documents]


class Embeddings:
    def generate_embeddings(self, chunks): return np.zeros((len(chunks), 2), dtype=np.float32)


class Vectors:
    def __init__(self): self.records, self.deleted = [], []
    def add_documents(self, chunks, embeddings, ids): self.records.extend(zip(ids, chunks))
    def delete_document_vectors(self, user_id, document_id): self.deleted.append((user_id, document_id))


class OCRTests(unittest.TestCase):
    def load_pages(self, pages, ocr):
        pdf = FakePdf(pages)
        module = types.SimpleNamespace(open=lambda _path: pdf)
        with tempfile.TemporaryDirectory() as directory, patch.dict(sys.modules, {"fitz": module}):
            path = Path(directory) / "sample.pdf"; path.write_bytes(b"pdf")
            loader = DocumentLoader(ocr_service=ocr)
            documents = loader.load_document(str(path))
        return documents, loader, pdf

    def test_digital_pdf_uses_native_text_without_ocr(self):
        ocr = FakeOCR()
        documents, loader, pdf = self.load_pages([FakePage("A normal digital PDF with enough meaningful text for extraction.")], ocr)
        self.assertEqual(len(ocr.calls), 0)
        self.assertEqual(loader.last_extraction_info["extraction_method"], "native")
        self.assertEqual(documents[0].metadata["page"], 1)
        self.assertTrue(pdf.closed)

    def test_scanned_and_mixed_pdf_use_ocr_only_for_needed_pages(self):
        text_page, scanned_page = FakePage("This page is native text with enough words."), FakePage("")
        ocr = FakeOCR({id(scanned_page): "Fee Amount: 45,000 PKR\nDue Date: 20 September 2026\nVoucher No: ABC123"})
        documents, loader, _ = self.load_pages([text_page, scanned_page], ocr)
        self.assertEqual(len(ocr.calls), 1)
        self.assertEqual(loader.last_extraction_info, {"extraction_method": "mixed", "ocr_pages": 1})
        self.assertEqual(documents[1].metadata["page"], 2)
        self.assertIn("45,000 PKR", documents[1].page_content)

    def test_empty_ocr_and_unavailable_engine_fail_safely(self):
        with self.assertRaises(OCRProcessingError): self.load_pages([FakePage("")], FakeOCR())
        with self.assertRaises(OCRUnavailableError): self.load_pages([FakePage("")], FakeOCR(error=OCRUnavailableError("OCR unavailable")))

    def test_ocr_documents_enter_normal_vector_pipeline_with_page_and_ownership(self):
        page = FakePage("")
        ocr = FakeOCR({id(page): "Student Name: Test Student\nFee Amount: 45,000\nDue Date: 20 September 2026\nVoucher No: ABC123"})
        documents, loader, _ = self.load_pages([page], ocr)
        with tempfile.TemporaryDirectory() as directory:
            vectors = Vectors()
            service = DocumentService(upload_directory=directory, metadata_collection=Collection(), document_loader=types.SimpleNamespace(load_document=lambda _path: documents, last_extraction_info=loader.last_extraction_info), document_splitter=Splitter(), embeddings=Embeddings(), vectors=vectors)
            count, info = service.process_document("ignored.pdf", "user-a", "document-a", "voucher.pdf")
        self.assertEqual(count, 1)
        self.assertEqual(info["extraction_method"], "ocr")
        vector_id, chunk = vectors.records[0]
        self.assertEqual(vector_id, "document-a:0")
        self.assertEqual(chunk.metadata["user_id"], "user-a")
        self.assertEqual(chunk.metadata["document_id"], "document-a")
        self.assertEqual(chunk.metadata["page"], 1)
        self.assertIn("Voucher No", chunk.page_content)

