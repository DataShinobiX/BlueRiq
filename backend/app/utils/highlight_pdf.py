import fitz  # PyMuPDF
from transformers import pipeline
import json

nlp = pipeline("fill-mask", model="GroNLP/bert-base-dutch-cased") 

def load_domain_rules(domain):
    with open('path/to/domain_rules.json') as f:
        data = json.load(f)
    return data['domains'].get(domain, {})

def identify_important_parts(input_pdf, domain):
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text("text")
    
    domain_rules = load_domain_rules(domain)
    nlp_doc = nlp(text)
    important_parts = [result['word'] for result in nlp_doc if result['entity'] in domain_rules.get('rules', [])]
    return important_parts

def highlight_important_parts(input_pdf, output_pdf, important_parts):
    doc = fitz.open(input_pdf)
    for page in doc:
        for part in important_parts:
            highlights = page.search_for(part)
            for rect in highlights:
                page.add_highlight_annot(rect)
    doc.save(output_pdf)