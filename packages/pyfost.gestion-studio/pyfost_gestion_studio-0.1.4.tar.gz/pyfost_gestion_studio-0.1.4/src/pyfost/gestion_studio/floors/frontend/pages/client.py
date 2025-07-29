from ...api import FloorsAPI, models

FLOORS_API_CLIENT = None


def init_floors_client(api_host, api_port):
    global FLOORS_API_CLIENT
    FLOORS_API_CLIENT = FloorsAPI(host=api_host, port=api_port)


def get_floors_client() -> FloorsAPI:
    assert FLOORS_API_CLIENT is not None  # Initialized by mount_pages()
    return FLOORS_API_CLIENT
