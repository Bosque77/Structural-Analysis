import tkinter as tk
from tkinter import filedialog, messagebox
from scale_conditions_logic import scale_loadcases

# Function to open file and process it
def process_file():
    try:
        scale_factor = float(scale_factor_entry.get())
        lcid_not_to_change = list(map(int, loadcase_listbox.get(0, tk.END)))

        # Open the selected file and read its contents
        with open(file_path, 'r') as f:
            loadcases = f.readlines()

        # Process the file with the scaling logic
        scaled_loadcases = scale_loadcases(loadcases, scale_factor, lcid_not_to_change)

        # Save the processed loadcases to a new file
        outfile = filedialog.asksaveasfilename(defaultextension=".cond", filetypes=[("Condition files", "*.cond")])
        if outfile:
            with open(outfile, 'w') as f:
                f.writelines(scaled_loadcases)
            messagebox.showinfo("Success", "The file has been processed and saved.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to open the file dialog to select a file
def open_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Condition files", "*.cond")])
    if file_path:
        # Display only the filename in the scrollable text widget
        file_label.config(state=tk.NORMAL)  # Enable text box temporarily to insert text
        file_label.delete(1.0, tk.END)  # Clear the current text
        file_label.insert(tk.END, file_path.split('/')[-1])  # Insert the filename
        file_label.config(state=tk.DISABLED)  # Disable text box to prevent edits

# Function to add loadcases to the listbox
def add_loadcase():
    try:
        lcid = int(loadcase_entry.get())
        loadcase_listbox.insert(tk.END, lcid)
        loadcase_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid integer for the loadcase.")

# GUI Setup
root = tk.Tk()
root.title("Loadcase Scaling Tool")

# Set the color scheme and left alignment
root.configure(bg="#f0f8ff")  # Light blue background
root.grid_columnconfigure(0, weight=1)  # Ensure all widgets are left aligned

# File selection section
file_frame = tk.Frame(root, bg="#f0f8ff")
file_frame.grid(sticky="w", pady=10, padx=10)

file_label_title = tk.Label(file_frame, text="Selected File:", bg="#f0f8ff", font=("Arial", 12))
file_label_title.grid(sticky="w", row=0, column=0)

# Scrollable text box for file name display
file_label = tk.Text(file_frame, height=1, width=40, font=("Arial", 12), wrap=tk.NONE, state=tk.DISABLED)
file_label.grid(sticky="w", row=0, column=1)

scroll_x = tk.Scrollbar(file_frame, orient=tk.HORIZONTAL, command=file_label.xview)
file_label.config(xscrollcommand=scroll_x.set)
scroll_x.grid(row=1, column=1, sticky="ew")

file_button = tk.Button(file_frame, text="Select File", command=open_file, bg="#007acc", fg="white", font=("Arial", 12))
file_button.grid(sticky="w", row=0, column=2, padx=10)

# Scale factor input
scale_factor_frame = tk.Frame(root, bg="#f0f8ff")
scale_factor_frame.grid(sticky="w", pady=10, padx=10)

scale_factor_label = tk.Label(scale_factor_frame, text="Scale Factor:", bg="#f0f8ff", font=("Arial", 12))
scale_factor_label.grid(sticky="w", row=0, column=0)

scale_factor_entry = tk.Entry(scale_factor_frame, width=10, font=("Arial", 12))
scale_factor_entry.grid(sticky="w", row=0, column=1)

# Loadcase input section
loadcase_frame = tk.Frame(root, bg="#f0f8ff")
loadcase_frame.grid(sticky="w", pady=10, padx=10)

loadcase_label = tk.Label(loadcase_frame, text="LCIDs Not to Change:", bg="#f0f8ff", font=("Arial", 12))
loadcase_label.grid(sticky="w", row=0, column=0)

loadcase_entry = tk.Entry(loadcase_frame, width=10, font=("Arial", 12))
loadcase_entry.grid(sticky="w", row=0, column=1)

add_button = tk.Button(loadcase_frame, text="Add", command=add_loadcase, bg="#007acc", fg="white", font=("Arial", 12))
add_button.grid(sticky="w", row=0, column=2, padx=5)

# Listbox for LCIDs
listbox_frame = tk.Frame(root, bg="#f0f8ff")
listbox_frame.grid(sticky="w", pady=10, padx=10)

loadcase_listbox = tk.Listbox(listbox_frame, width=20, height=5, font=("Arial", 12))
loadcase_listbox.grid(sticky="w", row=0, column=0)

# Process file button
process_button = tk.Button(root, text="Process File", command=process_file, bg="#007acc", fg="white", font=("Arial", 14))
process_button.grid(sticky="w", pady=20, padx=10)

root.mainloop()
