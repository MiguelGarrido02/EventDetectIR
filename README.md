# IR Evaluation on Social Event Detection

## Project Overview
This project evaluates Information Retrieval (IR) models for detecting social events from news articles. 
Data is collected from two South Korean newspapers  (*The Korea Herald* and *The Korea Times*) using web scraping techniques. Then two IR models are used: Boolean Information Retrieval System and a Vector Space Model (TF-IDF).

## Features
- **Web Scraping**:
  - `scraper_korea_herald.py`: Scrapes articles from *The Korea Herald*.
  - `scraper_korea_times.py`: Scrapes articles from *The Korea Times*.
  
- **Information Retrieval Systems**:
  - `boolean_ir_system.py`: Boolean retrieval system that uses Boolean operators (AND, OR, NOT) to search for articles.
  - `vector_space_ir_system.py`: Vector Space Model IR system that ranks articles by their relevance to user queries using cosine similarity and TF-IDF weighting.

## How to Use
1. **Scraping News Articles**:
   - Run the scraping scripts to collect news articles:
     ```bash
     python src/scraper_korea_herald.py
     python src/scraper_korea_times.py
     ```
   - The scrapers will collect the articles and save them as text files in the `data/` folder.

2. **Information Retrieval**:
   - Use the Boolean IR system:
     ```bash
     python src/boolean_ir_system.py
     ```
   - Use the Vector Space Model (TF-IDF) system:
     ```bash
     python src/vector_space_ir_system.py
     ```

3. **Evaluate Results**:
   - Both systems will return relevant articles based on your queries. You can then analyze the performance in terms of precision, recall, and time efficiency.

## Documentation
For a detailed explanation of the project, please refer to the [Project Documentation (PDF)](./docs/IR%20System.pdf).


