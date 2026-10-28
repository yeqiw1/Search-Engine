# Search Engine and Document Retrieval System

A Python-based search engine that indexes and retrieves relevant documents based on user queries. The system uses information retrieval techniques such as inverted indexing, text preprocessing, and TF-IDF scoring to efficiently search through large document collections and rank relevant results.

## Features

- **Document Indexing:** Builds an inverted index to map terms to the documents containing them, enabling efficient document retrieval.
- **Text Preprocessing:** Performs tokenization, normalization, and stemming to improve search consistency and accuracy.
- **TF-IDF Scoring:** Uses term frequency and inverse document frequency to measure term importance and support relevance-based ranking.
- **Positional Indexing:** Tracks term positions within documents to support more detailed search operations.
- **Duplicate Detection:** Identifies duplicate and near-duplicate documents to reduce redundant search results.
- **Query Processing:** Processes user search queries and retrieves relevant documents based on indexed terms.
- **Search Interface:** Provides a user interface for submitting queries and viewing search results.

## Technologies Used

- **Language:** Python
- **Core Concepts:** Information Retrieval, Data Structures, Algorithms
- **Indexing:** Inverted Index, Positional Index
- **Ranking:** TF-IDF
- **Text Processing:** Tokenization, Normalization, Stemming
- **Data Processing:** Document Parsing and Duplicate Detection

## How It Works

1. **Document Processing:** Reads documents and extracts searchable text.
2. **Text Preprocessing:** Tokenizes, normalizes, and stems the extracted text.
3. **Index Construction:** Creates an inverted index containing document references and term information.
4. **Query Processing:** Applies text preprocessing to user queries to match indexed terms.
5. **Document Retrieval:** Identifies documents containing relevant query terms.
6. **Result Ranking:** Uses TF-IDF-based scoring to evaluate document relevance and rank search results.
7. **Result Display:** Presents matching documents through the search interface.

## Getting Started

### Prerequisites

- Python 3
- Required Python dependencies specified by the project

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yeqiw1/Search-Engine.git
   ```

2. Navigate to the project directory:

   ```bash
   cd Search-Engine
   ```

3. Install any required dependencies according to the project's source files or dependency configuration.

4. Build the search index using the project's indexing scripts.

5. Launch the search interface and enter a query to retrieve relevant documents.

## Project Highlights

This project demonstrates the implementation of fundamental information retrieval algorithms and data structures to build a functional search engine.

Key concepts include:

- Efficient document indexing and retrieval
- Algorithm design and optimization
- Natural language text preprocessing
- Information retrieval and relevance ranking
- Duplicate and near-duplicate document detection
- Modular Python application development

## Author

**Katy Wu**

B.S. Software Engineering | University of California, Irvine

[GitHub](https://github.com/yeqiw1) | [Project Repository](https://github.com/yeqiw1/Search-Engine)
