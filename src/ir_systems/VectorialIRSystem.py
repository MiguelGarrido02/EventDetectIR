import re 
import math 
import time

class RankedRetrieval:
    def __init__(self):
        # Initialize index, document frequency, weights, idf, and max_doc_id attributes
        self.index = {}
        self.doc_frequency = {}
        self.weights = {}
        self.idf = []
        self.max_doc_id = 0

    def tokenize(self, text):
        """
        Tokenize the input text using regular expressions.

        Args:
            text (str): The input text to be tokenized.

        Returns:
            list: A list of tokens extracted from the text.
        """
        # Define a regular expression pattern to match words (alphanumeric sequences)
        pattern = r'\b\w+\b'
        # Use the findall() function from the re module to extract all matches of the pattern
        tokens = re.findall(pattern, text.lower())
        return tokens

    def get_tf(self, title, text, doc_id):
        """
        Calculate term frequency (TF) for each term in the document and update the inverted index and document frequency.

        Args:
            title (str): The title of the document.
            text (str): The text content of the document.
            doc_id (int): The unique identifier of the document.
        """
        # Tokenize the title and text
        title_tokens = self.tokenize(title)
        text_tokens = self.tokenize(text)

        # Add token-docID pairs to the index for title and text
        for token in title_tokens + text_tokens:
            if token not in self.index:
                self.index[token] = []
            self.index[token].append(doc_id)
    
        # Count document frequency for each term in title and text
        all_tokens = title_tokens + text_tokens

        # Count term frequencies
        term_frequencies = {}
        for token in all_tokens:
            term_frequencies[token] = term_frequencies.get(token, 0) + 1

        # Find the frequency of the most common term
        max_frequency = max(term_frequencies.values())

        # Normalize term frequencies
        for token, frequency in term_frequencies.items():
            term_frequencies[token] = frequency / max_frequency

        # Update self.doc_frequency with normalized term frequencies
        for token, frequency in term_frequencies.items():
            if token not in self.doc_frequency:
                self.doc_frequency[token] = [(doc_id, frequency)]  # Initialize with a list containing (doc_id, normalized frequency)
            else:
                found = False
                for i, (existing_doc_id, _) in enumerate(self.doc_frequency[token]):
                    if existing_doc_id == doc_id:
                        self.doc_frequency[token][i] = (existing_doc_id, frequency)  # Update frequency
                        found = True
                        break
                if not found:
                    self.doc_frequency[token].append((doc_id, frequency))  # If document ID not found, add it with frequency

    def get_idf(self):
        """
        Calculate inverse document frequency (IDF) for each term in the document.
        """
        for term, contents in self.doc_frequency.items():
            document_count = len(contents)  # Number of different documents containing that term
            idf = math.log2(self.max_doc_id / document_count)
            for doc_id, frequency in contents:
                weight = frequency * idf
                if term not in self.weights:
                    self.weights[term] = [(doc_id, weight)]
                else:
                    self.weights[term].append((doc_id, weight))

    def tokenize_query(self, query):
        """
        Tokenize the input query.

        Args:
            query (str): The query string.

        Returns:
            list: A list of tokens extracted from the query.
        """
        # Tokenize the query
        return query.lower().split()

    def get_query_vector(self, query_tokens):
        """
        Generate the TF-IDF weighted vector for the query.

        Args:
            query_tokens (list): A list of tokens from the query.

        Returns:
            dict: A dictionary representing the TF-IDF weighted vector for the query.
        """
        query_vector = {}
        # Calculate TF for each term in the query
        term_frequencies = {}
        for token in query_tokens:
            term_frequencies[token] = term_frequencies.get(token, 0) + 1

        # Calculate IDF for each term in the query
        for token, tf in term_frequencies.items():
            document_count = len(self.doc_frequency.get(token, []))  # Number of documents containing the term
            try: 
                idf = math.log2(self.max_doc_id / (document_count))  
            except:
                idf = math.log2(self.max_doc_id / (document_count + 1)) # Add 1 to avoid division by zero, smoothing techinque
            query_vector[token] = tf * idf

        return query_vector

    def compute_cosine_similarity(self, query_vector, document_vectors):
        """
        Compute the cosine similarity between the query vector and document vectors.

        Args:
            query_vector (dict): The TF-IDF weighted vector for the query.
            document_vectors (dict): A dictionary containing TF-IDF weighted vectors for each document.

        Returns:
            dict: A dictionary containing cosine similarity scores for each document.
        """
        similarity_scores = {}
    
        # Compute numerator (dot product) and denominator (magnitudes) for each document
        for term in query_vector:
            query_weight = query_vector[term]

            
            # Iterate over the documents containing the term
            for doc_id, doc_weight in document_vectors.get(term, []):
                if doc_id not in similarity_scores:
                    similarity_scores[doc_id] = {'numerator': 0.0, 'doc_magnitude': 0.0}
            
                # Accumulate the dot product
                similarity_scores[doc_id]['numerator'] += query_weight * doc_weight
                # Accumulate the sum of squares of document weights
                similarity_scores[doc_id]['doc_magnitude'] += doc_weight ** 2
    
        # Compute the denominator (magnitude) for each document
        for doc_id in similarity_scores:
            similarity_scores[doc_id]['doc_magnitude'] = math.sqrt(similarity_scores[doc_id]['doc_magnitude'])
    
        # Normalize similarity scores by document magnitudes
        for doc_id in similarity_scores:
            # Check if magnitude is non-zero before performing division
            if similarity_scores[doc_id]['doc_magnitude'] != 0:
                similarity_scores[doc_id] = similarity_scores[doc_id]['numerator'] / (math.sqrt(sum(query_weight ** 2 for query_weight in query_vector.values())) * similarity_scores[doc_id]['doc_magnitude'])
            else:
                # If magnitude is zero, set similarity score to zero
                similarity_scores[doc_id] = 0.0

        return similarity_scores


