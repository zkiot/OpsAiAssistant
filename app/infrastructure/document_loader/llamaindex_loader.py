# app/infrastructure/document_loader/llamaindex_loader.py
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter


class LlamaIndexDocumentLoader:
    """只借用 LlamaIndex 的文档读取和切分能力，不用它的 Index/QueryEngine。"""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self._splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def load_and_split(self, directory: str) -> list[str]:
        documents = SimpleDirectoryReader(directory).load_data()
        nodes = self._splitter.get_nodes_from_documents(documents)
        return [node.get_content() for node in nodes]  # 返回纯文本，不返回LlamaIndex的对象