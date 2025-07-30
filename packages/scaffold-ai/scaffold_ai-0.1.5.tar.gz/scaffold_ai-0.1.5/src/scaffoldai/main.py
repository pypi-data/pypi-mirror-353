import os
from openai import OpenAI
import subprocess
import shutil

def main():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    user_goal = input("Enter your project goal: ")
    use_vite = input("Use Vite for the project? (yes/no): ").strip().lower() == "yes"

    def bootstrap_project(project_name: str, template: str = "react"):
        if os.path.exists(project_name):
            shutil.rmtree(project_name)
            print(f"🗑️ Deleted existing folder: {project_name}")
        print(f"🚀 Bootstrapping project: {project_name}")
        if use_vite:
            subprocess.run(
                ["npm", "create", "vite@latest", project_name, "--", "--template", template],
                check=True
            )
        else:
            os.makedirs(project_name, exist_ok=True)
            with open(os.path.join(project_name, "index.html"), "w") as f:
                f.write("")
        print(f"📦 Project created at ./{project_name}")

    def create_file(project_name: str, filename: str, content: str):
        filename = f'{project_name}/{filename}'
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        with open(filename, "w") as f:
            f.write(content)
        print(f"📁 File created: {filename}")

    def read_file(project_name: str, filename: str) -> str:
        with open(f'{project_name}/{filename}', "r") as f:
            return f.read()
        
    def edit_file(project_name: str, filename: str, find: str, replace_with: str) -> str:
        filename = f'{project_name}/{filename}'
        with open(filename, "r") as f:
            content = f.read()

        if find not in content:
            return "⚠️ Pattern not found."

        new_content = content.replace(find, replace_with)

        with open(filename, "w") as f:
            f.write(new_content)

        return "✅ File edited successfully."

    def run_project(project_name: str):
        if use_vite:
            print(f"⚙️ Running Vite project: {project_name}")
            cwd = os.path.abspath(project_name)
            subprocess.run(["npm", "install"], cwd=cwd, check=True)
            print("🚀 Project created. Follow Vite's instructions above to start the project.")
            return
        else:
            print(f"⚙️ Running project: {project_name}")
            cwd = os.path.abspath(project_name)
            subprocess.Popen(
                ["python3", "-m", "http.server", "3000"],
                cwd=cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("🚀 Simple HTTP server started on http://localhost:3000")
            return

    def finish(reason: str):
        print(f"✅ Agent finished: {reason}")

    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "Create a file with the given content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "description": "Name of the project"},
                        "filename": {"type": "string", "description": "Path to the file"},
                        "content": {"type": "string", "description": "Content of the file"},
                    },
                    "required": ["project_name", "filename", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a file",
                "parameters": {
                "type": "object",
                "properties": {
                    "project_name": { "type": "string", "description": "Name of the project" },
                    "filename": { "type": "string" }
                },
                "required": ["project_name", "filename"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "edit_file",
                "description": "Edit an existing file by replacing a specific string with new content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": { "type": "string", "description": "Name of the project" },
                        "filename": { "type": "string" },
                        "find": { "type": "string" },
                        "replace_with": { "type": "string" }
                    },
                    "required": ["project_name", "filename", "find", "replace_with"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_project",
                "description": "Install dependencies and run the Vite project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string"},
                    },
                    "required": ["project_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "finish",
                "description": "Signal that the task is complete",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reason": {"type": "string"}
                    },
                    "required": ["reason"]
                }
            }
        }
    ]

    if use_vite:
        tools.append({
            "type": "function",
            "function": {
                "name": "bootstrap_vite_project",
                "description": "Initialize a new Vite project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string"},
                        "template": {
                            "type": "string",
                            "enum": ["react", "vue", "svelte", "vanilla"],
                            "default": "react",
                            "description": "Template to use for the Vite project"
                        }
                    },
                    "required": ["project_name", "template"]
                }
            }
        })
    else:
        tools.append({
            "type": "function",
            "function": {
                "name": "bootstrap_project",
                "description": "Initialize a new vanilla project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string"}
                    },
                    "required": ["project_name"]
                }
            }
        })

    messages = [
        {"role": "system", "content": f'''
        You are an autonomous developer. 
        Use the '{'bootstrap_vite_project' if use_vite else 'bootstrap_project'}' tool to scaffold the project.
        You may use the 'create_file' tool to add or modify files.
        If you want to change a file and you're unsure what's inside, first call 'read_file' tool.
        Then, plan a minimal change using the 'edit_file' tool. Only use full replacement if absolutely necessary.
        Before finishing, run the project using 'run_project' tool.
        Once you believe all required steps are complete, and the app is running,
            immediately call the finish tool with a final message.
            Do not repeat summaries unless new actions are taken.
        '''},
        {"role": "user", "content": user_goal}
    ]

    # Agent loop
    while True:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        reply = response.choices[0].message
        messages.append(reply)

        if reply.tool_calls:
            for tool_call in reply.tool_calls:
                if tool_call.function.name == "bootstrap_project":
                    args = eval(tool_call.function.arguments)
                    bootstrap_project(**args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "bootstrap_project",
                        "content": "Project bootstrapped."
                    })
                if tool_call.function.name == "bootstrap_vite_project":
                    args = eval(tool_call.function.arguments)
                    bootstrap_project(**args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "bootstrap_vite_project",
                        "content": "Vite Project bootstrapped."
                    })
                elif tool_call.function.name == "create_file":
                    args = eval(tool_call.function.arguments)
                    create_file(**args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "create_file",
                        "content": "File created successfully."
                    })
                elif tool_call.function.name == "read_file":
                    args = eval(tool_call.function.arguments)
                    read_file(**args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "read_file",
                        "content": "File read successfully."
                    })
                elif tool_call.function.name == "edit_file":
                    args = eval(tool_call.function.arguments)
                    edit_file(**args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "edit_file",
                        "content": "File edited successfully."
                    })
                elif tool_call.function.name == "run_project":
                    args = eval(tool_call.function.arguments)
                    run_project(**args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "run_project",
                        "content": "Project started."
                    })
                elif tool_call.function.name == "finish":
                    args = eval(tool_call.function.arguments)
                    finish(**args)
                    exit(0)
        else:
            print("🤖 Agent message:", reply.content)

if __name__ == "__main__":
    main()