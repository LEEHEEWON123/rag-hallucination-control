from grounding_pipeline.chunking import chunk_markdown


def test_chunk_markdown_basic():
    text = "# Title\n\n" + ("단락입니다. " * 40) + "\n\n## 다음\n\n" + ("내용. " * 40)
    chunks = chunk_markdown(text, doc_id="demo", source_path="demo.md", chunk_size=120, chunk_overlap=20)
    assert len(chunks) >= 2
    assert chunks[0].doc_id == "demo"
    assert chunks[0].chunk_id.startswith("demo::")
    assert all(c.text for c in chunks)


def test_chunk_rejects_bad_overlap():
    try:
        chunk_markdown("abc", doc_id="x", source_path="x.md", chunk_size=10, chunk_overlap=10)
        assert False, "expected ValueError"
    except ValueError:
        pass
