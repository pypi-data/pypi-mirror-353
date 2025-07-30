import requests

def create_asana_task(personal_access_token, project_id, task_name, notes=None, assignee=None):
    """
    Create a task in Asana.

    Args:
        personal_access_token (str): Your Asana personal access token.
        project_id (str): The ID of the Asana project.
        task_name (str): The name of the task.
        notes (str, optional): Description/notes for the task.
        assignee (str, optional): Email of the assignee.

    Returns:
        dict: JSON response from Asana API.
    """
    url = "https://app.asana.com/api/1.0/tasks"
    headers = {
        "Authorization": f"Bearer {personal_access_token}"
    }
    data = {
        "name": task_name,
        "projects": [project_id]
    }
    if notes:
        data["notes"] = notes
    if assignee:
        data["assignee"] = assignee

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
