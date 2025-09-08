import tkinter as tk
from tkinter import ttk
import configparser
from typing import List, Tuple, Optional

import caldav

# --- Configuration and CalDAV Logic ---

def load_config() -> Optional[Tuple[str, str, str, str]]:
    """Reads CalDAV credentials and calendar name from config.ini."""
    try:
        config = configparser.ConfigParser()
        config.read("config.ini")
        url = config["caldav"]["url"]
        username = config["caldav"]["username"]
        password = config["caldav"]["password"]
        calendar_name = config["caldav"]["calendar_name"]
        return url, username, password, calendar_name
    except (KeyError, FileNotFoundError):
        return None


def fetch_tasks(
    url: str, username: str, password: str, calendar_name: str
) -> List[str]:
    """Fetches task summaries from a specific CalDAV calendar."""
    task_summaries: List[str] = []
    try:
        with caldav.DAVClient(
            url=url, username=username, password=password
        ) as client:
            principal = client.principal()
            
            # Find the specific calendar by its display name
            target_calendar = None
            for cal in principal.calendars():
                if cal.name == calendar_name:
                    target_calendar = cal
                    break
            
            if not target_calendar:
                return [f"Error: Calendar '{calendar_name}' not found."]

            # Fetch tasks only from the target calendar
            for task in target_calendar.todos(include_completed=False):
                if hasattr(task.vobject_instance, 'vtodo') and hasattr(task.vobject_instance.vtodo, 'summary') and task.vobject_instance.vtodo.status.value == 'NEEDS-ACTION':
                    summary = task.vobject_instance.vtodo.summary.value
                    task_summaries.append(str(summary))
        
        return task_summaries
    except Exception as e:
        return [f"Error: {e}"]


# --- GUI Application ---

class CalDavApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CalDAV Tasks")
        self.root.geometry("400x500")

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.task_listbox = tk.Listbox(main_frame)
        self.task_listbox.pack(pady=5, fill=tk.BOTH, expand=True)

        refresh_button = ttk.Button(
            main_frame, text="Refresh Tasks", command=self.refresh_tasks
        )
        refresh_button.pack(fill=tk.X)

        self.refresh_tasks()

    def refresh_tasks(self) -> None:
        """Clears the listbox and re-populates it with tasks."""
        self.task_listbox.delete(0, tk.END)
        self.task_listbox.insert(tk.END, "Loading...")
        self.root.update_idletasks()

        config = load_config()
        if not config:
            self.task_listbox.delete(0, tk.END)
            self.task_listbox.insert(tk.END, "Error: config.ini not found or invalid.")
            return

        url, username, password, calendar_name = config
        tasks = fetch_tasks(url, username, password, calendar_name)

        self.task_listbox.delete(0, tk.END)
        if not tasks:
            self.task_listbox.insert(tk.END, "No tasks found.")
        else:
            for task_name in tasks:
                self.task_listbox.insert(tk.END, task_name)


if __name__ == "__main__":
    root = tk.Tk()
    app = CalDavApp(root)
    root.mainloop()
