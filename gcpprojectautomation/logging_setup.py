import logging
import os
import json

# Set up the logger
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Set up the message format
formatter = logging.Formatter(fmt='%(asctime)s - gcpprojectautomation - '
                                  '%(levelname)s - %(process)d - %(name)s - %(message)s')


def logging_setup():
    """
    Sets up logging. All settings are contained within the config file. Other functions can modify the config
    Docs Location: https://github.com/creative-appnologies/gcp_project_automation/wiki/config.json
    :return: None
    """
    # Get the configuration data
    with open(os.getenv("GCP_AUTOMATION_CONFIG")) as file:
        data = json.load(file)
        logging_settings = data['Config'][0]['LoggingSettings'][0]

    # Set up file logging if enabled
    if logging_settings['FileLogging'][0]['FileLogging'] == "True":
        # Get the file path
        filelog = logging.FileHandler(logging_settings['FileLogging'][0]['FileLogLocation'])
        # Set the level
        if logging_settings['FileLogging'][0]['FileLogLevel'] == "Debug":
            filelog.setLevel(level=logging.DEBUG)
        elif logging_settings['FileLogging'][0]['FileLogLevel'] == "Info":
            filelog.setLevel(level=logging.INFO)
        elif logging_settings['FileLogging'][0]['FileLogLevel'] == "Warning":
            filelog.setLevel(level=logging.WARNING)
        elif logging_settings['FileLogging'][0]['FileLogLevel'] == "Error":
            filelog.setLevel(level=logging.ERROR)
        elif logging_settings['FileLogging'][0]['FileLogLevel'] == "Critical":
            filelog.setLevel(level=logging.CRITICAL)
        else:
            print("No logging level set")
            exit(1)
        # Set the handler message
        filelog.setFormatter(formatter)
        # Add handler
        log.addHandler(filelog)

    # Set up Stream Logging if enabled
    if logging_settings['StreamLogging'][0]["StreamLogging"] == "True":
        stream_log = logging.StreamHandler()
        if logging_settings['StreamLogging'][0]['StreamLogLevel'] == "Debug":
            stream_log.setLevel(level=logging.DEBUG)
        elif logging_settings['StreamLogging'][0]['StreamLogLevel'] == "Info":
            stream_log.setLevel(level=logging.INFO)
        elif logging_settings['StreamLogging'][0]['StreamLogLevel'] == "Warning":
            stream_log.setLevel(level=logging.WARNING)
        elif logging_settings['StreamLogging'][0]['StreamLogLevel'] == "Error":
            stream_log.setLevel(level=logging.ERROR)
        elif logging_settings['StreamLogging'][0]['StreamLogLevel'] == "Critical":
            stream_log.setLevel(level=logging.CRITICAL)
        else:
            print("No logging level set")
            exit(1)

    # Set the handler message
    stream_log.setFormatter(formatter)
    # Add handler
    log.addHandler(stream_log)
