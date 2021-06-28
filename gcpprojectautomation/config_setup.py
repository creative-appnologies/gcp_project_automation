import json
import os
import shutil


def setup_config_file():
    """
    Tests to ensure config file exists. If not, copies example file over
    Documentation:
    :return: True or False
    """
    # Test if file exists
    if os.path.exists(os.getenv("GCP_AUTOMATION_CONFIG")):
        file_exists = True
    else:
        # Copy file from example file across
        example_file = "./bin/example_config.json"
        destination = os.getenv("GCP_AUTOMATION_CONFIG")
        try:
            shutil.copyfile(example_file, destination)
            file_exists = True
            # If source and destination are same
        except shutil.SameFileError:
            print("Source and destination represents the same file.")
            file_exists = True
        # If destination is a directory.
        except IsADirectoryError:
            print("Destination is a directory.")
            file_exists = False
        # If there is any permission issue
        except PermissionError:
            print("Permission denied.")
            file_exists = False
        # For other errors
        except Exception as e:
            print(f"Error occurred while copying file. Exception: {e}")
            file_exists = False
    return file_exists


def set_config_file():
    """
    Checks all aspects of the config file
    :return: True
    """
    # Ensure file exists
    file_exists = setup_config_file()

    # With config file, setup project
    if file_exists:
        # Import settings from the config file
        config_file = str(os.getenv("GCP_AUTOMATION_CONFIG"))
        with open(config_file) as file:
            config = json.load(file)

        # Confirm and set Log File location
        if 'LoggingSettings' not in config['Config'][0] or config['Config'][0]['LoggingSettings'] is None \
                or config['Config'][0]['LoggingSettings'] == "":
            log_settings = input("No logging settings found. Use defaults where possible? (Y/N): ")
            if log_settings == "Y":
                config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogging"] = "True"
                config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogLocation"] \
                    = input("File log location: ")
                config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogLevel"] = "Debug"
                config['Config'][0]['LoggingSettings'][0]['StreamLogging'][0]["StreamLogging"] = "True"
                config['Config'][0]['LoggingSettings'][0]['StreamLogging'][0]["LogStream"] = "Console"
                config['Config'][0]['LoggingSettings'][0]['StreamLogging'][0]["StreamLogLevel"] = "Warning"
            else:
                # Set up File Logging or disable
                file_logging = input("Use file logging? (Y/N")
                if file_logging == "Y":
                    config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogging"] = "True"
                    config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogLocation"] \
                        = input("File log location: ")
                    log_level = input("Choose default logging level for file logging: "
                                      "Debug (D), Info (I), Warning (W), Error(E), Critical(C)")
                    if log_level == "D":
                        config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogLevel"] = "Debug"
                    elif log_level == "I":
                        config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogLevel"] = "Info"
                    elif log_level == "W":
                        config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogLevel"] = "Warning"
                    elif log_level == "E":
                        config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogLevel"] = "Error"
                    elif log_level == "C":
                        config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogLevel"] = "Critical"
                    else:
                        print("File log level not selected, defaulting to Debug")
                        config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogLevel"] = "Debug"
                else:
                    config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogging"] = "False"
                    config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogLocation"] = "False"
                    config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogLevel"] = "Debug"
                    print("Logging to file disabled")

                # Set up log stream or disable
                log_stream = input("Currently supported log streams are: Console (C) or enter nothing to disable")
                if log_stream == "C":
                    config['Config'][0]['LoggingSettings'][0]['StreamLogging'][0]["StreamLogging"] = "True"
                    config['Config'][0]['LoggingSettings'][0]['StreamLogging'][0]["LogStream"] = "Console"
                    log_level = input("Choose default logging level for file logging: "
                                      "Debug (D), Info (I), Warning (W), Error(E), Critical(C)")
                    if log_level == "D":
                        config['Config'][0]['LoggingSettings'][0]['StreamLogging'][0]["StreamLogLevel"] = "Debug"
                    elif log_level == "I":
                        config['Config'][0]['LoggingSettings'][0]['StreamLogging'][0]["StreamLogLevel"] = "Info"
                    elif log_level == "W":
                        config['Config'][0]['LoggingSettings'][0]['StreamLogging'][0]["StreamLogLevel"] = "Warning"
                    elif log_level == "E":
                        config['Config'][0]['LoggingSettings'][0]['StreamLogging'][0]["StreamLogLevel"] = "Error"
                    elif log_level == "C":
                        config['Config'][0]['LoggingSettings'][0]['StreamLogging'][0]["StreamLogLevel"] = "Critical"
                    else:
                        print("Stream log level not selected, defaulting to Debug")
                        config['Config'][0]['LoggingSettings'][0]['StreamLogging'][0]["StreamLogLevel"] = "Debug"
                else:
                    config['Config'][0]['LoggingSettings'][0]['LogStream'] = "False"
        elif config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]['FileLogLocation'] is None \
                or config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]['FileLogLocation'] == "":
            config['Config'][0]['LoggingSettings'][0]['FileLogging'][0]["FileLogLocation"] \
                = input("File log location: ")

        if 'ParentProjectName' not in config['Config'][0] or config['Config'][0]['ParentProjectName'] is None \
                or config['Config'][0]['ParentProjectName'] == "":
            user_input = input("Parent Project Name does not exist. Please input: ")
            config['Config'][0]['ParentProjectName'] = user_input

        if 'ParentProjectId' not in config['Config'][0] or config['Config'][0]['ParentProjectId'] is None \
                or config['Config'][0]['ParentProjectId'] == "":
            user_input = input("Parent Project Id does not exist. Please input: ")
            config['Config'][0]['ParentProjectId'] = user_input

        if 'Authentication' not in config['Config'][0] or config['Config'][0]['Authentication'] is None \
                or config['Config'][0]['Authentication'] == []:
            auth_file = False
            while auth_file is not True:
                auth_loc = input("Path to Authentication settings required: ")
                # Check the file path
                if os.path.exists(auth_loc):
                    config['Config'][0]['Authentication'] = auth_loc
                    auth_file = True
                else:
                    print("Path provided for Authentication does not exist. Update and try again")
        else:
            auth_file = False
            auth_loc = config['Config'][0]['Authentication']
            while auth_file is not True:
                if os.path.exists(auth_loc):
                    config['Config'][0]['Authentication'] = auth_loc
                    auth_file = True
                else:
                    print("Specified authorisation file does not exist. Update and try again")
                    auth_loc = input("Specify authorisation file path: ")

        if 'BillingAccountId' not in config['Config'][0] or config['Config'][0]['BillingAccountId'] is None \
                or config['Config'][0]['BillingAccountId'] == "":
            user_input = input("Billing Account Id does not exist. Please input: ")
            config['Config'][0]['BillingAccountId'] = user_input

        if 'ManifestSettings' not in config['Config'][0] or config['Config'][0]['ManifestSettings'] is None \
            or config['Config'][0]['ManifestSettings'] == "":
            # Confirm if the user wishes to use default
            user_input = input("No Manifest Settings detected. Use default? (Y/N)")
            if user_input == "Y":
                config['Config'][0]['ManifestSettings']['LocalManifestLocation'] = "./bin/manifests"
                config['Config'][0]['ManifestSettings']['AutoQueryRemoteManifest'] = "RemoteFirst"
                config['Config'][0]['ManifestSettings']['RemoteManifestLocation'] = "URL" #todo: update this to be accurate
                config['Config'][0]['ManifestSettings']['RemoteManifestAuthentication'] = "" #todo: Update this to be accurate
            else:
                # Set the Local Manifest Location
                config['Config'][0]['ManifestSettings']['LocalManifestLocation'] = input("Local Manifest Location: ")
                # Set the AutoQueryRemoteManifestLocation
                manifest_setting = input("Select AutoQueryRemoteManifest setting to be either: (RO) RemoteOnly, (LO) "
                                          "LocalOnly, (RF) RemoteFirst or (LF) LocalFirst: ")
                if manifest_setting == "RO":
                    config['Config'][0]['ManifestSettings']['AutoQueryRemoteManifest'] = "RemoteOnly"
                elif manifest_setting == "LO":
                    config['Config'][0]['ManifestSettings']['AutoQueryRemoteManifest'] = "LocalOnly"
                elif manifest_setting == "RF":
                    config['Config'][0]['ManifestSettings']['AutoQueryRemoteManifest'] = "RemoteFirst"
                elif manifest_setting == "LF":
                    config['Config'][0]['ManifestSettings']['AutoQueryRemoteManifest'] = "LocalFirst"
                else:
                    config['Config'][0]['ManifestSettings']['AutoQueryRemoteManifest'] = "RemoteFirst"

                # Set the remote query API
                config['Config'][0]['ManifestSettings']['RemoteManifestLocation'] = input("Insert remote query API: ")
                config['Config'][0]['ManifestSettings'][
                    'RemoteManifestAuthentication'] = ""  # todo: Update this to be accurate

        # Turn the data back into json and write back to config file
        with open(config_file, "w") as file:
            json.dump(config, file)
        return True
    else:
        print("Config file error and logging not yet enabled. Breaking execution")
        exit(1)
