from pypdf import PdfReader

def read_doc(file_object):
    text = ""
    doc = PdfReader(file_object.filename)

    for page in doc.pages:
        text += page.extract_text()

    return {"file" : file_object.filename, "text" : text}

