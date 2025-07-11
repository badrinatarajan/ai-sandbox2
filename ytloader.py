from langchain_community.document_loaders.youtube import TranscriptFormat
from langchain_community.document_loaders import YoutubeLoader

loader = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=dq-qA4vEpN0",
    #"https://www.youtube.com/watch?v=ORMx45xqWkA",
    #"https://www.youtube.com/watch?v=TKCMw0utiak",
    #"https://www.youtube.com/watch?v=tKjDzfaYvNE",
    add_video_info=False,
    
    transcript_format=TranscriptFormat.CHUNKS,
    chunk_size_seconds=30,
)
l = loader.load_and_split()
for item in l:
    print(f' content: {item.page_content} metadata: {item.metadata}')
    print("\n\n")
#print(loader.load_and_split())
#print("\n\n".join(map(repr, loader.load())))
print ("\n\n")
