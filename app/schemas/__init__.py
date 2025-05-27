# Pydantic schemas for API validation 

# Export all schemas
from .user import *
from .ebook import *
from .collection import *
from .share import *
from .reading import *

# Resolve forward references
from . import ebook, collection, share, reading

# Update forward references for all models that use them
ebook.EbookWithAuthor.model_rebuild()
collection.CollectionWithAuthor.model_rebuild()
collection.CollectionWithEbooks.model_rebuild()
share.ShareLinkWithContent.model_rebuild()
reading.ReadingProgressWithEbook.model_rebuild() 