# python
from typing import Any, Dict, List, Optional, Sequence, Union
from langchain_core.documents import BaseDocumentCompressor, Document
from pydantic import ConfigDict, model_validator


class XinferenceRerank(BaseDocumentCompressor):
    """Document compressor that uses `Xinference Rerank API`."""

    client: Any = None
    server_url: Optional[str] = None
    model_uid: Optional[str] = None
    top_n: Optional[int] = 3

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Dict:
        try:
            from xinference.client import RESTfulClient
        except ImportError:
            try:
                from xinference_client import RESTfulClient
            except ImportError as e:
                raise ImportError(
                    "Could not import RESTfulClient from xinference. Please install it"
                    " with `pip install xinference` or `pip install xinference_client`."
                ) from e

        server_url = values.get("server_url")
        model_uid = values.get("model_uid")

        if server_url is None:
            raise ValueError("Please provide server URL")

        if model_uid is None:
            raise ValueError("Please provide the model UID")

        values["client"] = RESTfulClient(server_url)
        return values

    def rerank(
        self,
        documents: Sequence[Union[str, Document, dict]],
        query: str,
        *,
        top_n: Optional[int] = None,
        max_chunks_per_doc: Optional[int] = None,
        return_documents: Optional[bool] = None,
        return_len: Optional[bool] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        if not documents:
            return []
        docs = [doc.page_content if isinstance(doc, Document) else doc for doc in documents]
        model = self.client.get_model(self.model_uid)
        top_n = top_n if (top_n is not None and top_n > 0) else self.top_n
        results = model.rerank(
            documents=docs,
            query=query,
            top_n=top_n,
            max_chunks_per_doc=max_chunks_per_doc,
            return_documents=return_documents,
            return_len=return_len,
            **kwargs,
        )
        if hasattr(results, "results"):
            results = results.results
        items = results["results"]
        return [{"index": r["index"], "relevance_score": r["relevance_score"]} for r in items]

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks=None,
    ) -> Sequence[Document]:
        from copy import deepcopy

        compressed = []
        for res in self.rerank(documents, query):
            doc = documents[res["index"]]
            doc_copy = Document(doc.page_content, metadata=deepcopy(doc.metadata))
            doc_copy.metadata["relevance_score"] = res["relevance_score"]
            compressed.append(doc_copy)
        return compressed
