import os
from gcpprojectautomation import config_setup
from gcpprojectautomation import logging_setup
from gcpprojectautomation import projects
from gcpprojectautomation import iam_object

# Get the Config file location
if os.getenv("GCP_AUTOMATION_CONFIG") is None:
    # Determine if user wishes to set up the config file via commandline or has a location to point to
    custom_setup = input("Configuration required for this package. Do you wish to use the commandline setup (C) or"
                         " have a preconfigured file (P): ")

    if custom_setup == "C":
        # Branch to the custom setup script
        print("Made It")
        # todo: Create a custom setup script

    elif custom_setup == "P":
        # Get file location from user
        GCP_AUTOMATION_CONFIG = input("Place file location of configuration file here: ")
        # Test the file exists
        path_exists = False
        while path_exists is False:
            if os.path.exists(GCP_AUTOMATION_CONFIG):
                # Set environment variable
                os.environ["GCP_AUTOMATION_CONFIG"] = GCP_AUTOMATION_CONFIG
                path_exists = True
            else:
                GCP_AUTOMATION_CONFIG = input("Place file location of configuration file here: ")
    else:
        raise AttributeError("NoConfigurationProvided")
else:
    # Set basic configurations
    config = config_setup.set_config_file()
    if config is True:
        logging_setup.logging_setup()

# Version
__version__="0.1"
