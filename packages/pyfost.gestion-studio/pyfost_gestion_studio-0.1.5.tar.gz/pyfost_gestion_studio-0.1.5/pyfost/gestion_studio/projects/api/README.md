# Projects API

Use this to manage Projets, Users and Tasks from python

## Todo
- Implement more 

## Usage

```python

from pyfost.gestion_studio.projects.api import ProjectsAPI, models

api_url = "http://127.0.0.1:8002" # Use your real url here.
project_api = ProjectsAPI(url=api_url)

async def do_something():
    projects = await project_api.get_projects()
    return len(projects)

```
