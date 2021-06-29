import googleapiclient.discovery
from gcpprojectautomation import helpers
import logging as log
import googleapiclient.errors


class IAM(object):
    def __init__(self):
        self.credentials = helpers.get_credentials()

class ProjectIAM(IAM):
    def __init__(self, project_id, project_type):
        super().__init__()
        self.project_id = project_id
        self.project_type = project_type
        self.cloud_service = googleapiclient.discovery.build("cloudresourcemanager", "v1", credentials=self.credentials)
        self.service_account_auth = googleapiclient.discovery.build('iam', 'v1', credentials=self.credentials)
        self.current_policy = self.get_current_policy()
        self.service_account_list = self.list_service_accounts()

    def get_current_policy(self):
        """
        Gets the current IAM Policy for a project
        :param project_id: Project_ID being searched
        :param version: version be searched for
        :return: a dict of the current policies
        """
        policy = (
            self.cloud_service.projects()
            .getIamPolicy(
                resource=self.project_id,
                body={"options": {"requestedPolicyVersion": 3}},
            )
            .execute()
        )
        self.current_policy = policy
        return policy

    def list_service_accounts(self):
        """
        Gets a list of the current service accounts on the project
        :return: service_account_list
        """
        # Construct query object
        accounts = f"projects/{self.project_id}"
        log.info(f"Query for listing service accounts constructed: {accounts}")

        # Execute the query
        try:
            service_accounts = self.service_account_auth.projects().serviceAccounts().list(name=accounts).execute()
            return service_accounts
        except Exception as e:
            log.error(e)

    def add_iam_role(self, role):
        """
        Adds an IAM role to a policy
        :param role:
        :return:
        """
        # Confirm that the current role does not already exist
        for roles in self.current_policy['bindings']:
            # Split based upon "/" to extract name of the role
            role_name = str(roles['role']).split("/")[1]
            if role_name == role:
                print(f"IAM {role} on {self.project_id} already exists")
                return False
        # If for loop completes, this means that role doesn't exist.
        # Get the current policy
        policy = self.current_policy
        # Add the new role. Make sure the string being appended matches expected format
        policy_string = 'roles/' + role
        policy["bindings"].append(policy_string)
        # Submit the role to be updated
        updated_policy = self.set_iam_policy(policy)
        print(f"IAM role {role} added to {self.project_id}")
        return updated_policy

    def remove_iam_role(self, role):
        """
        Removes an iam role from a policy
        :param role:
        :return:
        """
        # Confirm that the current role exists
        for roles in self.current_policy['bindings']:
            # Split based upon "/" to extract name of the role
            role_name = str(roles['role']).split("/")[1]
            if role_name == role:
                # Remove role from policy
                policy = self.current_policy
                policy = policy['bindings'].remove(roles)
                # Submit update policy to be updated
                updated_policy = self.set_iam_policy(policy)
                print(f"IAM role {role} removed from {self.project_id}")
                return updated_policy
        # If loop completes without exiting, this means that role doesn't exist on this project
        print(f"IAM {role} on {self.project_id} is not applied to this project")
        return False


    def set_iam_policy(self, policy):
        """
        Takes the policy object and submits it to GCP.
        :param policy: object which defines the policy object for the project_id
        :return: updates policy on project
        """
        # Take the provided policy object and submit to GCP
        policy = (
            self.cloud_service.projects()
            .getIamPolicy(
                resource=self.project_id,
                body={"policy": policy}
            )
            .execute()
        )
        # Update the current policy for the object
        self.current_policy = self.get_current_policy()
        return self.current_policy


    def change_project_id(self, new_project_id):
        """
        Updated the project being captured by this class
        :param new_project_id: the project id to be updated
        :return: updates the class with a new project
        """

    def __str__(self):
        return self.project_id


class AccountIAM(IAM):
    def __init__(self, account_name, project_id, account_type="service"):
        IAM.__init__(self)
        self.project_id = project_id
        self.account_name = account_name
        self.account_type = account_type
        self.service_account_auth = googleapiclient.discovery.build('iam', 'v1', credentials=self.credentials)
        self.account_exists = self.check_account_exists()
        if self.account_exists:
            self.current_policy = self.get_current_policy()
        else:
            self.current_policy = None

    def get_current_policy(self):
        """
        Gets the current IAM Policy for the account
        :return: a dict of the current policies
        """

        # Set up the query
        resource = f"projects/{self.project_id}/serviceAccounts/{self.account_name}"
        log.info(f"Requesting IAM information for {resource}")
        # Execute the query
        try:
            service_account = self.service_account_auth.projects().serviceAccounts().getIamPolicy(
                resource=resource).execute()
            log.debug(f"IAM details for {self.account_name} on project {self.project_id} gathered")
            return service_account
        except Exception as e:
            log.error(f"Error getting current policy: {e}")

    def check_account_exists(self):
        """
        Checks that the specified user account exists
        :return: True or False
        """
        if self.account_type == "service":
            # Set up the query
            resource = f"projects/-/serviceAccounts/{self.account_name}"
            log.info(f"Requesting IAM information for {resource}")
            # Execute the query
            try:
                service_account = self.service_account_auth.projects().serviceAccounts().get(
                    name=resource).execute()
                log.info(f"Account {self.account_name} found")
                return True
            except googleapiclient.errors.HttpError as e:
                log.warning(f"Account {self.account_name} not found")
                return False
            except Exception as e:
                log.error(f"Error checking if account exists: {e}")
                return False
