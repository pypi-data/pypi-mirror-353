import json

from pynostr.event import Event

from agentstr.logger import get_logger
from agentstr.nostr_client import NostrClient

try:
    from langchain_community.embeddings import FakeEmbeddings
    from langchain_core.documents import Document
    from langchain_core.messages import HumanMessage
    from langchain_core.vectorstores import InMemoryVectorStore
    from langchain_openai import ChatOpenAI
    langchain_installed = True
except ImportError:
    FakeEmbeddings = "FakeEmbeddings"
    InMemoryVectorStore = "InMemoryVectorStore"
    Document = "Document"
    HumanMessage = "HumanMessage"
    ChatOpenAI = "ChatOpenAI"
    langchain_installed = False

logger = get_logger(__name__)


class NostrRAG:
    """Retrieval-Augmented Generation (RAG) system for Nostr events.
    
    This class fetches Nostr events, builds a vector store knowledge base, and enables
    semantic search and question answering over the indexed content.
    """
    def __init__(self, nostr_client: NostrClient | None = None, vector_store=None, relays: list[str] | None = None,
                 private_key: str | None = None, nwc_str: str | None = None, embeddings=None, llm=None, llm_model_name=None, llm_base_url=None, llm_api_key=None):
        """Initialize the NostrRAG system.
        
        Args:
            nostr_client: An existing NostrClient instance (optional).
            vector_store: An existing vector store instance (optional).
            relays: List of Nostr relay URLs (if no client provided).
            private_key: Nostr private key in 'nsec' format (if no client provided).
            nwc_str: Nostr Wallet Connect string for payments (optional).
            embeddings: Embedding model for vectorizing documents (defaults to FakeEmbeddings with size 256).
            llm: Language model (optional).
            llm_model_name: Name of the language model to use (optional).
            llm_base_url: Base URL for the language model (optional).
            llm_api_key: API key for the language model (optional).
            
        Raises:
            ImportError: If LangChain is not installed.
        """
        if not langchain_installed:
            logger.error("Langchain not found. Please install it to use NostrRAG. `pip install agentstr-sdk[rag]`")
            raise ImportError("Langchain not found. Please install it to use NostrRAG. `pip install agentstr-sdk[rag]`")
        self.nostr_client = nostr_client or NostrClient(relays=relays, private_key=private_key, nwc_str=nwc_str)
        self.embeddings = embeddings or FakeEmbeddings(size=256)
        self.vector_store = vector_store or InMemoryVectorStore(self.embeddings)
        if llm is None and llm_model_name is None:
            raise ValueError("llm or llm_model_name must be provided")
        self.llm = llm or ChatOpenAI(model_name=llm_model_name, base_url=llm_base_url, api_key=llm_api_key, temperature=0)

    async def _select_hashtags(self, question: str, previous_hashtags: list[str] | None = None) -> list[str]:
        """Select relevant hashtags for the given question.

        Args:
            question: The user's question
            previous_hashtags: Previously used hashtags for this conversation

        Returns:
            List of relevant hashtags
        """
        template = """
You are a hashtag selector for Nostr. Given a question, suggest relevant hashtags that would help find relevant content.
Return ONLY the hashtags in a JSON array format, like: ["#hashtag1", "#hashtag2"]
Use at most 5 hashtags.

Question: {question}
Previous hashtags: {history}
"""

        history = json.dumps(previous_hashtags or [])
        prompt = template.format(question=question, history=history)
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        try:
            hashtags = json.loads(response.content)
            return hashtags
        except json.JSONDecodeError:
            # If the response isn't valid JSON, try to extract hashtags
            text = response.content
            hashtags = []
            # Find hashtags in the text
            for word in text.split():
                if word.startswith("#"):
                    hashtags.append(word)
            return hashtags[:5]  # Return at most 5 hashtags

    def _process_event(self, event: Event) -> Document:
        """Process a Nostr event into a LangChain Document.
        Args:
            event: A Nostr event.
        Returns:
            Document: A LangChain Document with the event's content and ID.
        """
        content = event.content
        metadata = event.to_dict()
        metadata.pop("content")
        return Document(page_content=content, id=event.id, metadata=metadata)

    async def build_knowledge_base(self, question: str, limit: int = 10) -> list[dict]:
        """Build a knowledge base from Nostr events relevant to the question.

        Args:
            question: The user's question to guide hashtag selection
            limit: Maximum number of posts to retrieve

        Returns:
            List of retrieved events
        """
        # Select relevant hashtags for the question
        hashtags = await self._select_hashtags(question)
        hashtags = [hashtag.lstrip("#") for hashtag in hashtags]

        logger.info(f"Selected hashtags: {hashtags}")

        # Fetch events for each hashtag
        events = await self.nostr_client.read_posts_by_tag(tags=hashtags, limit=limit)

        # Process events into documents
        documents = [self._process_event(event) for event in events]
        self.vector_store.add_texts([doc.page_content for doc in documents])

        return events

    async def retrieve(self, question: str, limit: int = 5) -> list[Document]:
        """Retrieve relevant documents from the knowledge base.

        Args:
            question: The user's question
            limit: Maximum number of documents to retrieve

        Returns:
            List of retrieved documents
        """
        await self.build_knowledge_base(question)
        return self.vector_store.similarity_search(question, k=limit)

    async def query(self, question: str, limit: int = 5) -> str:
        """Ask a question using the knowledge base.

        Args:
            question: The user's question
            limit: Number of documents to retrieve for context

        Returns:
            The generated response
        """

        # Get relevant documents
        relevant_docs = await self.retrieve(question, limit)

        # Generate response using the LLM
        template = """
You are an expert assistant. Answer the following question based on the provided context.

Question: {question}

Context:
{context}

Answer:"""

        prompt = template.format(
            question=question,
            context="\n\n".join([doc.page_content for doc in relevant_docs]),
        )

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content
