#!/usr/bin/env python3
"""More detailed PDF debugging"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import PyPDF2
import fitz  # PyMuPDF

def test_specific_pdf():
    # Test one of the failing PDFs specifically
    test_file = "uploads/resumes/1_4_1768231059_document.pdf"
    
    if not os.path.exists(test_file):
        print(f"File not found: {test_file}")
        print("Available files:")
        if os.path.exists("uploads/resumes"):
            for f in os.listdir("uploads/resumes"):
                if f.endswith('.pdf'):
                    print(f"  - {f}")
        return
    
    print(f"Testing file: {test_file}")
    print(f"File size: {os.path.getsize(test_file)} bytes")
    
    # Test PyPDF2
    print("\n=== Testing PyPDF2 ===")
    try:
        with open(test_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"Number of pages: {len(pdf_reader.pages)}")
            
            text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                print(f"Page {i+1} text length: {len(page_text)}")
                text += page_text + "\n"
            
            print(f"Total text from PyPDF2: {len(text)} chars")
            if text.strip():
                print("Text preview:", text[:200])
    except Exception as e:
        print(f"PyPDF2 error: {e}")
    
    # Test PyMuPDF
    print("\n=== Testing PyMuPDF ===")
    try:
        doc = fitz.open(test_file)
        print(f"Number of pages: {doc.page_count}")
        
        text = ""
        for page_num in range(doc.page_count):
            page = doc[page_num]
            page_text = page.get_text()
            print(f"Page {page_num+1} text length: {len(page_text)}")
            text += page_text + "\n"
        
        doc.close()
        
        print(f"Total text from PyMuPDF: {len(text)} chars")
        if text.strip():
            print("Text preview:", text[:200])
        else:
            print("❌ PyMuPDF also found no text - this PDF may be image-based or corrupted")
            
    except Exception as e:
        print(f"PyMuPDF error: {e}")

if __name__ == "__main__":
    test_specific_pdf()