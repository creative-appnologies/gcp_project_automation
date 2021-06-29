import gcpprojectautomation.manifest
import gcpprojectautomation.manifest_list
from gcpprojectautomation import project_object
from gcpprojectautomation import helpers
from gcpprojectautomation import iam_object
import logging as log
import random
import string
import pprint


def new_project(project_id="auto", project_name="auto", project_manifest="django-auto"):
    """
    Sets a new project. Will auto create a name unless selected otherwise
    :param project_manifest: Manifest for the project type
    :param project_name: string of new name
    :param project_id: string of new id.
    :return: returns project
    """
    # Check project_id for regex. If project_id set to 'auto', generate a 16 char string
    id_works = False
    while id_works is not True:
        # If set to auto, first generate a random 16 char string
        if project_id == "auto":
            # Generate random 16 character string
            project_id = ''.join(random.choice(string.ascii_lowercase) for i in range(16))
            log.info("Project Id auto selected")
        # Check id doesn't violate any known issues
        check_name = helpers.check_project_id(project_id)
        if check_name['outcome'] is True:
            # Regex check passed
            log.info(f"Project Id {project_id} selected as id for new project")
            id_works = True
        else:
            if project_id != "auto":
                # User needs to retry a different name
                project_id = input(f"Proposed Project Id {project_id} did not pass regex check, "
                                   f"please try again: ")

    # If project_name set to 'auto', set to be the same as the project_id
    if project_name == "auto":
        # Set to be the same as project_id
        project_name = project_id

    log.info(f"Project Name set to {project_name}")

    # Init new manifest object
    log.info(f"Project manifest for {project_manifest} requested")
    manifest = gcpprojectautomation.manifest.Manifest(project_manifest)

    # Get the service name to be used for project work
    service_account_name = helpers.get_service_account_name()
    log.debug(f"Service account used for project creation is {service_account_name}")

    if manifest != "DoesNotExist":
        log.info(f"Project Manifest loaded for Project Id: {project_id}, Project Type: {project_manifest}")
        # Init new project object
        project = project_object.GCPProject(project_id=project_id, project_name=project_name,
                                            project_manifest=project_manifest)
        # If the project already exists, no requirement to create, just update
        if project.project_exists is True:
            log.info(f"Project Id {project_id} already exists. Updating with manifest details")
            project_created = True
        else:
            # Create the project
            project_created = project.create_new_project()

        # Once project is created, Assign billing
        if project_created is True:
            log.info(f"Project {project_id} created in project.new_project file")
            # Enable billing
            project_billing = project.enable_project_billing()
            if project_billing is True:
                log.info(f"Project {project_id} billing enabled in project.new_project file")
                # Enable the API's from the manifest
                for api in manifest.apis_required:
                    project.enable_new_api(api['API_Name'])
                apis_enabled = True
                return apis_enabled
            else:
                log.critical(f"Error enabling billing on {project_id}")
        else:
            log.critical(f"Error creating project {project_id}")
    else:
        log.critical(f"Manifest type {project_manifest} does not exist. Choose a different manifest type and try again")
        raise ValueError("ManifestType does not exist")

#todo: Get project types
def list_project_types():
    """
    Gets a list of the projects available and their names
    :return:
    """
    # Get the list of manifests
    manifests = gcpprojectautomation.manifest_list.ManifestLists().list_manifests()

    # Prettify the display
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(manifests)

    return manifests