# Start time
start_time = time.time()

# Initialize an empty list to store documents
documents = []

# Initialize a RankedRetrieval object
retrieval = RankedRetrieval()
#file_path = r"C:\Users\34606\source\repos\RetrievingData\TheHerald_articles_all_sections_news.txt"
#file_path = r"C:\Users\34606\source\repos\RetrievingData\test_database.txt"
#file_path = r"C:\Users\34606\source\repos\RetrievingData\news_database.txt"
file_path = r"C:\Users\34606\source\repos\RetrievingData\expanded_database.txt"


# Read documents from a file
with open(file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()
    num_lines = len(lines)
    i = 0
    doc_id = 0
    url = ""
    while i < num_lines:
        # Find the delimiter "================="
        while i < num_lines and lines[i].strip() != "==========================================":
            i += 1
        i += 1  # Skip the delimiter line
        
        # Check if there are more lines to process
        if i < num_lines:
            # Extract document components until the next delimiter
            title = lines[i].strip()
            i += 1
            text = ""
            while i < num_lines and lines[i].strip() != "==========================================":
                if lines[i+1].strip() == "==========================================":
                    url = lines[i].strip()
                    #print(lines[i])
                else: 
                    text += lines[i].strip() + " "
                i += 1
            
            # Add document components to the documents list
            documents.append((title, text, url))
            # Add document to the inverted index
            retrieval.get_tf(title, text, doc_id)
            doc_id += 1

    retrieval.max_doc_id = doc_id # store number of documents, note that the number of documents is the id of the last document + 1, which is done above
    retrieval.get_idf()

    # End time
    end_time = time.time()

    execution_time = end_time - start_time

    print("Pre-processing time:", execution_time, "seconds")



    # Input query from user
    query = input("Enter your search query: ")
       # Start time
    retrieval_start_time = time.time()


    # Tokenize the query
    query_tokens = retrieval.tokenize_query(query)

    # Get the TF-IDF weighted vector for the query
    query_vector = retrieval.get_query_vector(query_tokens)

    # Compute cosine similarity between the query vector and document vectors
    results = retrieval.compute_cosine_similarity(query_vector, retrieval.weights)

    # Sort the dictionary items based on values (similarity scores)
    results = sorted(results.items(), key=lambda x: x[1], reverse=True)

    retrieval_end_time = time.time()
    retrieval_time = retrieval_end_time - retrieval_start_time

    print("Retrieval time:", retrieval_time, "seconds")


    print("Ranking: ")
    i = 1
    for element in results:
        print(i, ": ", documents[element[0]][0]) #element[0] = docID
        print("URL: ", documents[element[0]][2])
        i += 1
            # End time

