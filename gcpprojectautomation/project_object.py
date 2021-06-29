import os
import time

from gcpprojectautomation import helpers
import googleapiclient.discovery
import json
import pprint
import logging as log
import googleapiclient.errors


class GCPProject(object):
    """
    Class for creating new GCP Projects.
    Assumes that the following commands have been run:
    gcloud auth application-default login
    gcloud auth login

    A great resource for a full lifecycle of projects can be found here:
    https://snyk.io/advisor/python/google-cloud-resource-manager
    """
    def __init__(self, project_id, project_name, project_manifest):
        if helpers.check_project_id(project_id)["outcome"] is True:
            self.project_id = project_id
        else:
            log.critical(f"Project ID {project_id} not accepted. Program exiting")
            exit(1)
        self.project_name = str(project_name)
        self.parent_project_type = ""
        self.parent_project_id = ""
        self.credentials = helpers.get_credentials()
        self.billing_account_id = ""
        self.set_project_meta_data()
        self.cloud_service = googleapiclient.discovery.build("cloudresourcemanager", "v1", credentials=self.credentials)
        self.service_authenticated = googleapiclient.discovery.build('serviceusage', 'v1', credentials=self.credentials)
        self.project_exists = self.does_project_exist()
        self.project_manifest = project_manifest
        if self.project_exists:
            log.info(f"Project Id {self.project_id} exists already on specified account.")
            # Update the services it is currently using
            self.services_enabled = self.get_enabled_services()
        else:
            log.info(f"Project Id {project_id} does not exist on specified account.")

    def set_project_meta_data(self):
        """
        Sets the following metadata for a project:
        - parent_project_name
        - parent_project_id
        - authentication
        - billing_account_id
        :return:
        """
        # Get the config file
        with open(os.getenv("GCP_AUTOMATION_CONFIG")) as f:
            config_info = json.load(f)
        # Set all the settings
        self.parent_project_id = config_info['Config'][0]['ParentProjectId']
        self.parent_project_type = config_info['Config'][0]['ParentProjectType']
        self.billing_account_id = config_info['Config'][0]['BillingAccountId']
        log.info(f"Meta info fields parent_project_id, parent_project_name, billing_account_id set for "
                 f"{self.project_id}")

    def find_project(self):
        """
        Gets the details on the current project
        :return: True or false depending on discovery
        """
        try:
            project = self.cloud_service.projects().get(projectId=self.project_id).execute()
            if project is not None:
                # print(f"Project {self.project_id} exists on GCP and the service account has access")
                return project
            else:
                log.debug(f"Project Id {self.project_id} does not exist on google cloud")
        except googleapiclient.errors.HttpError as e:
            if e.status_code == 403:
                log.debug(f"Project Id {self.project_id} not found in project_object.find_project() function"
                     f". If this was expected behaviour continue")
            return False
        except Exception as e:
            log.error(f"find_project in project_object class returned an error: {e}")
            return e

    def does_project_exist(self):
        """
        Checks if a current project already exists
        :return: True or False. If true, updates parent details of object
        """
        # Try to find the project using the find_project method
        project_exists = self.find_project()
        # Branch based upon logic
        if project_exists is False:
            log.info(f"Project Id {self.project_id} returned not found")
            self.project_exists = False
            return False
        else:
            self.project_exists = True
            return True

    def create_new_project(self):
        """
        Creates a new project with the parent defined by the user. Specification of the parent accounts is required
        per GCP documentation:
        :parent_type: defines the type of parent. If left blank, is set to the default values project name
        :parent_id: defines the id of the parent. If left blank, is set to the default values provided
        :return: new project
        """
        # If project does not exist, create a new one
        if not self.project_exists:
            # Create the request
            body = {
                "projectId": self.project_id,
                "name": self.project_name,
                "parent": {
                    "type": self.parent_project_type,
                    "id": self.parent_project_id
                }
            }
            log.debug(f"Body of project creation API request: {body} ")
            try:
                #
                request = self.cloud_service.projects().create(
                    body=body
                )
                response = request.execute()
                log.debug(f"Response to project creation: {response}")
                log.info(f"Project create API call POST with the following details:"
                         f"Project ID: {self.project_id}, Project Name: {self.project_name}, "
                         f"Parent Type: {self.parent_project_type}, Parent ID: {self.parent_project_id}")
            except Exception as e:
                log.error(e)
                return False

            # If no errors are thrown, start checking for new project to become available.
            project_exists = False
            while project_exists is False:
                # Wait for 2 seconds
                time.sleep(2)
                # Check if project exists
                project_exists = self.does_project_exist()

            # Confirm that the project now exists
            project_created = self.does_project_exist()
            if project_created:
                # Update self.project_exists
                log.info(f"Project Id {self.project_id} created")
                # Update the class attribute
                self.project_exists = True
                return True
            else:
                log.warning(f"Project ID {self.project_id} was not created")
                return False
        else:
            log.warning(f"Project ID {self.project_id} already exists. Setting created to True")
            self.project_exists = True
            return True

    def get_enabled_services(self):
        """
        Gets the services currently enabled on a project
        :return:
        """
        # Construct the query to list enabled services
        # Reference: https://cloud.google.com/service-usage/docs/reference/rest/v1/services/list
        # Great StackOverflow post: https://stackoverflow.com/questions/57526808/how-do-you-enable-gcp-apis-through-the-python-client-library
        project = f"projects/{self.project_id}"
        service = googleapiclient.discovery.build('serviceusage', 'v1', credentials=self.credentials)
        # Construct the query
        request = service.services().list(parent=project, pageSize=200, filter="state:ENABLED")
        # Execute the query
        try:
            response = request.execute()
        except Exception as e:
            print(e)
            exit(1)

        # Confirm all the results have been gathered
        if 'nextPageToken' in response:
            page_token = response['nextPageToken']
            # This means there are more. Google has ~700 items at time of writing
            for x in range(6):
                print("Paginated response, collecting more")
                request = service.services().list(parent=self.project_id, pageSize=200, filter="state:ENABLED",
                                                  pageToken=page_token)
                try:
                    pageResponse = request.execute()
                except Exception as e:
                    print(e)
                    exit(1)

                # Update the list of services
                response['services'].append(pageResponse['services'])

                # Set the next page token
                if 'nextPageToken' in response:
                    page_token = pageResponse['nextPageToken']
                else:
                    x = 6
        # If no services have been enabled, set to empty string
        if response == {}:
            response = None

        # Return the enabled services
        return response

    def enable_new_api(self, api_or_service):
        """
        This function enables services to be added to a project programmatically
        Reference: https://cloud.google.com/service-usage/docs/reference/rest/v1/services/enable
        :param api_or_service:
        :return:
        # todo: create a bulk enable new api
        """
        # Construct the search string
        api_or_service = f"{api_or_service}.googleapis.com"
        api_enabled = False
        # Check if the service is already enabled (skip if no service enabled
        if self.services_enabled is not None:
            for services in self.services_enabled['services']:
                if api_or_service in services['config']['name']:
                    api_enabled = True
                    return api_enabled

        # If API not found, enable the service
        service = googleapiclient.discovery.build('serviceusage', 'v1', credentials=self.credentials)
        # Construct the query
        service_name = f"projects/{self.project_id}/services/{api_or_service}"
        request = service.services().enable(name=service_name)
        # Execute the query
        try:
            response = request.execute()
            log.debug(f"API {api_or_service} enabled. Response: {response}")
            # Update self.services available
            self.services_enabled = self.get_enabled_services()
        except Exception as e:
            log.error(e)

    def enable_project_billing(self):
        """
        Sets up a new project if selected
        :return: True
        """
        #todo: test if Billing API is enabled, if not, enable

        # Construct the billing body for api
        # Reference:
        # https://stackoverflow.com/questions/53841940/cant-enable-billing-for-a-fresh-google-cloud-platform-project-in-python-api
        log.info(f"Setting up Billing Account Id API Call in project_object.enable_project_billing(). "
                 f"Check config for Billing Account Id")
        billing_id = self.billing_account_id
        project = f"projects/{self.project_id}"
        billing_body = {
            "name": f"projects/{self.project_id}/billingInfo",
            "projectId": self.project_id,
            "billingEnabled": True,
            "billingAccountName": f"billingAccounts/{billing_id}"
        }

        log.info(f"Setting up billing authentication")
        # Set up the API call
        billing_api = googleapiclient.discovery.build("cloudbilling", "v1", credentials=self.credentials)
        billing_enable = billing_api.projects().updateBillingInfo(name=project, body=billing_body)
        # Execute billing
        try:
            billing_execute = billing_enable.execute()
            log.info(f"Billing enabled. Details {billing_execute}")
            return True
        except Exception as e:
            log.error(e)
            return False

    def get_project_billing_info(self):
        """
        Gets the billing info for a project
        Reference: https://cloud.google.com/billing/docs/reference/rest/v1/projects/getBillingInfo
        :return: Project Billing Info
        """
        # Construct the project string
        project = f"projects/{self.project_id}"
        # Build the REST API call
        billing_api = googleapiclient.discovery.build("cloudbilling", "v1", credentials=self.credentials)
        billing_enable = billing_api.projects().getBillingInfo(name=project)
        # Execute the REST API call
        try:
            billing_execute = billing_enable.execute()
        except Exception as e:
            print(e)

    def human_readable_apis_enabled(self):
        """
        returns a human readable list of API's currently enabled
        :return: list of API's currently enabled
        """
        # Pretty Print a list of the services and status to the screen
        # Set pretty print to indent of 4
        pp = pprint.PrettyPrinter(indent=4)
        # Filter so that only name and status print
        human_readable = {
            'servicelist': []
        }

        # New projects start with no services available, so test for 'None'
        if self.services_enabled is None:
            human_readable['servicelist'] = None
        else:
            # If services are available, format them into an easier list
            # todo: turn this into a pandas dataframe?
            for service in self.services_enabled['services']:
                service_output = {
                    "API_Name": service['config']['title'],
                    "Status": service['state']
                }
                human_readable['servicelist'].append(service_output)

        print(pp.pprint(human_readable['servicelist']))
        # return human_readable

    def disable_api(self, api_or_service):
        """
        Disable or remove an API from the specified service
        :param api_or_service:
        :return:
        """
        # Check if the service is actually enabled
        # If it is, disable it
        # Update self.services available
