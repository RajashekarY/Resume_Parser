from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
import pandas as pd
import spacy
from spacy.matcher import Matcher
import re
from pprint import pprint


######################################### Pdfminer #########################################
## convert pdf to text using Pdfminer
resume=''
pdf=r".\src\resume.pdf"
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(
                                resource_manager,
                                fake_file_handle,
                                codec='utf-8',
                                laparams=LAParams()
                        )
            page_interpreter = PDFPageInterpreter(
                                resource_manager,
                                converter
                            )
            page_interpreter.process_page(page)
            text = fake_file_handle.getvalue()
            yield text
            converter.close()
            fake_file_handle.close()

for page in extract_text_from_pdf(pdf):
    resume += ' ' + page
######################################### SpaCy ############################################
## Parsing through the text resume using spaCy NLP features
nlp = spacy.load('en_core_web_sm')

def name(resume):
    matcher = Matcher(nlp.vocab)
    doc = nlp(resume)
    pattern = [{'POS': 'PROPN',"IS_ALPHA":True},{'POS': 'PROPN',"IS_ALPHA":True}]
    matcher.add('NAME', None, pattern)
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        return str(span.text).strip()
def number(resume):
    matcher = Matcher(nlp.vocab)
    doc=nlp(resume)
    matcher=Matcher(nlp.vocab)
    pattern=[{'LIKE_NUM':True,'LENGTH':{">=": 10}}]
    matcher.add('PHONE NUMBER',None,pattern)
    matches=matcher(doc)
    for id,s,e in matches:
        return(str(doc[s:e]).strip())
def skills(resume, skills):
    doc = nlp(resume)
    noun_chunks = doc.noun_chunks
    skills=[skill.lower().strip() for skill in skills]
    skillset = []
    for token in doc:
        if token.text.lower().strip() in skills:
            skillset.append(token.text)
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
            return ' '.join([skill.capitalize() for skill in set(skill.lower() for skill in skillset)])
def residence(resume):
    doc = nlp(resume)
    for ent in doc.ents:
        if ent.label_=="GPE":
            return str(ent.sent).strip()
def email(resume):
    doc=nlp(resume)
    for token in doc:
        if '@' in token.text:
            return token.text.strip()
def languages(resume):
    ## Storing all languages from a dataset (186)
    data = pd.read_csv(r".\src\Languages.csv", names=["a","b","c","language","d"])
    languages = data.language.tolist()
    languages=[language.strip() for language in languages]

    doc=nlp(resume)
    matches=[]
    for token in doc:
        if token.text.capitalize() in languages:
            matches.append(token.text)
    return(' '.join(list(set(matches))))

skl=['routing','switching','OSPF','CCNA','CCNP','BGP','Python','programming','leadership','Orgnaized','Deadline']

print("#"*75)
print(f"RESUME: {pdf}")
print(f"NAME: {name(resume)}")
print(f"ADRESS: {residence(resume)}")
print(f"PHONE NUMBER: {number(resume)}")
print(f"EMAIL: {email(resume)}")
print(f"LANGUAGES: {languages(resume)}")
print(f"MATCHED SKILLS: {skills(resume,skl)}")
print("#"*75)
