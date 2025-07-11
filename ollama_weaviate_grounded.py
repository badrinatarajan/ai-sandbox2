# Weaviate local DB store with ollama using mxbai-embed-large embedding and deepseek-r1 as the generative model
import weaviate
import weaviate.classes as wvc
import ollama
import os
import sys
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat

COLLECTION_NAME = "VideoCollectionSDWAN2md"

LINK="https://www.youtube.com/watch?v=dq-qA4vEpN0" #what is SDWAN



def connect_and_get_client():
    client = weaviate.connect_to_local() # Connect to our local database
    return client

def load_doc(link):
    loader = YoutubeLoader.from_youtube_url(
    link,
    add_video_info=False,
    transcript_format=TranscriptFormat.CHUNKS,
    chunk_size_seconds=60,
    )
    l = loader.load_and_split()
    return (l)

# Create a new data collection
def create_collection(client):
    if client.collections.exists(COLLECTION_NAME):
        collection = client.collections.get(COLLECTION_NAME)
        print(f'Using existing collection...{collection}')
    else:    
        try :
            print('Creating collection....')
            collection = client.collections.create(
                name = COLLECTION_NAME, # Name of the data collection
                properties=[
                    wvc.config.Property(
                        name="text",
                        data_type=wvc.config.DataType.TEXT
                    ),
                    wvc.config.Property(
                        name="source",
                        data_type=wvc.config.DataType.TEXT
                    ),
                    wvc.config.Property(
                        name="start_seconds",
                        data_type=wvc.config.DataType.INT
                    ),
                    wvc.config.Property(
                        name="start_timestamp",
                        data_type=wvc.config.DataType.TEXT
                    ),
                ]
            )
        except  weaviate.exceptions.WeaviateBaseError as e:
            return {
            "status": "error",
            "error_message": str(e),
            "message": f"Failed to create collection: {str(e)}"
            }   
    print(f'returning collection {collection}')
    return {
                "status": "success",
                "collection": collection,
                "message": f"Successfully created or retrieved collection {COLLECTION_NAME}"
            } 
    
def close_connection(client):
    client.close()    

def generate_embeddings_and_add_to_collection(docs, collection):

    print(f'Importing {len(docs)} chunk objects')
    batch_err = False
    with collection.batch.fixed_size(batch_size=200) as batch:
            for item in docs:
                # Generate embeddings
                pc = item.page_content
                md = item.metadata
                source = md.get('source','Not available')
                start_seconds = md.get('start_seconds', 0)
                start_timestamp = md.get('start_timestamp', 'Not available')
                #print(f'Adding object with source {source} start_seconds {start_seconds} start_timestamp {start_timestamp}')
                response = ollama.embeddings(model ="mxbai-embed-large",
                                                prompt = pc)

                # Add data object with text and embedding
                batch.add_object(
                        properties = {  "text" : pc, 
                                        "source":source,
                                        "start_seconds":start_seconds, 
                                        "start_timestamp":start_timestamp},
                        vector = response["embedding"],
                    )
                if batch.number_errors > 10:
                        batch_err= True
                        print("Batch import stopped due to excessive errors.")
                        break
    if batch_err:
        return {
            "status": "error",
            "message": "Failed to add objects to collection"
            } 
    return {
        "status":"success",
        "message":f"Successfully generated embeddings for collection {COLLECTION_NAME}"
    }
    
def retrieve_doc(collection, prompt):
    
    # Generate an embedding for the prompt and retrieve the most relevant doc
    response = ollama.embeddings(
    model = "mxbai-embed-large",
    prompt = prompt,
    )
    
    results = collection.query.near_vector(near_vector = response["embedding"],
                                        limit = 10, distance=0.7)

    #print(f'results [{results.objects}], num of objects [{len(results.objects)}]')

    data = ''
    metadata = []
    for idx, item in enumerate(results.objects):
        source = item.properties.get('source')
        start_timestamp = item.properties.get('start_timestamp')
        start_seconds = item.properties.get('start_seconds')
        # print(f"idx {idx} text {item.properties['text']},"
        #        f"source {source}, "
        #        f"start_timestamp {start_timestamp}," 
        #        f"start_seconds {start_seconds} \n")
        data = data + ' '+ str(item.properties['text'])
        metadata.append((source, start_timestamp, start_seconds))
    if len(results.objects):
        return data, metadata

    return None

def generate_content(prompt_template):
    
    output = ollama.generate(
      model = "deepseek-r1",
      prompt = prompt_template,
    )

    #print(output['response'])
    return output['response']

def check_status(val, c):
    if val.get('status') == 'error':
        close_connection(c)
        sys.exit()

def get_status(status, msg):
     return {
            "status": status,
            "message": str(msg)
        }

def must_init():
    if  COLLECTION_NAME == 'None':
        return get_status("error", "failed to get COLLECTION_NAME") 
   

    return get_status("success", "All env vars present")                


def main():
    st = must_init()
    if st.get('status') != 'success':
        print(f'Initialization error, err = {st.get("message")}')
        sys.exit(0)

    c= connect_and_get_client()
    rc = create_collection(c)
    if rc.get('status') != 'success':
        print(f'DB error, err = {rc.get("message")}')
        sys.exit(0)
    print(f'rc {rc}')
    collection = rc.get('collection')
    if collection == None:
        print('DB error, collection not available')
        sys.exit(0)

    num_objects = len(collection)
    print(f'Found {num_objects} objects inserted in the collection')
    if num_objects == 0 :
        docs = load_doc(LINK)
        rc = generate_embeddings_and_add_to_collection(docs, collection)
        if rc.get('status') != 'success':
            print(f'Embeddings error = {st.get("message")}')
            sys.exit(0)

    prompt =  "what is SDWAN"   
    context_data , metadata = retrieve_doc(collection, prompt)
    #print(f'Retrieved data {context_data}')

    if context_data == None:
        print('Could not get enough context from the video')

    else:        
        #Generate content using retrieved data:
        prompt ="Compare advantages of SDWAN over MPLS"
        prompt_template = f"Using this data: \"{context_data}\". Respond to this prompt: \"{prompt}\""
        print(f'Generating response for prompt {prompt_template}')
        response= generate_content(prompt_template)
        print(f'Response: {response}\n')
        print(f'Sources: {metadata}\n')

    close_connection(c)

if __name__== '__main__':
    main()
