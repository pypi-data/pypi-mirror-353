import argparse
import logging
import os
import time
import unicodedata
from io import BytesIO
from typing import Any, Literal

import numpy as np

# SmolaAgents imports
# Qwen2.5VL imports
# E2B imports
from PIL import Image
from smolagents import HfApiModel, Model, Tool, tool
from smolagents.monitoring import LogLevel

from screensuite.agents.client.desktop_env_client import (
    DesktopEnvClient,
    ExecuteResponse,
)

from ..prompt import E2B_SYSTEM_PROMPT_TEMPLATE
from .base_vision_agent import VisionAgent

logger = logging.getLogger()


def get_agent_summary_erase_images(agent):
    for memory_step in agent.memory.steps:
        if hasattr(memory_step, "observations_images"):
            memory_step.observations_images = None
        if hasattr(memory_step, "task_images"):
            memory_step.task_images = None
    return agent.write_memory_to_messages()


class DesktopAgent(VisionAgent):
    """Agent for e2b desktop automation"""

    def __init__(
        self,
        model: Model,
        data_dir: str,
        tools: list[Tool] | None = None,
        max_steps: int = 200,
        verbosity_level: LogLevel = LogLevel.INFO,
        planning_interval: int | None = None,
        use_v1_prompt: bool = False,
        **kwargs,
    ):
        logger.info("Initializing Desktop sandbox...")
        self.env = DesktopEnvClient()
        screen_size = self.env.get_screen_size()
        if screen_size is None:
            raise ValueError("Failed to get screen size")
        self.width, self.height = screen_size["width"], screen_size["height"]
        print(f"Screen size: {self.width}x{self.height}")

        self.use_v1_prompt = use_v1_prompt

        # Initialize base agent
        super().__init__(
            model=model,
            data_dir=data_dir,
            tools=tools,
            max_steps=max_steps,
            verbosity_level=verbosity_level,
            planning_interval=planning_interval,
            **kwargs,
        )

        self.prompt_templates["system_prompt"] = E2B_SYSTEM_PROMPT_TEMPLATE.replace(
            "<<resolution_x>>", str(self.width)
        ).replace("<<resolution_y>>", str(self.height))

        # Add screen info to state
        self.state["screen_width"] = self.width
        self.state["screen_height"] = self.height

    def _setup_desktop_tools(self):
        """Register all desktop tools"""

        @tool
        def click(x: int, y: int) -> str:
            """
            Performs a left-click at the specified coordinates
            Args:
                x: The x coordinate (horizontal position)
                y: The y coordinate (vertical position)
            """
            self.env.move_mouse(x, y)
            self.env.left_click()
            self.click_coordinates = [x, y]
            self.logger.log(f"Clicked at coordinates ({x}, {y})")
            return f"Clicked at coordinates ({x}, {y})"

        @tool
        def right_click(x: int, y: int) -> str:
            """
            Performs a right-click at the specified coordinates
            Args:
                x: The x coordinate (horizontal position)
                y: The y coordinate (vertical position)
            """
            self.env.move_mouse(x, y)
            self.env.right_click()
            self.click_coordinates = [x, y]
            self.logger.log(f"Right-clicked at coordinates ({x}, {y})")
            return f"Right-clicked at coordinates ({x}, {y})"

        @tool
        def double_click(x: int, y: int) -> str:
            """
            Performs a double-click at the specified coordinates
            Args:
                x: The x coordinate (horizontal position)
                y: The y coordinate (vertical position)
            """
            self.env.move_mouse(x, y)
            self.env.double_click()
            self.click_coordinates = [x, y]
            self.logger.log(f"Double-clicked at coordinates ({x}, {y})")
            return f"Double-clicked at coordinates ({x}, {y})"

        @tool
        def move_mouse(x: int, y: int) -> str:
            """
            Moves the mouse cursor to the specified coordinates
            Args:
                x: The x coordinate (horizontal position)
                y: The y coordinate (vertical position)
            """
            self.env.move_mouse(x, y)
            self.logger.log(f"Moved mouse to coordinates ({x}, {y})")
            return f"Moved mouse to coordinates ({x}, {y})"

        def normalize_text(text):
            return "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))

        @tool
        def type_text(text: str) -> str:
            """
            Types the specified text at the current cursor position.
            Args:
                text: The text to type
            """
            clean_text = normalize_text(text)
            self.env.write(clean_text, delay_in_ms=75)
            self.logger.log(f"Typed text: '{clean_text}'")
            return f"Typed text: '{clean_text}'"

        @tool
        def press_key(key: str) -> str:
            """
            Presses a keyboard key
            Args:
                key: The key to press (e.g. "enter", "space", "backspace", etc.).
            """
            self.env.press(key)
            self.logger.log(f"Pressed key: {key}")
            return f"Pressed key: {key}"

        @tool
        def go_back() -> str:
            """
            Goes back to the previous page in the browser. If using this tool doesn't work, just click the button directly.
            Args:
            """
            self.env.press("altleft")
            self.logger.log("Went back one page")
            return "Went back one page"

        @tool
        def drag_and_drop(x1: int, y1: int, x2: int, y2: int) -> str:
            """
            Clicks [x1, y1], drags mouse to [x2, y2], then release click.
            Args:
                x1: origin x coordinate
                y1: origin y coordinate
                x2: end x coordinate
                y2: end y coordinate
            """
            self.env.drag((x1, y1), (x2, y2))
            message = f"Dragged and dropped from [{x1}, {y1}] to [{x2}, {y2}]"
            self.logger.log(message)
            return message

        @tool
        def scroll(x: int, y: int, direction: Literal["up", "down"] = "down", amount: int = 2) -> str:
            """
            Moves the mouse to selected coordinates, then uses the scroll button: this could scroll the page or zoom, depending on the app. DO NOT use scroll to move through linux desktop menus.
            Args:
                x: The x coordinate (horizontal position) of the element to scroll/zoom
                y: The y coordinate (vertical position) of the element to scroll/zoom
                direction: The direction to scroll ("up" or "down"), defaults to "down". For zoom, "up" zooms in, "down" zooms out.
                amount: The amount to scroll. A good amount is 1 or 2.
            """
            self.env.move_mouse(x, y)
            self.env.scroll(x=x, y=y, direction=direction, amount=amount)
            message = f"Scrolled {direction} by {amount}"
            self.logger.log(message)
            return message

        @tool
        def wait(seconds: float) -> str:
            """
            Waits for the specified number of seconds. Very useful in case the prior order is still executing (for example starting very heavy applications like browsers or office apps)
            Args:
                seconds: Number of seconds to wait, generally 3 is enough.
            """
            time.sleep(seconds)
            self.logger.log(f"Waited for {seconds} seconds")
            return f"Waited for {seconds} seconds"

        @tool
        def open_url(url: str) -> str:
            """
            Directly opens a browser with the specified url: use this at start of web searches rather than trying to click the browser.
            Args:
                url: The URL to open
            """
            # Make sure URL has http/https prefix
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            self.env.open(url)
            # Give it time to load
            time.sleep(2)
            self.logger.log(f"Opening URL: {url}")
            return f"Opened URL: {url}"

        @tool
        def find_on_page_ctrl_f(search_string: str) -> str:
            """
            Scroll the browser viewport to the first occurrence of the search string. This is equivalent to Ctrl+F. Use this to search on a pdf for instance.
            Args:
                search_string: The string to search for on the page.
            """
            self.env.press(["ctrl", "f"])
            time.sleep(0.3)
            clean_text = normalize_text(search_string)
            self.env.write(clean_text, delay_in_ms=75)
            time.sleep(0.3)
            self.env.press("enter")
            time.sleep(0.3)
            self.env.press("esc")
            output_message = f"Scrolled to the first occurrence of '{clean_text}'"
            self.logger.log(output_message)
            return output_message

        # Register the tools
        self.tools["click"] = click
        self.tools["right_click"] = right_click
        self.tools["double_click"] = double_click
        self.tools["move_mouse"] = move_mouse
        self.tools["type_text"] = type_text
        self.tools["press_key"] = press_key
        self.tools["scroll"] = scroll
        self.tools["wait"] = wait
        self.tools["open_url"] = open_url
        self.tools["go_back"] = go_back
        self.tools["drag_and_drop"] = drag_and_drop
        self.tools["find_on_page_ctrl_f"] = find_on_page_ctrl_f

    def get_screenshot(self) -> np.ndarray[Any, Any]:
        """Get a screenshot from the E2B environment."""
        time.sleep(2.5)  # Let things happen on the desktop
        screenshot_bytes = self.env.screenshot()
        if screenshot_bytes is None:
            raise ValueError("Failed to get screenshot")
        image = Image.open(BytesIO(screenshot_bytes))
        return np.array(image)

    def run_arbitrary_command(self, command: str) -> str:
        """Run an arbitrary command on the desktop"""
        execution = self.env.execute_shell_command(command)
        if isinstance(execution, ExecuteResponse):
            response = execution.output + (("\n" + str(execution.error)) if execution.error else "")
        else:
            raise ValueError(f"Unexpected execution response: {execution}")
        return response

    def close(self):
        """Clean up resources"""
        if self.env:
            # self.env.stream.stop()
            self.env.kill()
            logger.info("Desktop sandbox terminated")


