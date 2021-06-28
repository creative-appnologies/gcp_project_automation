import json
import os
import logging as log


class ManifestLists(object):
    def __init__(self, setup=True):
        # Run the manifest setting method
        self.local_manifest_location = ""
        self.remote_manifest_location = ""
        self.remote_manifest_login = ""
        self.auto_query_remote_manifest = ""
        self.get_manifest_settings()
        self.manifests = self.list_manifests()
        self.setup = setup

    def get_manifest_settings(self):
        """
        Get settings for manifest from the config file
        :return: location of settings
        """
        log.info(f"Manifest settings update called from ManifestLists class. Location queried "
                 f"{os.getenv('GCP_AUTOMATION_CONFIG')}")
        # Get the configuration settings from the environment variable set
        with open(os.getenv("GCP_AUTOMATION_CONFIG")) as f:
            config_data = json.load(f)
        # Set the variables in the class
        self.local_manifest_location = str(config_data['Config'][0]["ManifestSettings"][0]["LocalManifestLocation"])
        self.remote_manifest_location = config_data['Config'][0]["ManifestSettings"][0]["RemoteManifestLocation"]
        self.remote_manifest_login = config_data['Config'][0]["ManifestSettings"][0]["RemoteManifestUsername"]
        self.auto_query_remote_manifest = config_data['Config'][0]["ManifestSettings"][0]["AutoQueryRemoteManifest"]

    def list_local_manifests(self):
        """
        Lists the manifests currently available locally
        :return: local_manifest dictionary
        """
        log.info(f"Local manifest query made to {self.local_manifest_location}")
        # Get a list of the files
        file_list = os.listdir(self.local_manifest_location)
        # Create a dictionary to store results
        local_manifests = {
            "LocalManifestList": []
        }
        # Format the list
        for manifest in file_list:
            # Remove the file extension
            mani = manifest.split(".")[0]
            # Add to dictionary
            local_manifests['LocalManifestList'].append(mani)

        # Return outcome
        return local_manifests

    def list_remote_manifests(self):
        """
        Queries API to get the list of current Manifests available
        :return: remote_manifest dictionary
        """
        log.info("Remote manifest query made")
        # Query API
        pass

    def list_manifests(self):
        """
        Lists the manifests available
        :return: manifests dictionary
        """
        # Set up return object
        manifests = {}
        try:
            print(self.auto_query_remote_manifest)
            # Get the AutoQueryRemoteManifest and branch accordingly
            if self.auto_query_remote_manifest == "RemoteOnly":
                log.info(f"Query for remote manifests sent from 'list_manifests' function. One API Query call made. Further"
                         f"documentation: https://github.com/creative-appnologies/gcp_project_automation/wiki/ManifestList-Class")
                # Only get remote manifests
                # Requires API Call
                # Query API
                remote_manifests = self.list_remote_manifests()
                manifests['RemoteManifests'] = [remote_manifests["RemoteManifests"]]
                # Ensure that notation on setting made for local manifests
                manifests['LocalManifests'] = ["AutoQueryRemoteManifest set to 'RemoteOnly'. No local manifests listed"]
            elif self.auto_query_remote_manifest == "LocalOnly":
                log.info("Query for local manifests made in 'list_manifests' function'. Further documentation:"
                         "https://github.com/creative-appnologies/gcp_project_automation/wiki/ManifestList-Class")
                local_manifests = self.list_local_manifests()
                manifests['LocalManifests'] = [local_manifests["LocalManifestList"]]
                # Ensure that notation on setting for remote manifests made
                manifests['RemoteManifests'] = ["AutoQueryRemoteManifest setting to 'LocalOnly'. No remote query made"]
            elif self.auto_query_remote_manifest == "LocalFirst" or self.auto_query_remote_manifest == "RemoteFirst":
                # For this query, no tangible difference in the order of operations, so capture both
                log.info("Query for both local and remote manifests made in 'list_manifests' function. Further "
                         "documentation: "
                         "https://github.com/creative-appnologies/gcp_project_automation/wiki/ManifestList-Class")
                # Query API
                remote_manifests = self.list_remote_manifests()
                manifests['RemoteManifests'] = [remote_manifests["RemoteManifestList"]]

                # Query local manifests
                local_manifests = self.list_local_manifests()
                manifests['LocalManifests'] = [local_manifests["LocalManifestList"]]
            else:
                # Error in function call
                raise ValueError("Error calling manifest list")
        except Exception as e:
            print(e)

        return manifests
