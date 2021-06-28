import gcpprojectautomation.manifest
import gcpprojectautomation.manifest_list
from gcpprojectautomation import project_object
from gcpprojectautomation import helpers
import logging as log
import random
import string
import pprint


def new_project(project_name="auto", project_id="auto", project_type="django-auto"):
    """
    Sets a new project. Will auto create a name unless selected otherwise
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

    # If project_name set to 'auto', set to be the same as the proejct_id
    if project_name == "auto":
        # Set to be the same as project_id
        project_name = project_id

    log.info(f"Project Name set to {project_name}")

    # Init new manifest object
    log.info(f"Project Manifest loaded for Project Id: {project_id}, Project Type: {project_type}")
    manifest = gcpprojectautomation.manifest.Manifest(project_type)

    # Init new project

    print(manifest)


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

