import streamlit as st
from PyPDF2 import PdfReader
import docx2txt
import os
from create_json import create_json
from json_store import store_json


# Function to extract text from a PDF file
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    return text

# Function to extract text from a DOCX file
def extract_text_from_docx(file):
    doc = docx2txt.process(file)
    return doc

# Save JSON files to the Temp directory
def save_json_files(json_files, directory="Temp"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    for file_name, content in json_files.items():
        with open(os.path.join(directory, file_name), "w") as f:
            f.write(content)

# Load JSON files from the Temp directory
def load_json_files(directory="Temp"):
    json_files = {}
    if os.path.exists(directory):
        for file_name in os.listdir(directory):
            if file_name.endswith(".json"):
                with open(os.path.join(directory, file_name), "r") as f:
                    json_files[file_name] = f.read()
    return json_files

# Main function to run the Streamlit app
def addPage():
    st.title("Document to Text Converter")
    st.markdown("Upload PDF or DOCX files, and process them into editable JSON files.")

    # Initialize session state variables if they do not exist
    if "files_to_process" not in st.session_state:
        st.session_state["files_to_process"] = []
    if "processed_file" not in st.session_state:
        st.session_state["processed_file"] = ""
    if "resume_text" not in st.session_state:
        st.session_state["resume_text"] = ""
    if "json_files" not in st.session_state:
        st.session_state["json_files"] = {}

    # Only show the uploader if no files have been stored in session state yet.
    if not st.session_state["files_to_process"]:
        uploaded_files = st.file_uploader("Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True)
        if uploaded_files:
            # Store the uploaded files in session state so that they are not shown again
            st.session_state["files_to_process"] = uploaded_files

    # If there are files waiting to be processed, show the number of files and the process button.
    if st.session_state["files_to_process"]:
        st.write(f"There are {len(st.session_state['files_to_process'])} file(s) waiting to be processed.")

        # Only allow processing a new file if one is not already being processed.
        if not st.session_state["processed_file"]:
            if st.button("Process Next Resume"):
                file_to_process = st.session_state["files_to_process"].pop(0)
                try:
                    if file_to_process.name.lower().endswith(".pdf"):
                        st.session_state["resume_text"] = extract_text_from_pdf(file_to_process)
                    elif file_to_process.name.lower().endswith(".docx"):
                        st.session_state["resume_text"] = extract_text_from_docx(file_to_process)
                    else:
                        st.warning(f"Unsupported file type: {file_to_process.name}")
                        return

                    st.session_state["processed_file"] = file_to_process.name

                    # Create JSON files from the processed resume
                    with st.spinner("Processing resume and creating JSON files..."):
                        create_json(st.session_state["resume_text"])

                    # Load JSON files for editing
                    st.session_state["json_files"] = load_json_files()

                    st.rerun()

                except Exception as e:
                    st.error(f"Error processing {file_to_process.name}: {e}")

    else:
        # No files in session state means either no upload or all files have been processed.
        st.info("Upload files to begin or all files have been processed.")

    # If a file is currently being processed, show its details and JSON editing interface.
    if st.session_state["processed_file"]:
        st.header(f"Processing: {st.session_state['processed_file']}")

        with st.expander("Resume Text"):
            st.text_area("Extracted Text", st.session_state["resume_text"], height=300)

        # Display JSON files for editing
        edited_json_files = {}
        for file_name, content in st.session_state["json_files"].items():
            with st.expander(file_name):
                edited_content = st.text_area(f"Edit {file_name}", content, height=200)
                edited_json_files[file_name] = edited_content

        # Save changes and proceed
        if st.button("Save and Proceed"):
            save_json_files(edited_json_files)
            st.session_state["json_files"] = edited_json_files

            with st.spinner("Saving and storing JSON files..."):
                store_json(st.session_state["resume_text"])

            st.success("Files saved and stored in the database. Starting next function...")

            # Clear the current file variables so that the next file (if any) can be processed
            st.session_state["processed_file"] = ""
            st.session_state["resume_text"] = ""
            st.rerun()
