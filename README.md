<p align="center">
<img src="ragit/services/ragit/static/ragit.jpeg"  width="100" height="100">
</p>

# RAGit: A Framework for Generalized RAG Solutions

RAGit is an open-source framework designed to simplify the creation and
management of Retrieval Augmented Generation (RAG) solutions. By abstracting
away the complexities of data management, model selection, and infrastructure,
RAGit empowers developers to focus on application logic and customization. 

# Core Principles

The core principles behind RAGit can be summarized as follows:

### Generality

RAGit can by applied to any set of data than can provided in a wide range of
data types providing a flexible foundation for building custom RAG applications.

### Simplicity

RAGit prioritizes ease of use by abstracting the underlying complexities of data
management. Users can concentrate on refining document selection and optimizing
results without being encumbered by low-level implementation details.

### Configurability

RAGit offers extensive customization options, enabling users to experiment with
various hyperparameters. From chunk splitting strategies to vector distance
algorithms and prompt engineering, users have granular control over the RAG
pipeline.

### Comprehensiveness

Beyond model training and inference, RAGit provides tools for data ingestion,
processing, and management.

### Vendor Neutrality

RAGit is designed to be agnostic to specific underlying technologies, enabling
easy switching between different components and services.

By adhering to these principles, RAGit aims to accelerate the development of
effective and robust RAG solutions. 
   

# Data Pipeline

A high level view of the pipeline associated with RAGit is the following:

### Document Collection

The backend process begins by gathering all supported documents (PDF, DOCX, and
Markdown) from a designated directory. These documents serve as the foundation
for RAG creation.

### Document Splitting and Database Insertion

Each document is divided into smaller chunks, which are then stored in the
database. This process is incremental, allowing for database updates without
requiring all documents upfront.

### Embedding Calculation and Insertion

To enable vector search, embeddings are computed for each database chunk. A
dedicated process identifies chunks lacking embeddings, calculates them, and
stores the results in the database.

### Vector Database Construction

The vector database is built or rebuilt using existing document embeddings. This
is the step that makes the embeddings accessible for the RAG service.

### Front End
The vector database and the front end web service are deployed to a web server
making them available to the public.

### Evaluation and improvements
The front end collects user information to allow for the evalution of the
solution (for example thumps up - down) which results to the backend working on
a peridodic re-creation of the vector database, the prompts and other component
that might affect the quality of the solution.

# Installation

### Build the virtual machine

Currently, the installation requires 
[vagrant](https://developer.hashicorp.com/vagrant/install#darwin)
and virtual box thus mac M3 users
will not be able to install it using this approach. In the case of the mac M3
you can try either using virtual environment of just installing it natively;
either way we will shortly have more details instructions about how to do this.

To install and run RAGIT locally the easiest way is to use a virtual machine
that can be created using vagrant. You will need to have vagrant installed
on your machine . Assuming you already have vagrant installed then you need to
follow these steps to install the repository under your home directory (you
can always install it in any other directory if needed).

```
cd ~
git clone git@github.com:codingismycraft/mygenai.git
mkdir ~/mygen-data
cd mygenai
vagrant up
vagrant ssh
```

Now you can ssh to the newly created virtual machine which should be ready
to go.

### Store a valid OpenAI API key

A valid OpenAI API key stored in a `settings.json` file within your home
directory in the following format:


```json
{
    "OPENAI_API_KEY": "<valid-open-ai-key>"
}
```

**Create the testing database**
```
cd /vagrant/mygenai/db
./create-db.sh
```


**Run the tests**
```
cd /vagrant/mygenai/
pt
```

# Creating a Custom RAG Collection

### Overview

A RAG collection is a fundamental component of the mygenai system. It is
uniquely identified by a `collection name` or simply `name`. This document
outlines the steps involved in creating and managing a custom RAG collection.


### 1. Create the Database

   Navigate to the `db` directory within the `mygenai` project directory and
   execute the `create-db.sh` script:

   ```bash
   cd /vagrant/ragit/db
   ./create-db.sh
   ```
   This will create a PostgreSQL database with the same name as your collection.

### 2. Prepare the Documents Directory

   Create a directory to store your collection's documents:
   ```bash
   mkdir -p ~/mygen-data/<collection-name>/documents
   ```
   Replace `<collection-name>` with the desired name for your collection.

### 3. Populate with Documents
   Copy all relevant documents into the newly created documents directory.

### 4. Process Documents and Create Index
   Navigate to the `utilities` directory and run the `process_docs.py` script:
   ```bash
   cd ragit/utilities
   python3 process_docs.py -n <name> -v
   ```

   Replace `<name>` with your collection name. The `-v` flag provides verbose
   output. This step processes your documents and creates a vector database for
   efficient retrieval.


### Additional Notes

- Ensure you have the necessary dependencies installed for
  running `process_docs.py`.

- For optimal performance, consider organizing your documents effectively (you
can always nest them under the documents directory to make them easier to
navigate)

- Regularly review and update your collection to maintain its relevance.

By following these steps, you can successfully create and manage custom RAG
collections within the mygenai system.


# RAGIT Web Application

### Overview

RAGIT is a web application that used a vector database to allow for a RAG 
based chat-bot.  

### Ragit Configuration File

Ragit is back-end agnostic in the sense that it can use any RAG collection 
that is available in the backend. We can customize the vector db by changing
the `config.yaml` under the same directory as the ragit application.

An example of a configuration yaml file is the following:

```yaml
web_service:
  name: ragit
  port: <PORT-NUMBER>

domain:
  name: <collection name goes here>
```

#### web_service
* **name**: The name of the web service.
    * Type: string
* **port**: The port number for the web service.
    * Type: integer

#### domain
* **title**: The title of the website.
    * Type: string
* **description**: A description of the website.
    * Type: string
* **name**: The name of the RAG collection.
    * Type: string


### Notes
* All fields within `web_service` and `domain` are required.
* The `port` number should be replaced with the desired port for the web service.

### Running the web-server
Having the proper configuration yaml file to point to the desired RAG collection
we can now start the ragit server as follows:

```bash
cd ragit/services/ragit
python3 app.py
```

you should now be able to access it by using this URL from your browser:

```url
localhost:<port>
```

