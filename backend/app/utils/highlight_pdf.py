import fitz  # PyMuPDF
import spacy

# Load the Dutch language model
nlp = spacy.load("nl_core_news_sm")

def identify_important_parts(input_pdf):
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text("text")
    nlp_doc = nlp(text)
    important_parts = [ent.text for ent in nlp_doc.ents if ent.label_ in ["ORG", "GPE", "PERSON"]]
    return important_parts

def highlight_important_parts(input_pdf, output_pdf, important_parts):
    doc = fitz.open(input_pdf)
    for page in doc:
        for part in important_parts:
            highlights = page.search_for(part)
            for rect in highlights:
                page.add_highlight_annot(rect)
    doc.save(output_pdf)