import tkinter as tk
from tkinter import ttk
import caldav

def fetch_tasks():
    """Connects to CalDAV server and populates the listbox with task names."""
    url = url_entry.get()
    username = user_entry.get()
    password = pass_entry.get()

    if not all([url, username, password]):
        status_var.set("Error: All fields are required.")
        return

    # Clear previous results and set status
    task_listbox.delete(0, tk.END)
    status_var.set("Connecting...")
    root.update_idletasks()  # Force GUI to update

    try:
        with caldav.DAVClient(
            url=url, username=username, password=password
        ) as client:
            principal = client.principal()
            calendars = principal.calendars()
            status_var.set("Fetching tasks...")
            root.update_idletasks()

            task_count = 0
            for calendar in calendars:
                # Search for VTODO components (tasks)
                for task in calendar.todos():
                    task_name = task.vobject_instance.vtodo.summary.value
                    task_listbox.insert(tk.END, task_name)
                    task_count += 1

            status_var.set(f"Success! Found {task_count} tasks.")

    except Exception as e:
        status_var.set(f"Error: {e}")


# --- GUI Setup ---
root = tk.Tk()
root.title("Simple CalDAV Task Viewer")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Input fields
ttk.Label(frame, text="CalDAV URL:").grid(column=0, row=0, sticky=tk.W)
url_entry = ttk.Entry(frame, width=40)
url_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Username:").grid(column=0, row=1, sticky=tk.W)
user_entry = ttk.Entry(frame, width=40)
user_entry.grid(column=1, row=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Password:").grid(column=0, row=2, sticky=tk.W)
pass_entry = ttk.Entry(frame, width=40, show="*")
pass_entry.grid(column=1, row=2, sticky=(tk.W, tk.E))

# Action button
fetch_button = ttk.Button(frame, text="Fetch Tasks", command=fetch_tasks)
fetch_button.grid(column=1, row=3, sticky=tk.E, pady=5)

# Results listbox
task_listbox = tk.Listbox(frame, height=15)
task_listbox.grid(column=0, row=4, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

# Status bar
status_var = tk.StringVar()
status_label = ttk.Label(frame, textvariable=status_var, anchor=tk.W)
status_label.grid(column=0, row=5, columnspan=2, sticky=(tk.W, tk.E))

# --- Start GUI ---
root.mainloop()
