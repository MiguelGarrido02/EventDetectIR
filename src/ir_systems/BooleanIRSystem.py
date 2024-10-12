import re
import time

class InvertedIndex:
    def __init__(self):
        # Initialize the index and document frequency attributes
        self.index = {}

    def tokenize(self, text):
        """
        Tokenize the input text.

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

    def add_document(self, title, text, doc_id):
        """
        Add document to the inverted index.

        Args:
            title (str): The title of the document.
            text (str): The text content of the document.
            doc_id (int): The unique identifier of the document.
        """
        # Tokenize the title and text using regular expressions
        title_tokens = self.tokenize(title)
        text_tokens = self.tokenize(text)

        # Add token-docID pairs to the index for title and text
        for token in title_tokens + text_tokens:
            if token not in self.index:
                self.index[token] = []
            self.index[token].append(doc_id)

    def search(self, query):
        """
        Search for documents based on a query.

        Args:
            query (str): The search query.

        Returns:
            list: A list of document IDs that match the query.
        """
        query = query.lower()
        query = query.split()
        results = set()
        skip_word = 0
        for word in range(len(query)):

            if skip_word != 0:
                skip_word -= 1
                continue

            if query[word] not in ["and", "or", "not"]:
                results = set(self.index.get(query[word], []))

            elif query[word] == "not" and word == 0:  # if not is the first word in the query
                # Get all 
                results = set([term for term in self.index.get[term]])
                # Exclude the posting list associated with the term
                results.difference_update(self.index.get(query[word+1], []))
                skip_word = 1

            elif query[word] == "and":
                if query[word+1] == "not":
                    # Exclude the posting list associated with the term
                    results.difference_update(self.index.get(query[word+2], [])) 
                    skip_word = 2  # we will skip 2 words, "and" & "not"
                else:
                    results.intersection_update(self.index.get(query[word+1], []))
                    skip_word = 1  # we will skip one word, the "and"
            elif query[word] == "or":
                if query[word+1] == "not":
                    # Add posts that exclude the posting list associated with the term
                    # Get all terms from the inverted index that are not equal to query[word]
                    print(query[word+2])
                    print(self.index.keys())
                    terms_not_query_word = [term for term in self.index.keys() if term != query[word+2]]
                    # Iterate through the terms not containing query[word]
                    for term in terms_not_query_word:
                        # Update results with documents containing the term
                        results.update(self.index.get(term, []))
                        skip_word = 2  # we will skip 2 words, "or" & "not"
                else:
                    print(query[word])
                    results.update(self.index.get(query[word+1], []))
                    skip_word = 1  # we will skip one word, the "or"

        return(list(results))


# Initialize an empty list to store documents
documents = []

# Initialize an InvertedIndex object
index = InvertedIndex()
file_path = r"C:\Users\34606\source\repos\RetrievingData\news_database.txt"
#file_path = r"C:\Users\34606\source\repos\RetrievingData\test_database.txt"


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
               else: 
                    text += lines[i].strip() + " "
               i += 1

            # Add document components to the documents list
            documents.append((title, text, url))
            # Add document to the inverted index
            index.add_document(title, text, doc_id)
            doc_id += 1

# Display the extracted documents
#for title, text, url in documents:
#    print("Title:", title)
#    print()  # Print an empty line for better readability

# Perform a search
query = input("Enter your search query: ")
# Call section_scraper function with the URL and output file names
start_time = time.time()
results = index.search(query)
results = list(set(results))  # Eliminate repeated results

# Display search results
if results:
    print("Matching documents:")
    for result in results:
        print(documents[result][0]) # Print the title of the matching document
        print("URL :", documents[result][2])
else:
    print("No matching documents found.")
print("--- %s seconds ---" % (time.time() - start_time))