#!/usr/bin/env python3
"""Debug script to test actual PDF parsing"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.resume_parser import ResumeParser

def test_pdf_parsing():
    parser = ResumeParser()
    
    # Test with actual uploaded PDFs
    upload_dirs = [
        'uploads/resumes',
        'uploads'
    ]
    
    print("=== Testing PDF Parsing ===")
    
    for upload_dir in upload_dirs:
        if os.path.exists(upload_dir):
            print(f"\nChecking directory: {upload_dir}")
            
            for filename in os.listdir(upload_dir):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(upload_dir, filename)
                    print(f"\nTesting file: {filename}")
                    
                    try:
                        # Test text extraction first
                        text = parser.extract_text(file_path)
                        print(f"Extracted text length: {len(text)} characters")
                        
                        if len(text) > 100:
                            print("Text preview:", text[:200] + "...")
                        else:
                            print("Full text:", text)
                        
                        # Test full parsing
                        if text:
                            parsed = parser.parse_resume(file_path)
                            print(f"Parsing status: {parsed.get('parsing_status', 'unknown')}")
                            print(f"Skills found: {len(parsed.get('skills', []))}")
                            print(f"Experience years: {parsed.get('total_experience_years', 0)}")
                            
                            if parsed.get('skills'):
                                print(f"Skills: {parsed['skills'][:5]}...")  # First 5 skills
                        else:
                            print("❌ No text extracted from PDF!")
                            
                    except Exception as e:
                        print(f"❌ Error parsing {filename}: {e}")
                        import traceback
                        traceback.print_exc()
        else:
            print(f"Directory {upload_dir} not found")

if __name__ == "__main__":
    test_pdf_parsing()