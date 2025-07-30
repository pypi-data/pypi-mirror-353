from gemini_application.application_abstract import ApplicationAbstract
from gemini_model.chatassistant.rag import RAG, State
import os
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import hub
from langchain_ollama.llms import OllamaLLM
import chromadb
from langgraph.graph import START, StateGraph


class ChatPopup(ApplicationAbstract):
    def __init__(self):
        super().__init__()

        # Classes
        self.rag_model = RAG()
        self.llm_model = None
        self.docs = None
        self.embeddings_model = None
        self.graph = None
        self.retriever = None
        self.chroma_client = None
        self.chroma_collection = None

        # Variables
        self.langchain_api_key = None
        self.llm_model_version = None
        self.prompt_type = None
        self.chunks = None
        self.docs_dir = None
        self.chroma_dir = None
        self.text_splitter = None
        self.graph_builder = None
        self.prompt = None
        self.chunk_size = None
        self.chunk_overlap = None
        self.add_start_index = None
        self.collection_name = None
        self.chromadb_host = None
        self.chromadb_port = None
        self.ollama_host = None
        self.ollama_port = None

    def init_parameters(self, **kwargs):
        """Function to initialize parameters"""
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.rag_model.create_ollama_client(self.ollama_host, self.ollama_port)

    def initialize_model(self):
        # API key for accessing langchain model
        os.environ["LANGCHAIN_API_KEY"] = (
            self.langchain_api_key
        )

        # Http chromaDB storage, on Docker container
        self.chroma_client = chromadb.HttpClient(host=self.chromadb_host, port=self.chromadb_port)

        # Now create or retrieve the collection
        self.chroma_collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        self.llm_model = OllamaLLM(model=self.llm_model_version)

        self.prompt = hub.pull(self.prompt_type)

        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size,
                                                            chunk_overlap=self.chunk_overlap,
                                                            add_start_index=self.add_start_index)

    def retrieve(self, state: State):
        retrieved_docs = self.chroma_collection.query(query_texts=[state["question"]],
                                                      n_results=3)
        return {"context": retrieved_docs}

    def generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])

        results = self.prompt.invoke({"question": state["question"], "context": docs_content})

        response = self.llm_model.invoke(results)

        return {"answer": response}

    def update_data(self):
        # Step 1: Fetch existing metadata from the collection
        tic = time.time()
        existing_sources = set()
        all_metadata = self.chroma_collection.get(include=["metadatas"])

        if "metadatas" in all_metadata:
            for meta in all_metadata["metadatas"]:
                if meta and "source" in meta:
                    existing_sources.add(meta["source"])
        toc = time.time()
        elapsed_time = toc - tic
        print(f"Model: Fetched existing metadata from collection ({elapsed_time:.5f} s)")

        # Step 2: List all files and filter out existing ones
        all_files = [
            f for f in os.listdir(self.docs_dir)
            if os.path.isfile(os.path.join(self.docs_dir, f))
        ]
        new_files = [f for f in all_files if f not in existing_sources]

        print(f"Model: Found {len(new_files)} new files to process")

        # Step 3: Read only new files
        tic = time.time()
        docs_data = self.rag_model.readfiles(self.docs_dir, filenames=new_files)
        toc = time.time()
        elapsed_time = toc - tic
        print(f"Model: Documents read ({elapsed_time:.5f} s)")

        # Step 4: Process and add new files to ChromaDB
        tic = time.time()
        for filename, text in docs_data.items():
            chunks = self.rag_model.chunksplitter(text, self.chunk_size)
            embeds = self.rag_model.getembedding(self.embeddings_model, chunks)
            ids = [f"{filename}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": filename} for _ in range(len(chunks))]

            # Add the embeddings to the chromadb
            self.chroma_collection.add(
                ids=ids,
                documents=chunks,
                embeddings=embeds,
                metadatas=metadatas
            )
        toc = time.time()
        elapsed_time = toc - tic
        print(f"Model: New files processed ({elapsed_time:.5f} s)")

        # Step 5: Create graph
        tic = time.time()
        self.graph_builder = StateGraph(State).add_sequence([self.retrieve, self.generate])
        self.graph_builder.add_edge(START, "retrieve")

        self.graph = self.graph_builder.compile()
        toc = time.time()
        elapsed_time = toc - tic
        print(f"Model: Graph created ({elapsed_time:.5f} s)")

    def get_embedding(self, user_message: str):
        response = self.rag_model.ollama_client.embeddings(
            model="nomic-embed-text:latest",
            prompt=user_message
        )
        return response['embedding']

    def get_response(self, prompt: str) -> str:
        response = self.rag_model.ollama_client.generate(
            model=self.llm_model_version,
            prompt=prompt,
            stream=False
        )
        # Extract text from response
        return response.model_dump().get("response", "")

    def process_prompt(self, user_message):
        print("processing prompt...")

        # Get embedding of the user query
        tic = time.time()

        query_embed = self.get_embedding(user_message)
        toc = time.time()
        print(f"Model: Embeddings retrieved from user query ({toc - tic:.5f} s)")

        # Retrieve relevant documents
        result = self.chroma_collection.query(
            query_embeddings=query_embed,
            n_results=5,
            include=["documents", "metadatas"]
        )

        documents = result["documents"][0]
        metadatas = result["metadatas"][0]

        # Build prompt
        related_text = "\n\n".join(documents)
        prompt = self.prompt.format(question=user_message, context=related_text)

        # Generate response
        tic = time.time()
        response = self.get_response(prompt)
        toc = time.time()
        print(f"Model: Ollama generated response ({toc - tic:.5f} s)")

        # Format shortened citations
        short_citations = []
        short_sources = []

        for i, meta in enumerate(metadatas):
            filename = meta.get("source", "unknown.txt")
            title = os.path.basename(filename)
            location = f"chunk {i + 1}"  # or use metadata['id'] if available
            short_citations.append(f"{title}, {location}")
            short_sources.append(filename)

        return {
            "answer": response,
            "citations": short_citations,
            "sources": short_sources
        }

    def calculate(self):
        return "Output calculated"
