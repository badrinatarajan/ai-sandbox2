# ai-sandbox2  
Building a Private RAG pipeline for YouTube content - using Ollama and Deepseek

To setup and run the code:
1. python3 -m venv .venv
2. source .venv/bin/activate
3. pip3 install -U weaviate-client
4. pip3 install -U ollama
5. pip3 install langchain
6. pip3 install langchain_community
7. python3 ./ollama_weaviate_grounded.py

To download the deepseek model:
1. Visit the Ollama download page and download for your OS 
Instructions for MacOS:
https://ollama.com/download/mac
Click on the Download for macOS button.
Once the download is complete, locate the .zip file in your ~/Downloads folder, double click the .zip and extract contents.

2. Once downloaded open a Terminal and pull the needed model:
$ ollama pull deepseek-r1:latest

Reference:
https://badrinatarajan.substack.com/p/from-videos-to-insight-rag-with-open