def main():
    """Run the E2B Vision Agent"""
    parser = argparse.ArgumentParser(description="Run the E2B Vision Agent")
    parser.add_argument("task", help="The task to perform on the desktop")
    parser.add_argument("--api-key", default=os.environ.get("E2B_API_KEY"), help="E2B API key")
    parser.add_argument("--resolution", default="1024,768", help="Screen resolution (width,height)")
    parser.add_argument("--model-path", default="Qwen/Qwen2.5-VL-3B-Instruct", help="Path to Qwen2.5VL model")
    parser.add_argument("--output-dir", default="e2b_qwen_screenshots", help="Output directory for screenshots")
    args = parser.parse_args()

    if not args.api_key:
        raise ValueError("E2B API key not provided. Set E2B_API_KEY environment variable or use --api-key")

    width, height = map(int, args.resolution.split(","))

    # Initialize model
    # model = QwenVLModel(model_path=args.model_path)

    model = HfApiModel("Qwen/Qwen2.5-VL-72B-Instruct", provider="hyperbolic")

    # Initialize agent
    agent = DesktopAgent(
        model=model,
        data_dir="output",
        max_steps=50,
    )

    try:
        # Run the agent
        result = agent.run(args.task)
        print(f"\nTask completed with result: {result}")
    finally:
        # Clean up
        agent.close()


if __name__ == "__main__":
    main()
