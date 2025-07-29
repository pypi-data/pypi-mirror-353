# isort: skip_file

import json
import logging
import time
from typing import Any

import numpy as np
import requests

from android_world.env import json_action  # type: ignore
from pydantic import BaseModel
from screensuite.agents.remote_env import create_remote_env_provider
from screensuite.agents.remote_env.docker.provider import DockerProviderConfig

logger = logging.getLogger()
logger.setLevel(logging.INFO)

Params = dict[str, int | str]


class Response(BaseModel):
    status: str
    message: str


class AndroidEnvClient:
    """Client for interacting with the Android environment server"""

    def __init__(self):
        logger.info("Setting up Android environment using Docker - Initial setup may take 5-10 minutes. Please wait...")
        self.provider = create_remote_env_provider(
            config=DockerProviderConfig(
                ports_to_forward={5000},
                image="huggingface/android_world:latest",
                healthcheck_endpoint="/health",
                healthcheck_port=5000,
                privileged=True,
            )
        )
        self.provider.start_emulator()
        ip_addr = self.provider.get_ip_address()
        self.base_url = f"http://{ip_addr.ip_address}:{ip_addr.host_port[5000]}"

    def reset(self, go_home: bool) -> Response:
        """Reset the environment"""
        response = requests.post(f"{self.base_url}/reset", params={"go_home": go_home})
        response.raise_for_status()
        return Response(**response.json())

    def get_screenshot(self, wait_to_stabilize: bool = False) -> np.ndarray[Any, Any]:
        """Get the current screenshot of the environment"""
        response = requests.get(f"{self.base_url}/screenshot", params={"wait_to_stabilize": wait_to_stabilize})
        response.raise_for_status()
        image = response.json()
        # Convert pixels list back to numpy array
        screenshot = np.array(image["pixels"]).astype(np.uint8)
        return screenshot

    def execute_action(
        self,
        action: json_action.JSONAction,
    ) -> Response:
        """Execute an action in the environment"""
        print(f"Executing action: {action.json_str()}")
        response = requests.post(f"{self.base_url}/execute_action", json=json.loads(action.json_str()))
        response.raise_for_status()
        return Response(**response.json())

    def get_suite_task_list(self, max_index: int) -> list[str]:
        """Get the list of tasks in the suite"""
        response = requests.get(f"{self.base_url}/suite/task_list", params={"max_index": max_index})
        response.raise_for_status()
        return response.json()["task_list"]

    def get_suite_task_length(self, task_type: str) -> int:
        """Get the length of the suite of tasks"""
        response = requests.get(f"{self.base_url}/suite/task_length", params={"task_type": task_type})
        response.raise_for_status()
        return response.json()["length"]

    def reinitialize_suite(
        self,
        n_task_combinations: int = 2,  # Default from initial server lifespan setup
        seed: int = 42,  # Default from initial server lifespan setup
        task_family: str = "android_world",  # Default from initial server lifespan setup
    ) -> Response:
        """Reinitialize the suite of tasks"""
        params: Params = {
            "n_task_combinations": n_task_combinations,
            "seed": seed,
            "task_family": task_family,
        }
        response = requests.get(f"{self.base_url}/suite/reinitialize", params=params)
        response.raise_for_status()
        return Response(**response.json())

    def initialize_task(self, task_type: str, task_idx: int) -> Response:
        """Initialize the task in the environment"""
        params: Params = {"task_type": task_type, "task_idx": task_idx}
        response = requests.post(f"{self.base_url}/task/initialize", params=params)
        response.raise_for_status()
        return Response(**response.json())

    def start_on_home_screen(self, task_type: str, task_idx: int) -> bool:
        """Start the task on the home screen"""
        params: Params = {"task_type": task_type, "task_idx": task_idx}
        response = requests.post(f"{self.base_url}/task/start_on_home_screen", params=params)
        response.raise_for_status()
        return response.json()["start_on_home_screen"]

    def get_task_complexity(self, task_type: str, task_idx: int) -> int:
        """Get the complexity of the current task"""
        params: Params = {"task_type": task_type, "task_idx": task_idx}
        response = requests.post(f"{self.base_url}/task/complexity", params=params)
        response.raise_for_status()
        return response.json()["complexity"]

    def tear_down_task(self, task_type: str, task_idx: int) -> Response:
        """Tear down the task in the environment"""
        params: Params = {"task_type": task_type, "task_idx": task_idx}
        response = requests.post(f"{self.base_url}/task/tear_down", params=params)
        response.raise_for_status()
        return Response(**response.json())

    def get_task_score(self, task_type: str, task_idx: int) -> float:
        """Get the score of the current task"""
        params: Params = {"task_type": task_type, "task_idx": task_idx}
        response = requests.get(f"{self.base_url}/task/score", params=params)
        response.raise_for_status()
        return response.json()["score"]

    def get_task_goal(self, task_type: str, task_idx: int) -> str:
        """Get the goal of the current task"""
        params: Params = {"task_type": task_type, "task_idx": task_idx}
        response = requests.get(f"{self.base_url}/task/goal", params=params)
        response.raise_for_status()
        return response.json()["goal"]

    def get_task_template(self, task_type: str, task_idx: int) -> str:
        """Get the template of the current task"""
        params: Params = {"task_type": task_type, "task_idx": task_idx}
        response = requests.get(f"{self.base_url}/task/template", params=params)
        response.raise_for_status()
        return response.json()["template"]

    def is_miniwob_epidode_terminated(self) -> bool:
        """Check if the episode is terminated"""
        response = requests.get(f"{self.base_url}/task/miniwob/is_epidode_terminated")
        response.raise_for_status()
        return response.json()["is_epidode_terminated"]

    def close(self) -> None:
        """Close the environment"""
        try:
            response = requests.post(f"{self.base_url}/close")
            response.raise_for_status()
        finally:
            self.provider.stop_emulator()

    def health(self) -> bool:
        """Check the health of the environment"""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
        except Exception as e:
            print(f"Environment is not healthy: {e}")
            return False
        return True


