import tkinter as tk
from tkinter import filedialog, messagebox
import re

# Function to handle the file processing logic
def scale_loadcases(loadcases, scale_factor, lcid_not_to_change):
    scaled_loadcases = []
    comb_pattern = re.compile(r"^comb\s+(\d+)\s+'([^']+)'\s+(.+)")

    for loadcase in loadcases:
        loadcase = loadcase.strip()
        comb_match = comb_pattern.match(loadcase)
        if comb_match:
            lc_id, lc_name, operations = comb_match.groups()
            lc_id = int(lc_id)

            # Split the operations part into individual components
            components = re.split(r'(\s[+-]\s)', operations)
            scaled_operations = []

            for component in components:
                float_match = re.match(r'(\d*\.?\d+)\s+\((\d+)\)', component.strip())
                if float_match:
                    value, operation_lcid = float_match.groups()
                    operation_lcid = int(operation_lcid)
                    value = float(value)
                    if operation_lcid not in lcid_not_to_change:
                        value *= scale_factor
                    scaled_operations.append(f"{value:.3f} ({operation_lcid})")
                else:
                    scaled_operations.append(component)

            scaled_operations_str = ''.join(scaled_operations)
            scaled_operations_str = re.sub(r'\+\s+\-', '- ', scaled_operations_str)
            scaled_operations_str = re.sub(r'\-\s+\-', '+ ', scaled_operations_str)
            scaled_operations_str = re.sub(r'\+\s+\+', '+ ', scaled_operations_str)
            scaled_operations_str = re.sub(r'\-\s+\+', '- ', scaled_operations_str)
            
            scaled_loadcases.append(f"comb {lc_id} '{lc_name}' {scaled_operations_str}\n")
        else:
            scaled_loadcases.append(loadcase + "\n")

    return scaled_loadcases

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
        file_label.config(text=f"Selected File: {file_path}")

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

# Set the color scheme
root.configure(bg="#f0f8ff")  # Light blue background

# File selection section
file_frame = tk.Frame(root, bg="#f0f8ff")
file_frame.pack(pady=10)

file_label = tk.Label(file_frame, text="No file selected", bg="#f0f8ff", font=("Arial", 12))
file_label.pack(side=tk.LEFT, padx=10)

file_button = tk.Button(file_frame, text="Select File", command=open_file, bg="#007acc", fg="white", font=("Arial", 12))
file_button.pack(side=tk.LEFT)

# Scale factor input
scale_factor_frame = tk.Frame(root, bg="#f0f8ff")
scale_factor_frame.pack(pady=10)

scale_factor_label = tk.Label(scale_factor_frame, text="Scale Factor:", bg="#f0f8ff", font=("Arial", 12))
scale_factor_label.pack(side=tk.LEFT, padx=10)

scale_factor_entry = tk.Entry(scale_factor_frame, width=10, font=("Arial", 12))
scale_factor_entry.pack(side=tk.LEFT)

# Loadcase input section
loadcase_frame = tk.Frame(root, bg="#f0f8ff")
loadcase_frame.pack(pady=10)

loadcase_label = tk.Label(loadcase_frame, text="LCIDs Not to Change:", bg="#f0f8ff", font=("Arial", 12))
loadcase_label.pack(side=tk.LEFT, padx=10)

loadcase_entry = tk.Entry(loadcase_frame, width=10, font=("Arial", 12))
loadcase_entry.pack(side=tk.LEFT)

add_button = tk.Button(loadcase_frame, text="Add", command=add_loadcase, bg="#007acc", fg="white", font=("Arial", 12))
add_button.pack(side=tk.LEFT, padx=5)

# Listbox for LCIDs
listbox_frame = tk.Frame(root, bg="#f0f8ff")
listbox_frame.pack(pady=10)

loadcase_listbox = tk.Listbox(listbox_frame, width=20, height=5, font=("Arial", 12))
loadcase_listbox.pack(side=tk.LEFT)

# Process file button
process_button = tk.Button(root, text="Process File", command=process_file, bg="#007acc", fg="white", font=("Arial", 14))
process_button.pack(pady=20)

root.mainloop()
