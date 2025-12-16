import logging
import os


def custom_path_filter(path):
    # Define the project root name
    project_root = "react-from-scratch"
    
    # Find the index of the project root in the path
    idx = path.find(project_root)
    if idx != -1:
        # Extract the portion of the path after the project root
        path = path[idx+len(project_root):]
    return path

class CustomLogRecord(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pathname = custom_path_filter(self.pathname)


def setup_logger(log_filename="app.log"):
    # Get the ReAct-Agent root directory (3 levels up from this file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, "..", "..")
    project_root = os.path.abspath(project_root)

    # Define the log file path in the project root
    log_filepath = os.path.join(project_root, log_filename)

    # Define the logging configuration
    logging.setLogRecordFactory(CustomLogRecord)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(module)s] [%(pathname)s]: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_filepath, mode='a')
        ]
    )

    # Return the configured logger
    return logging.getLogger()

logger = setup_logger()