# Example usage:
if __name__ == "__main__":
    from PIL import Image

    client = AndroidEnvClient()

    while True:
        if not client.health():
            print("Environment is not healthy, waiting for 1 second...")
            time.sleep(1)
        else:
            break

    res = client.reset(go_home=True)
    print(f"reset response: {res}")

    screenshot = client.get_screenshot()
    print("Screen dimensions:", screenshot.shape)
    Image.fromarray(screenshot).save("screenshot.png")

    res = client.execute_action(json_action.JSONAction(action_type="click", x=100, y=200))
    print(f"execute_action response: {res}")

    task_list = client.get_suite_task_list(max_index=-1)
    print(task_list)

    res = client.reinitialize_suite()
    print(f"reinitialize_suite response: {res}")

    for task_type in task_list:
        task_length = client.get_suite_task_length(task_type=task_type)
        print(f"task_length: {task_length}")

        for task_idx in range(task_length):
            task_template = client.get_task_template(task_type=task_type, task_idx=task_idx)
            print(f"task_template: {task_template}")

            task_goal = client.get_task_goal(task_type=task_type, task_idx=task_idx)
            print(f"task_goal: {task_goal}")

            try:
                res = client.initialize_task(task_type=task_type, task_idx=task_idx)
                print(f"initialize_task response: {res}")

                # Complete the task using your agent...

                task_score = client.get_task_score(task_type=task_type, task_idx=task_idx)
                print(f"task_score: {task_score}")

                res = client.tear_down_task(task_type=task_type, task_idx=task_idx)
                print(f"tear_down_task response: {res}")

            except Exception as e:
                # Error tasks:
                # RetroPlayingQueue -> sqlite3.OperationalError: no such table: playing_queue
                # SimpleSmsReplyMostRecent -> IndexError: list index out of range
                print(f"Error initializing task {task_type} {task_idx}: {e}")
                print("Continuing to next task...")
                continue

            res = client.reset(go_home=True)
            print(f"reset response: {res}")

    client.close()
