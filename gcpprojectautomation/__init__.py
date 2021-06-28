import os
from gcpprojectautomation import config_setup
from gcpprojectautomation import logging_setup
from gcpprojectautomation import projects

# Get the Config file location
if os.getenv("GCP_AUTOMATION_CONFIG") is None:
    # Determine if user wishes to set up the config file via commandline or has a location to point to
    custom_setup = input("Configuration required for this package. Do you wish to use the commandline setup (C) or"
                         "have a preconfigured file (P)")

    if custom_setup == "C":
        # Branch to the custom setup script
        print("Made It")

    elif custom_setup == "P":
        # Get file location from user
        GCP_AUTOMATION_CONFIG = input("Place file location of configuration file here")
        # Set environment variable
        os.environ["GCP_AUTOMATION_CONFIG"] = GCP_AUTOMATION_CONFIG
    else:
        raise AttributeError("NoConfigurationProvided")
else:
    # Set basic configurations
    config = config_setup.set_config_file()
    if config is True:
        logging_setup.logging_setup()

# Version
__version__="0.1"
