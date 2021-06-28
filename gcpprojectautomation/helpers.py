import os
from google.oauth2 import service_account
import json
import re
import logging as log


def get_credentials():
    """
    Gets the credentials set for Google Cloud SDK. Credentials are for service accounts at this time.
    This function specifically uses this as an example:
    https://cloud.google.com/docs/authentication/production#auth-cloud-implicit-python
    Credentials flow:
    :filename: If filename is None, defaults to the environment variables
    :return: credentials object
    """
    # Get the credential
    if os.path.exists(os.getenv("GCP_AUTOMATION_CONFIG")):
        credential_location = os.getenv("GCP_AUTOMATION_CONFIG")
        with open(credential_location) as f:
            credential_location = json.load(f)
        credential = credential_location['Config'][0]['Authentication']
        log.info(f"Retrieved credentail location as {credential}")
    else:
        raise ValueError("Error in get_credentials function when calling 'GCP_AUTOMATION_CONFIG'")

    # Construct the credentials request
    try:
        # Turn provided string into a filepath
        credentials = service_account.Credentials.from_service_account_file(
            filename=credential,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        log.info("Credentials object constructed from service account file")
        return credentials
    except Exception as e:
        return e


def get_billing_info():
    """
    Gets the BillingAccountId from config
    :return: billing_account_id string
    """
    # Get the credential
    if os.path.exists(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")):
        location = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        with open(location) as f:
            location = json.load(f)
        billing_account_id = location['Config'][0]['Authentication']
        log.info(f"Retrieved Billing Account Id location as {billing_account_id}")
        return billing_account_id
    else:
        raise ValueError("Error in get_billing_info function when calling 'GOOGLE_APPLICATION_CREDENTIALS'")


def check_project_id(project_id):
    """
    Performs a regex and replacement on project id when the class is called.
    Replaces all Capitalized letters with lowercase letters and spaces with '-'.
    Throws error if:
    '-' used at start of project_id
    Any special characters other than '-' used
    Any known special words are used

    Note:
        GCP only allows lowercase letters, digits and hyphens. Projects must start with a letter and cannot have
        trailing hyphens. Some words are also restricted.
        Ref: https://cloud.google.com/resource-manager/docs/creating-managing-projects

    :param project_id: project id from NewGCPProject class
    :return: formatted project_id
    """
    # Convert variable into a string
    project_id = str(project_id)
    # Replace Capital letters and spaces
    project_id = project_id.replace(" ", "-").lower()

    # Throw an error if any known incorrect usages found
    try:
        if re.search("^-|[^a-z0-9-]|google|ssl|-$", project_id):
            raise ValueError("Invalid characters or words in Project ID")
        elif len(project_id) > 30:
            raise ValueError("Too many characters in Project ID")
        elif len(project_id) < 6:
            raise ValueError("More Characters required in Project ID")
        else:
            log.info(f"Project Id {project_id} passed regex check")
            project_outcome = {
                "outcome": True,
                "project_id": project_id
            }
            return project_outcome
    except ValueError as e:
        log.warning(f"Proposed Id {project_id} violates known google policies: "
                    "https://cloud.google.com/resource-manager/docs/creating-managing-projects")
        project_outcome = {
            "outcome": False,
            "project_id": project_id
        }
        return project_outcome
