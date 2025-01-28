import streamlit as st
from PyPDF2 import PdfReader
import docx2txt
import json
import os
from json_store import store_json
from create_json import create_json

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
def main():
    st.title("Document to Text Converter")
    st.markdown("Upload PDF or DOCX files, and process them into editable JSON files.")

    # Display JSON files from the Temp directory
    st.header("Previously Saved JSON Files")
    saved_json_files = load_json_files()
    if saved_json_files:
        for file_name, content in saved_json_files.items():
            with st.expander(file_name):
                st.text_area(f"Content of {file_name}", content, height=200, key=f"saved_{file_name}")
    else:
        st.info("No previously saved JSON files found in the Temp directory.")

    # File uploader for multiple files
    uploaded_files = st.file_uploader("Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True)

    if "processed_file" not in st.session_state:
        st.session_state["processed_file"] = None
    if "resume_text" not in st.session_state:
        st.session_state["resume_text"] = None
    if "json_files" not in st.session_state:
        st.session_state["json_files"] = {}
    if "errors" not in st.session_state:
        st.session_state["errors"] = []

    # Process button
    if uploaded_files:
        st.write(f"You uploaded {len(uploaded_files)} files.")

        col1, col2 = st.columns(2)

        # Process single file
        with col1:
            if st.button("Process Resumes"):
                file_to_process = uploaded_files[0]

                try:
                    if file_to_process.name.endswith(".pdf"):
                        st.session_state["resume_text"] = extract_text_from_pdf(file_to_process)
                    elif file_to_process.name.endswith(".docx"):
                        st.session_state["resume_text"] = extract_text_from_docx(file_to_process)
                    else:
                        st.warning(f"Unsupported file type: {file_to_process.name}")
                        st.stop()

                    st.session_state["processed_file"] = file_to_process.name

                    # Create JSON files from the processed resume
                    with st.spinner("Processing resume and creating JSON files..."):
                        create_json(st.session_state["resume_text"])

                    # Load JSON files for editing
                    st.session_state["json_files"] = load_json_files()

                    st.rerun()

                except Exception as e:
                    st.error(f"Error processing {file_to_process.name}: {e}")

        # Process all files
        with col2:
            if st.button("Process All"):
                progress = st.progress(0)
                completed = 0
                total_files = len(uploaded_files)

                for idx, file_to_process in enumerate(uploaded_files):
                    try:
                        if file_to_process.name.endswith(".pdf"):
                            resume_text = extract_text_from_pdf(file_to_process)
                        elif file_to_process.name.endswith(".docx"):
                            resume_text = extract_text_from_docx(file_to_process)
                        else:
                            raise ValueError(f"Unsupported file type: {file_to_process.name}")

                        with st.spinner(f"Processing {file_to_process.name}..."):
                            create_json(resume_text)
                            completed += 1
                            progress.progress(int((completed / total_files) * 100))
                            st.success(f"Finished processing: {file_to_process.name}")

                    except Exception as e:
                        st.session_state["errors"].append({"file": file_to_process.name, "error": str(e)})
                        st.error(f"Error processing {file_to_process.name}: {e}")

                st.success("Processing complete!")

                if st.session_state["errors"]:
                    st.warning("Some resumes encountered errors. Please review below.")

    # Display errors and allow editing
    if st.session_state["errors"]:
        st.header("Resumes with Errors")
        for error in st.session_state["errors"]:
            st.error(f"File: {error['file']} - Error: {error['error']}")

            file_path = os.path.join("Temp", error['file'].replace(".pdf", ".json").replace(".docx", ".json"))
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    content = f.read()

                edited_content = st.text_area(f"Edit JSON for {error['file']}", content, height=200)

                if st.button(f"Save Changes: {error['file']}", key=f"save_{error['file']}"):
                    with open(file_path, "w") as f:
                        f.write(edited_content)
                    st.success(f"Changes saved for {error['file']}.")

    if st.session_state["processed_file"]:
        st.header(f"Processing: {st.session_state['processed_file']}")

        # Show resume text in a dropdown section
        with st.expander("Resume Text"):
            st.text_area("Extracted Text", st.session_state["resume_text"], height=300)

        # Show and edit JSON files
        edited_json_files = {}
        for file_name, content in st.session_state["json_files"].items():
            with st.expander(file_name):
                edited_content = st.text_area(f"Edit {file_name}", content, height=200)
                edited_json_files[file_name] = edited_content

        # Save changes and trigger next function
        if st.button("Save and Proceed"):
            save_json_files(edited_json_files) 
            st.session_state["json_files"] = edited_json_files

            # Store JSON files in the database
            with st.spinner("Saving and storing JSON files..."):
                store_json(st.session_state["resume_text"])

            st.success("Files saved and stored in the database. Starting next function...")
            # Add your next function here
    else:
        st.info("Upload and process a file to begin.")

if __name__ == "__main__":
    main()
