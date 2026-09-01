from pypdf import PdfReader
import io

def read_doc(file_object):
    text = ""
    content = file_object.file.read()
    doc = PdfReader(io.BytesIO(content))

    for page in doc.pages:
        text += page.extract_text() 

    return {"file" : file_object.filename, "text" : text}

