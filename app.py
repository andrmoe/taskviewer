import tkinter as tk
from tkinter import ttk
import configparser
from typing import List, Tuple, Optional

import caldav
from caldav.objects import Todo
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
) -> List[Todo]:
    """Fetches task summaries from a specific CalDAV calendar."""
    tasks: List[Todo] = []
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
                    #summary = task.vobject_instance.vtodo.summary.value
                    tasks.append(task)
        
        return tasks
    except Exception as e:
        return [f"Error: {e}"]


# --- GUI Application ---

class CalDavApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CalDAV Tasks")
        self.root.geometry("400x500")
        self.task_objects: [Todo] = []
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.task_listbox = tk.Listbox(main_frame)
        self.task_listbox.pack(pady=5, fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        complete_button = ttk.Button(button_frame, text="Complete Selected Task", command=self.complete_task)
        complete_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
        refresh_button = ttk.Button(
            main_frame, text="Refresh Tasks", command=self.refresh_tasks
        )
        refresh_button.pack(fill=tk.X)

        self.refresh_tasks()

    def complete_task(self) -> None:
        """Marks the selected task as complete and saves it to the server."""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("No Selection", "Please select a task to complete.")
            return

        index = selected_indices[0]
        task_to_complete = self.task_objects[index]

        try:
            task_to_complete.complete()  # This sets status, completed-date, etc.
            task_to_complete.save()
            self.refresh_tasks()
        except Exception as e:
            messagebox.showerror("Error", f"Could not complete task: {e}")

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
        self.task_objects = fetch_tasks(url, username, password, calendar_name)

        self.task_listbox.delete(0, tk.END)
        if not self.task_objects:
            self.task_listbox.insert(tk.END, "No tasks found.")
        else:
            for task in self.task_objects:
                self.task_listbox.insert(tk.END, task.vobject_instance.vtodo.summary.value)


if __name__ == "__main__":
    root = tk.Tk()
    app = CalDavApp(root)
    root.mainloop()
