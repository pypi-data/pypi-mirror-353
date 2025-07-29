def genai_prgm(n):
    if n==1:
        print("""
import gensim.downloader as api
# Load pre-trained model
model = api.load("glove-wiki-gigaword-50")
# Example words
word1 = "king"
word2 = "man"
word3 = "woman"
# Performing vector arithmetic
result_vector = model[word1]- model[word2] + model[word3]
predicted_word = model.most_similar([result_vector], topn=2)
print(f"Result of '{word1}- {word2} + {word3}' is: {predicted_word[1][0]}")
""")

    if n==2:
        print("""
import gensim.downloader as api
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import numpy as np
# Load pre-trained Word2Vec model
model = api.load("glove-wiki-gigaword-50")
# Select 10 words from a specific domain (e.g., technology)
words = ["computer", "internet", "software", "hardware", "disk", "robot", "data",
"network", "cloud", "algorithm"]
# Get word vectors and convert to a 2D NumPy array
word_vectors = np.array([model[word] for word in words])
# Reduce dimensions using PCA
pca = PCA(n_components=2)
reduced_vectors = pca.fit_transform(word_vectors)
# Plot PCA visualization
plt.figure(figsize=(8, 6))
for i, word in enumerate(words):
    plt.scatter(reduced_vectors[i, 0], reduced_vectors[i, 1])
    plt.annotate(word, (reduced_vectors[i, 0], reduced_vectors[i, 1]))
plt.title("PCA Visualization of Word Embeddings (Technology Domain)")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.show()
input_word = "computer" # You can change this to any word in your list
similar_words = model.most_similar(input_word, topn=5)
print(f"Words similar to '{input_word}':", similar_words)
 """)

    if n==3:
        print("""import gensim
 from gensim.models import Word2Vec
 import nltk
 fromnltk.tokenizeimportword_tokenize

 corpus=[
 Any 5 sentences of ur choice
 ]
 #Tokenizesentences
 tokenized_corpus=[word_tokenize(sentence.lower())for sentence in corpus]
 
 model=Word2Vec(sentences=tokenized_corpus,vector_size=100,window=3,min_count=1,
 workers=4,sg=1)
 #Savethemodel
 model.save("medical_word2vec.model")
 
 similar_words=model.wv.most_similar("doctor",topn=5)
 #Displayresults
 print("Top 5 words similar to 'doctor':")
 print(similar_words)""")

    if n==4:
        print("""from transformers import pipeline
 import gensim.downloader as api

 glove_model=api.load("glove-wiki-gigaword-50")
 word="technology"
 similar_words=model.most_similar(word,topn=5)
 print(f"Similar wordsto'{word}':{similar_words}")
 #Loadatextgenerationpipeline
 generator=pipeline("text-generation",model="gpt2")
 #Functiontogeneratetext
 def generate_response(prompt,max_length=100):
     response=generator(prompt,max_length=max_length,num_return_sequences=1)
     return response[0]['generated_text']
 #Originalprompt
 original_prompt="Explaintheimpactoftechnologyonsociety."
 original_response=generate_response(original_prompt)
 #Enrichedprompt
 enriched_prompt="Explain the impact of technology,innovation,science,engineering,anddigital
 advancementsonsociety."
 enriched_response=generate_response(enriched_prompt)
 #Printresponses
 print("OriginalPromptResponse:")
 print(original_response)
 print("\nEnrichedPromptResponse:")
 print(enriched_response)
 """)

    if n==5:
        print("""import gensim.downloader as api
 # Load GloVe embeddings directly
 model = api.load("glove-wiki-gigaword-50")
 # Function to construct a short paragraph
 def construct_paragraph(seed_word, similar_words):
 # Create a simple template-based paragraph
     paragraph = (
     f"In the spirit of {seed_word}, one might embark on an unforgettable {similar_words[0][0]} "
     f"to distant lands. Every {similar_words[1][0]} brings new challenges and opportunities for
     {similar_words[2][0]}. "
     f"Through perseverance and courage, the {similar_words[3][0]} becomes a tale of triumph, much
     like an {similar_words[4][0]}."
     )
     return paragraph
 # Generate a paragraph for "adventure"
 seed_word = "adventure"
 similar_words = model.most_similar(seed_word, topn=5)
 # Construct a paragraph
 paragraph = construct_paragraph(seed_word, similar_words)
 print(paragraph)
 """)

    if n==6:
        print("""from transformers import pipeline
 # Load the sentiment analysis pipeline
 sentiment_pipeline = pipeline("sentiment-analysis")
 # Example sentences
 sentences = [
 "I love this product! It works perfectly.",
 "This is the worst experience I've ever had.",
 "The weather is nice today.",
 "I feel so frustrated with this service."
 ]
 # Analyze sentiment for each sentence
 results = sentiment_pipeline(sentences)
 # Print the results
 for sentence, result in zip(sentences, results):
     print(f"Sentence: {sentence}")
     print(f"Sentiment: {result['label']}, Confidence:{result['score']:.4f}")
     print()
 """)

    if n==7:
        print("""from transformers import pipeline
 # Load the T5 summarization pipeline
 summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")
 # Example passage
 passage = "Machine learning is a subset of artificial intelligence that focuses on training algorithms
 to make predictions. It is widely used in industries like healthcare, finance, and retail."
 # Generate the summary
 summary = summarizer(passage, max_length=30, min_length=10, do_sample=False)
 # Print the summarized text
 print("Summary:")
 print(summary[0]['summary_text'])
 """)

    if n==8:
        print("""importos
 from cohere import Client
 from langchain.prompts import PromptTemplate
 #Step1:SetCohereAPIKey
 os.environ["COHERE_API_KEY"]="RI01YSU6DETF3yEF0MTwwbOOjIsVWRedqTpN627v"
 co=Client(os.getenv("COHERE_API_KEY"))
 #Step2:LoadTextDocument(Option1:LocalFile)
 with open("text.txt","r",encoding="utf-8")as file:
    text_document=file.read()

 template=""
 You are an expert summarizer.Summarize the following text in a concise manner:
 Text:{text}
 Summary:
 ""
 prompt_template=PromptTemplate(input_variables=["text"],template=template)
 formatted_prompt=prompt_template.format(text=text_document)
 #Step4:SendPrompttoCohereAPI
 response=co.generate(
 model="command",
 prompt=formatted_prompt,
 max_tokens=50
 )
 #Step5:DisplayOutput
 print("Summary:")
 print(response.generations[0].text.strip())""")

    if n==9:
        print("""from typing import Optional
 from pydantic import BaseModel,Field,ValidationError
 import wikipedia
 #Step1:DefinethePydanticSchemafortheOutput
 class InstitutionDetails(BaseModel):
     name:str=Field(description="Nameoftheinstitution")
     founder:Optional[str]=Field(description="Founderoftheinstitution")
     founding_year:Optional[int]=Field(description="Yeartheinstitutionwas
     founded")
     branches:Optional[int]=Field(description="Numberofbranchesofthe
     institution")
     employees:Optional[int]=Field(description="Numberofemployeesinthe
     institution")
     summary:Optional[str]=Field(description="Summaryoftheinstitution")
 #Step2:FetchInstitutionDetailsfromWikipedia
 def fetch_institution_details(institution_name:str)->InstitutionDetails:
     try:
         
         page=wikipedia.page(institution_name)
         summary=wikipedia.summary(institution_name,sentences=3)
         
         details={
         "name":institution_name,
         "founder":None, #YoucanuseNLPorregextoextractthisfromthepage
         content
         "founding_year":None, #Extractfromthepagecontent
         "branches":None, #Extractfromthepagecontent
         "employees":None, #Extractfromthepagecontent
         "summary":summary,
         }
         #ParsethedetailsintothePydanticschema
         returnInstitutionDetails(**details)
     except wikipedia.exceptions.PageError:
        return InstitutionDetails(name=institution_name,summary="NoWikipediapage
     found.")
     except wikipedia.exceptions.DisambiguationError:
        return InstitutionDetails(name=institution_name,summary="Multiple matches found.Please specify.")
    except ValidationError as e:
         print(f"Validation Error: {e}")
         return InstitutionDetails(name=institution_name, summary="Error parsing
         details.")
 # Step 3: Invoke the Chain and Fetch Results
 if __name__ == "__main__":
     institution_name = input("Enter the institution name: ")
     details = fetch_institution_details(institution_name)
     print(details)
     """)

    if n==10:
        print("""import streamlit as st
 from langchain_community.document_loaders import PDFPlumberLoader
 from langchain_text_splitters import RecursiveCharacterTextSplitter
 from langchain_core.vectorstores import InMemoryVectorStore
 from langchain_ollama import OllamaEmbeddings
 from langchain_core.prompts import ChatPromptTemplate
 from langchain_ollama.llms import OllamaLLM
 from langchain.chains import ConversationalRetrievalChain
 template = ""
 You are an assistant for question-answering tasks. Use the following pieces of
 retrieved context to answer the question. If you don't know the answer, just say that
 you don't know. Use three sentences maximum and keep the answer concise.
 Question: {question}
 Context: {context}
 Answer:
 ""

 file_path = "ipc.pdf"

 loader = PDFPlumberLoader(file_path)
 documents = loader.load()

 text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
 text_chunks = text_splitter.split_documents(documents)
 embeddings = OllamaEmbeddings(model="deepseek-r1:1.5b")
 vector_store = InMemoryVectorStore(embeddings)
 model=OllamaLLM(model="deepseek-r1:1.5b")
 retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k":
 5})
 chatbot=ConversationalRetrievalChain.from_llm(model,retriever)
 # UserChatLoop
 print(" IPC Chatbot Initialized!Ask about the IndianPenalCode.")
 chat_history=[]
 whileTrue:
     query=input("\n You:")
     if query.lower()in["exit","quit"]:
         print(" Chatbot:Goodbye!")
         break
     response=chatbot({"question":query,"chat_history":chat_history})
     chat_history.append((query,response["answer"]))
     print(f" Chatbot:{response['answer']}")
 """)