## Objective

The goal of this project is to develop a REST API that allows users to **index** and **query** their documents within a Vector Database.

 A Vector Database specializes in storing and indexing vector embeddings, enabling fast retrieval and similarity searches. This capability is crucial for applications involving natural language processing, recommendation systems, and many more…

The REST API should be containerized in a Docker container.

### Definitions

To ensure a clear understanding, let's define some key concepts:

1. Chunk: A chunk is a piece of text with an associated embedding and metadata.
2. Document: A document is made out of multiple chunks, it also contains metadata.
3. Library: A library is made out of a list of documents and can also contain other metadata.

The API should:

1. Allow the users to create, read, update, and delete libraries.
2. Allow the users to create, read, update and delete chunks within a library.
3. Index the contents of a library.
4. Do **k-Nearest Neighbor vector search** over the selected library with a given embedding query.

### Guidelines:

The code should be **Python** since that is what we use to develop our backend.

Here is a suggested path on how to implement a basic solution to the problem.

1. Define the Chunk, Document and Library classes. To simplify schema definition, we suggest you use a fixed schema for each of the classes. This means not letting the user define which fields should be present within the metadata for each class. 
    1. Following this path you will have fewer problems validating insertions/updates, but feel to let the users define their own schemas for each library if you are up for the challenge.
    2. Use **Pydantic** for these models.
2. Implement two or three indexing algorithms, do not use external libraries, we want to see you code them up. 
    1. What is the space and time complexity for each of the indexes? 
    2. Why did you choose this index?
3. Implement the necessary data structures/algorithms to ensure that there are no data races between reads and writes to the database. 
    1. Explain your design choices.
4. Create the logic to do the CRUD operations on libraries and documents/chunks. 
    1. Ideally use Services to decouple API endpoints from actual work 
5. Implement an API layer on top of that logic to let users interact with the vector database.
6. Create a docker image for the project

### Extra Points:

Here are some additional suggestions on how to enhance the project even further. You are not required to implement any of these, but if you do, we will value it. If you have other improvements in mind, please feel free to implement them and document them in the project’s README file

1. **Metadata filtering:**
    - Add the possibility of using metadata filters to enhance query results: ie: do kNN search over all chunks created after a given date, whose name contains xyz string etc etc.
2. **Persistence to Disk**:
    - Implement a mechanism to persist the database state to disk, ensuring that the docker container can be restarted and resume its operation from the last checkpoint. Explain your design choices and tradeoffs, considering factors like performance, consistency, and durability.
3. **Leader-Follower Architecture**:
    - Design and implement a leader-follower (master-slave) architecture to support multiple database nodes within the Kubernetes cluster. This architecture should handle read scalability and provide high availability. Explain how leader election, data replication, and failover are managed, along with the benefits and tradeoffs of this approach.
4. **Python SDK Client**:
    - Develop a Python SDK client that interfaces with your API, making it easier for users to interact with the vector database programmatically. Include  documentation and examples.

## Constraints

Do **not** use libraries like chroma-db, pinecone, FAISS, etc to develop the project, we want to see you write the algorithms yourself. You can use numpy to calculate trigonometry functions `cos` , `sin` , etc

You **do not need to build a document processing pipeline** (ocr+text extraction+chunking) to test your system. Using a bunch of manually created chunks will suffice.

## **Tech Stack**

- **API Backend:** Python + FastAPI + Pydantic

## Resources:

[Cohere](https://cohere.com/embeddings) API key to create the embeddings for your test.

```markdown
A1Fi5KBBNoekwBPIa833CBScs6Z2mHEtOXxr52KO
```

## Evaluation Criteria

We will evaluate the code functionality and its quality.

**Code quality:**

- [SOLID design principles](https://realpython.com/solid-principles-python/).
- Use of static typing.
- FastAPI good practices.
- Pydantic schema validation
- Code modularity and reusability.
- Use of RESTful API endpoints.
- Project containerization with Docker.
- Testing
- Error handling.
- If you know what Domain-Driven design is, do it that way!
    - Separate API endpoints from business logic using services and from databases using repositories
- Keep code as pythonic as possible
- Do early returns
- Use inheritance where needed
- Use composition over inheritance