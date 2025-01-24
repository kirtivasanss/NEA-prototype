import streamlit as st
from PyPDF2 import PdfReader
import docx2txt
import json
import os
from json_store import store_json
from create_json import create_json


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    return text


def extract_text_from_docx(file):
    doc = docx2txt.process(file)
    return doc


def save_json_files(json_files, directory="Temp"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    for file_name, content in json_files.items():
        with open(os.path.join(directory, file_name), "w") as f:
            f.write(content)


def load_json_files(directory="Temp"):
    json_files = {}
    if os.path.exists(directory):
        for file_name in os.listdir(directory):
            if file_name.endswith(".json"):
                with open(os.path.join(directory, file_name), "r") as f:
                    json_files[file_name] = f.read()
    return json_files


def main():
    st.title("Add Resumes")

    # Initialize session state variables
    if "processed_file" not in st.session_state:
        st.session_state["processed_file"] = None
    if "resume_text" not in st.session_state:
        st.session_state["resume_text"] = None
    if "json_files" not in st.session_state:
        st.session_state["json_files"] = {}
    if "current_file_index" not in st.session_state:
        st.session_state["current_file_index"] = 0
    if "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = None
    if "processing_complete" not in st.session_state:
        st.session_state["processing_complete"] = False

    # File uploader
    uploaded_files = st.file_uploader("Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True)

    if uploaded_files and uploaded_files != st.session_state["uploaded_files"]:
        st.session_state["uploaded_files"] = uploaded_files
        st.session_state["current_file_index"] = 0
        st.session_state["processing_complete"] = False

    if st.session_state["uploaded_files"]:
        total_files = len(st.session_state["uploaded_files"])
        current_index = st.session_state["current_file_index"]

        st.write(f"Processing file {current_index + 1} of {total_files}")

        # Progress bar
        progress = st.progress(current_index / total_files)

        if not st.session_state["processing_complete"]:
            if st.button("Process Resume"):
                file_to_process = st.session_state["uploaded_files"][current_index]

                try:
                    if file_to_process.name.endswith(".pdf"):
                        st.session_state["resume_text"] = extract_text_from_pdf(file_to_process)
                    elif file_to_process.name.endswith(".docx"):
                        st.session_state["resume_text"] = extract_text_from_docx(file_to_process)
                    else:
                        st.warning(f"Unsupported file type: {file_to_process.name}")
                        st.stop()

                    st.session_state["processed_file"] = file_to_process.name

                    with st.spinner("Processing resume and creating JSON files..."):
                        create_json(st.session_state["resume_text"])

                    st.session_state["json_files"] = load_json_files()
                    st.rerun()

                except Exception as e:
                    st.error(f"Error processing {file_to_process.name}: {e}")

            if st.session_state["processed_file"]:
                st.header(f"Processing: {st.session_state['processed_file']}")

                with st.expander("Resume Text"):
                    st.text_area("Extracted Text", st.session_state["resume_text"], height=300)

                edited_json_files = {}
                for file_name, content in st.session_state["json_files"].items():
                    with st.expander(file_name):
                        edited_content = st.text_area(f"Edit {file_name}", content, height=200)
                        edited_json_files[file_name] = edited_content

                if st.button("Save and Process Next"):
                    save_json_files(edited_json_files)
                    with st.spinner("Saving and storing JSON files..."):
                        store_json()

                    # Move to next file or complete
                    if current_index + 1 < total_files:
                        st.session_state["current_file_index"] += 1
                        st.session_state["processed_file"] = None
                        st.session_state["resume_text"] = None
                        st.session_state["json_files"] = {}
                    else:
                        st.session_state["processing_complete"] = True
                    st.rerun()

        if st.session_state["processing_complete"]:
            st.success("All files have been processed and stored in the database!")
            if st.button("Process New Files"):
                # Reset all session state
                st.session_state["uploaded_files"] = None
                st.session_state["current_file_index"] = 0
                st.session_state["processed_file"] = None
                st.session_state["resume_text"] = None
                st.session_state["json_files"] = {}
                st.session_state["processing_complete"] = False
                st.rerun()
    else:
        st.info("Upload and process files to begin.")


if __name__ == "__main__":
    main()