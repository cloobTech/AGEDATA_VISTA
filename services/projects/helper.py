from models.project_member import ProjectMember


def instantiate_project_members_with_project_owner(owner, project) -> ProjectMember:
    """Basically, This function will be called when a user creates a new project"""

    project_member = ProjectMember(
        user_id=owner.id, project_id=project.id, role="owner", project=project, user=owner)
    return project_member
