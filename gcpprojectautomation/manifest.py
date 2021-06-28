# File to manage project manifests
import json
import os
import logging as log
import pprint


class Manifest(object):
    def __init__(self, manifest_name):
        # Run the manifest setting method
        self.local_manifest_location = ""
        self.remote_manifest_location = ""
        self.remote_manifest_authentication = ""
        self.auto_query_remote_manifest = ""
        self.set_manifest_settings()
        self.manifest_name = manifest_name
        self.manifest = self.get_manifest()

    def set_manifest_settings(self):
        """
        Get settings for manifest from the config file
        :return: location of settings
        """
        # Get the configuration settings from the environment variable set
        with open(os.getenv("GCP_AUTOMATION_CONFIG")) as f:
            config_data = json.load(f)
        # Set the variables in the class
        self.local_manifest_location = config_data['Config'][0]["ManifestSettings"][0]["LocalManifestLocation"]
        self.remote_manifest_location = config_data['Config'][0]["ManifestSettings"][0]["RemoteManifestLocation"]
        self.remote_manifest_authentication = \
            config_data['Config'][0]["ManifestSettings"][0]["RemoteManifestAuthentication"]
        self.auto_query_remote_manifest = config_data['Config'][0]["ManifestSettings"][0]["AutoQueryRemoteManifest"]
        log.info("Manifest location settings imported")

    def get_local_manifest(self):
        """
        Gets manifest from the ./bin/manifests file
        :param manifest_name: name of the manifest
        :return: manfiestobject
        """
        # Set up the filepath
        manifest_location = f"{self.local_manifest_location}/{self.manifest_name}.json"
        log.info(f"Manifest location set to {manifest_location}")
        # Confirm that file exists locally
        if os.path.exists(manifest_location):
            # Get the manifest
            with open(manifest_location) as f:
                manifest = json.load(f)
                log.info(f"Manifest exists at {manifest_location} and loaded")
        else:
            # If file does not exists, log info and set manifest to DoesNotExist
            log.info(f"Manifest does not exists at {manifest_location}. Check the manifest name of {self.manifest_name} or"
                     f"get remotely")
            manifest = "DoesNotExistLocally"

        # Return output of manifest
        return manifest

    def get_remote_manifest(self):
        """
        Gets specified manifests from remote location defined in config
        :param manifest_name:
        :return: manifest object
        """
        # Construct query
        # Send query
        # Process result
        # Return outcome
        return "DoesNotExistRemotely"

    def get_manifest(self):
        """
        Gets specfied manifest. First queries local manifests, then queries remote manifest if not found.
        Notifies user if not found
        :param manifest_name:
        :return:
        """
        manifest = ""
        if self.auto_query_remote_manifest == "LocalOnly":
            # Query locally, if not found, return not found
            manifest = self.get_local_manifest()
        elif self.auto_query_remote_manifest == "RemoteOnly":
            # Query remotely, if not found, return not found
            manifest = self.get_remote_manifest()
        elif self.auto_query_remote_manifest == "LocalFirst":
            # Query local manifest
            local_manifest = self.get_local_manifest()
            if local_manifest == "DoesNotExistLocally":
                log.info(f"Function get_manifest. Manifest {self.manifest_name} does not exist locally")
                # If not found locally, query remote manifest API
                remote_manifest = self.get_remote_manifest()
                if remote_manifest == "DoesNotExistRemotely":
                    manifest = "DoesNotExist"
                    log.warning(f"Manifest {self.manifest_name} does not exist locally or remotely. Check name.")
                else:
                    log.info(f"Manifest {self.manifest_name} found remotely. One API call made")
                    # Store manifest locally
                    local_store = self.store_manifest_locally(remote_manifest)
                    log.info(f"Manifest for {self.manifest_name} outcome is {local_store}")
                    manifest = remote_manifest
            else:
                log.info(f"Manifest {self.manifest_name} found locally. No API calls made")
        elif self.auto_query_remote_manifest == "RemoteFirst":
            # Query remote manifest
            remote_manifest = self.get_remote_manifest()
            if remote_manifest == "DoesNotExistRemotely":
                # Remote manifest not found, query locally
                local_manifest = self.get_local_manifest()
                if local_manifest == "DoesNotExistLocally":
                    manifest = "DoesNotExist"
                else:
                    manifest = local_manifest
            else:
                # Store manifest locally
                local_store = self.store_manifest_locally(remote_manifest)
                log.info(f"Manifest for {self.manifest_name} outcome is {local_store}")
                manifest = remote_manifest

        # Return manifest
        return manifest

    def store_manifest_locally(self, manifest):
        """
        If the specified manifest is not found locally, and AutoQueryRemoteManifest not set to 'LocalOnly', store
        manifest locally
        :param manifest: the manifest to be stored
        :return: True / False
        """
        # Confirm the auto_query_remote_manifest
        if self.auto_query_remote_manifest == "LocalOnly":
            log.info(f"AutoQueryRemoteManifest set to {self.auto_query_remote_manifest}. Manifest not saved locally. "
                     f"Further information: "
                     f"https://github.com/creative-appnologies/gcp_project_automation/wiki/Manifest-Class")
            return False
        else:
            log.info(f"AutoQueryRemoteManifest set to {self.auto_query_remote_manifest}. Saving manifest. Further "
                     f"information: https://github.com/creative-appnologies/gcp_project_automation/wiki/Manifest-Class")
            # Construct the file path
            file_path = f"{self.local_manifest_location}/{manifest['ManifestName']}.json"
            with open(file_path, "w") as f:
                json.dump(manifest, f)
            # Confirm the file now exists
            if os.path.exists(file_path):
                return True
            else:
                raise AssertionError(f"Error creating {file_path}. Manifest not saved")
