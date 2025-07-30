import json
import streamlit as st
from sage_web_apps.constants import SAGE_VERSIONS
from sage_web_apps.file_manager import SageFileManager
import os
import datetime

from sage_web_apps.streamlit_utils import download_show_config, get_config_params, load_preset
from sage_web_apps.utils import verify_params

st.title("Sage GUI")


c1, c2 = st.columns(2, vertical_alignment="bottom")
with c1:
    VERSION = st.selectbox(
        "Select Sage Version",
        options=SAGE_VERSIONS,
        index=0,  # Default to the first version
        help="Select the Sage version you want to use.",
    )

with c2:
    create_config = st.checkbox(
        "Create Configuration File",
        value=True,
        help="Whether to create a configuration file for Sage.",
    )
sage_file_manager = SageFileManager(VERSION)
output_dir = sage_file_manager.results_directory_path

if create_config:
    params = get_config_params(True, os.getcwd(), output_dir)

    if params is None:
        st.error("Failed to load configuration parameters.")
        #st.stop()

    config_json = json.dumps(params, indent=2)
else:
    config_file = st.file_uploader(
        "Upload Configuration File (JSON)",
        type=["json"],
        help="Upload a Sage configuration file in JSON format.",
    )
    if config_file is not None:
        config_json = config_file.getvalue().decode("utf-8")
        params = json.loads(config_json)
    else:
        st.stop()

are_params_valid = False
try:
    verify_params(params)
    are_params_valid = True
except ValueError as e:
    st.error(f"Parameter verification failed: {str(e)}")

with st.container(border = True):

    c1, c2 = st.columns(2, vertical_alignment="bottom")
    with c1:
        output_type = st.selectbox(
            "Output Type",
            options=["csv", "parquet"],
            index=1,  # Default to 'csv'
            help="Select the output file format.",
        )

    with c2:
        include_fragment_annotations = st.checkbox(
            "Include Fragment Annotations",
            value=True,
            help="Whether to include fragment annotations in the output.",
        )

    if st.checkbox("Add Date/Time to Output Directory", 
                    value=True, 
                    help="Whether to append the current date and time to the output directory name."):
        # update the output directory with current date and time
        date_str = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '-').replace('.', '-')
        params['output_directory'] = f"{params['output_directory']}_{date_str}"

    if st.button("Run Sage", disabled=not are_params_valid, use_container_width=True):
        # def run_search(self, json_path: str, output_path: str, include_fragment_annotations: bool = True, output_type: str = "csv"):

        st.caption("Output path")
        st.code(params["output_directory"], language="plaintext")
        with st.spinner("Running Sage..."):
            sage_file_manager.run_search(
                params=params,
                output_path=params["output_directory"],
                include_fragment_annotations=include_fragment_annotations,
                output_type=output_type,
            )

        st.success("Sage run completed successfully!")
        
        # Show the folder structure of the results directory
        st.write("Results Directory Structure:")
        files = os.listdir(params["output_directory"])
        for file in files:
            st.write(file)


