import azure.functions as func  # Import Azure Functions module
import logging  # Import logging module for debugging
import os  # Import os module to interact with the operating system
import subprocess  # Import subprocess module to run external scripts

def main(myblob: func.InputStream):
    """
    Azure Function triggered when a new file is uploaded to the root container (chatwithdatafiles).
    This function will process the file using embedfiles.py.
    """

    # Extract the blob name (only the file name, ignoring any folder structure)
    blob_name = os.path.basename(myblob.name)  # Ensures we always get the file name, not folder paths
    logging.info(f"Blob Trigger function started for file: {blob_name} in root container")

    try:
        # Run the embedfiles.py script, passing the blob name as an argument
        result = subprocess.run(["python", "embedfiles.py", blob_name], capture_output=True, text=True)

        # Check if the script executed successfully
        if result.returncode == 0:
            logging.info(f"Successfully processed blob {blob_name}")
        else:
            logging.error(f"Error processing file {blob_name}: {result.stderr}")

    except Exception as e:
        logging.exception(f"An error occurred while processing {blob_name}")
