from pypdf import PdfReader
from Core.Unifiedstate import ElevateMasterState
import re


# this tool is responsible for reading the pdf resume and cleaning it 
#it is currently not being used as a tool right not but as part of the core system but soon will be converted to a tool
def pdf_reader(state: ElevateMasterState):

    """This function reads a PDF resume, extracts the text, and cleans it by removing special characters and unnecessary formatting. It returns a structured dictionary containing the cleaned resume text under the key 'raw_resume'."""
    file = state.get("file")
    pdf_reader = PdfReader(file)

    page_content = {}

    for indx, pdf_page in enumerate(pdf_reader.pages):
        page_content[indx + 1] = pdf_page.extract_text()
    
    full_text = " ".join(str(val) for val in page_content.values())
    raw_lines = full_text.split('\n')
    clean_queries = []
    
    for line in raw_lines:
        clean = re.sub(r'[*#\-0-9.]', '', line).strip()
        if clean:
            clean_queries.append(clean)
    

    result =  "\n".join(i for i in clean_queries)
    
    final_result = {"raw_resume": result}
    print(final_result)
    return {"raw_resume": result}