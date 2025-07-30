
import questionary
from pathlib import Path
import shutil
import os

def run_init():
    project_name = questionary.text("Project name:").ask()
    directory = questionary.path("Directory to create the project in:").ask()
    project_type = questionary.select(
        "What type of project do you want?",
        choices=["frontend", "backend", "full_stack"]
    ).ask()

    tech_stack = None
    if project_type == "frontend":
        tech_stack = questionary.select(
            "Choose frontend tech stack:",
            choices=["react", "vite", "vue"]
        ).ask()
        if tech_stack == "vite":
            language = questionary.select(
                "choose: ",
                choices=["javascript", "typescript"]
            ).ask()
        elif tech_stack == "vue":
            language = questionary.select(
                "choose: ",
                choices=["Javascript", "typescript"]
            ).ask()
        elif tech_stack == "react":
            language = questionary.select(
                "",
                choices=["javascript"]
            ).ask()

    elif project_type == "backend":
        tech_stack = questionary.select(
            "Choose backend tech stack:",
            choices=[
                "node",
                "django",
                "fastapi",
                "flask",
                "spring-boot",
            ]
    ).ask()
    elif project_type == "full_stack":
        tech_stack = questionary.select(
            "Choose full-stack tech stack:",
            choices=[
                "react+node",
                "react+django",
                "react+fastapi",
                "next.js",
                "vue+flask"
            ]
        ).ask()

    author = questionary.text("Author:").ask()
    project_path = Path(directory) / project_name
    project_path.mkdir(parents=True, exist_ok=True)

    # for the template path

    root_directory = Path(__file__).parent.parent
    if project_type == "frontend":
        template_path = root_directory/"templates"/project_type/tech_stack/language
    elif project_type == "backend":
        template_path = root_directory/"templates"/project_type/tech_stack
    elif project_type == "full_stack":
        template_path = root_directory/"templates"/project_type/tech_stack

    if template_path.exists():
        shutil.copytree(template_path, project_path, dirs_exist_ok=True)


    print(f"Project '{project_name}' created at {project_path}")
    print(f"Tech stack: {tech_stack}")
    print(f"Author: {author}")
