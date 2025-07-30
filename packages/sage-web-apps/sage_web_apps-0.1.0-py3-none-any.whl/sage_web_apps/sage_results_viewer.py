import os
import streamlit as st

from sage_web_apps.constants import SAGE_VERSIONS
from sage_web_apps.file_manager import SageFileManager


VERSION = st.selectbox(
    "Select Sage Version",
    options=SAGE_VERSIONS,
    index=0,  # Default to the first version
    help="Select the Sage version you want to use.",
)

sage_file_manager = SageFileManager(VERSION)
st.write("Sage File Manager initialized with version: ", VERSION)
st.write("Current working directory: ", os.getcwd())

input_option = st.selectbox(
    "Select Input Option",
    ["Results Folder", "Results Path"],
    index=0,
)

if input_option == "Results Folder":
    working_dir = os.getcwd()
    output_dir = sage_file_manager.results_directory_path

    c1, c2 = st.columns([3, 1])
    with c1:
        results_folder = st.text_input(
            "Results Folder",
            value=output_dir,
            help="Enter the path to the results folder where Sage will save the results.",
        )
    with c2:
        if st.button("Load"):
            if not os.path.exists(results_folder):
                st.error(f"Results folder {results_folder} does not exist.")
            else:
                st.success(f"Results folder {results_folder} loaded successfully.")

            #make df of all folders 
            results_folders = [f for f in os.listdir(results_folder) if os.path.isdir(os.path.join(results_folder, f))]
            st.write("Available Results Folders:")
            st.write(results_folders)
else:
    results_path = st.text_input(
        "Results Path",
        value=sage_file_manager.results_directory_path,
        help="Enter the path to the results file.",
    )
    
