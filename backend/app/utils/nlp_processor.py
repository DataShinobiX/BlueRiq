#Trying to extract rules and entities from a policy document using spacy
#test comment
import fitz  # PyMuPDF
import spacy
import re
import logging
import os
from collections import defaultdict
from pdfminer.high_level import extract_text

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_file_path = os.path.join(log_dir, "nlp_debug.log")
fh = logging.FileHandler(log_file_path)
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

logger.addHandler(fh)

try:
    nlp = spacy.load("nl_core_news_lg")
except:
    nlp = spacy.load("nl_core_news_sm")


def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    logger.debug("Extracted text from %s: %s", pdf_path, text)
    return text


def categorize_sentences(text):
    rules = []
    definitions = []
    exceptions = []
    external_sources = []
    entities = defaultdict(set)

    doc = nlp(text)
    sentences = list(doc.sents)
    
    for i in range(len(sentences)):
        current_sent = sentences[i].text.strip()
        next_sent = sentences[i + 1].text.strip() if i + 1 < len(sentences) else ""
        
        # Check for if-then pattern within single sentence
        if re.search(r"\b(is|als|indien|wanneer|mits|in het geval dat)\b.*\b(dan|wordt|is|geldt|moet|dient|kan|mag)\b", current_sent, re.IGNORECASE):
            rules.append(current_sent)
        
        # Check for if-then pattern across two sentences
        elif re.search(r"\b(is|als|indien|wanneer|mits|in het geval dat)\b", current_sent, re.IGNORECASE) and \
             re.search(r"\b(dan|wordt|is|geldt|moet|dient|kan|mag)\b", next_sent, re.IGNORECASE):
            rules.append(f"{current_sent} {next_sent}")
        
        # Rule detection
        elif re.search(r"\b(kan|mag|moet|in het geval dat|dient|geldend van|hebben recht op)\b", current_sent, re.IGNORECASE):
            rules.append(current_sent)

        if re.search(r"\b(is|het geval|=)\b", current_sent, re.IGNORECASE):
            definitions.append(current_sent)

        if re.search(r"\b(indien|alsnog|niet|geval|maar)\b", current_sent, re.IGNORECASE):
            exceptions.append(current_sent)

        if re.search(r"\b(artikel|wetvoorstel|wet)\b", current_sent, re.IGNORECASE):
            external_sources.append(current_sent)

        # Named Entity Recognition
        for ent in sentences[i].ents:
            entities[ent.label_].add(ent.text)

    return rules, {label: list(vals) for label, vals in entities.items()}, definitions, exceptions, external_sources

def highlight_pdf(input_pdf_path, output_pdf_path, categorized_data):
    doc = fitz.open(input_pdf_path)

    color_map = {
        "rules": (1, 1, 0),           # Yellow
        "entities": (0.5, 0.8, 1),    # Light Blue
        "definitions": (0.8, 1, 0.8), # Light Green
        "exceptions": (1, 0.6, 0.6),  # Light Coral
        "external_sources": (0.8, 0.6, 1) # Plum
    }

    def highlight_terms(terms, color_rgb):
        for page in doc:
            for term in terms:
                if not term.strip():  # Skip empty
                    continue
                text_instances = page.search_for(term, quads=False)  # Simple search
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors(stroke=color_rgb)
                    highlight.update()

    # Highlight per category
    highlight_terms(categorized_data.get("rules", []), color_map["rules"])

    for entity_list in categorized_data.get("entities", {}).values():
        highlight_terms(entity_list, color_map["entities"])

    highlight_terms(categorized_data.get("definitions", []), color_map["definitions"])
    highlight_terms(categorized_data.get("exceptions", []), color_map["exceptions"])
    highlight_terms(categorized_data.get("external_sources", []), color_map["external_sources"])

    doc.save(output_pdf_path)
    doc.close()



def extract_policy_insights(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    rules, entities, definitions, exceptions, external_sources = categorize_sentences(text)
    return {
        "rules": rules,
        "entities": entities,
        "definitions": definitions,
        "exceptions": exceptions,
        "external_sources": external_sources
    }