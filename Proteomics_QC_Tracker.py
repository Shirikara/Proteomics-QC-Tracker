import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, Checkbutton, IntVar, ttk
import os
import re
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from PIL import Image, ImageTk
import webbrowser
#cd 'C:\Course_Python_2024\Proposal\HeLa QC tracker\'

# Function to open GitHub link
def open_github():
    webbrowser.open("https://github.com/Shirikara/Proteomics-QC-Tracker")

# Function to extract HeLa amount from file name
def extract_hela_amount(file_name):
    hela_match = re.search(r"_([0-9.]+)ng", file_name)
    if hela_match:
        amount = hela_match.group(1)
        return float(amount) if '.' in amount else int(amount)
    return "Unknown"

# Main function
def main():
   #Add select folder button
    def select_folder():
        folder_path = filedialog.askdirectory()
        if folder_path:
            process_folder(folder_path)

    def process_folder(folder_path):
        try:
            hela_qc_database = pd.DataFrame()

            # Search for files ending with "stats.tsv"
            stats_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith("stats.tsv")]

            if not stats_files:
                messagebox.showerror("Error", "No valid files ending with 'stats.tsv' were found in the folder!")
                return

            for file_path in stats_files:
                temp_df = pd.read_csv(file_path, sep="\t")
                file_name = os.path.basename(file_path)

                # Extract metadata from file name
                date_match = re.search(r"(\d{2})(\d{2})(\d{4})", file_name)
                creation_date = datetime.strptime(f"{date_match.group()}", "%d%m%Y") if date_match else None

                valid_initials = ["SK", "JS", "SP", "GE"]
                initials_match = re.search(r"_([A-Z]{2})_", file_name)
                user_initials = initials_match.group(1) if initials_match and initials_match.group(1) in valid_initials else "Unknown"

                if "File.Name" in temp_df.columns:
                    temp_df["HeLa_amount"] = temp_df["File.Name"].apply(
                        lambda x: int(re.search(r"(\d{1,2})(?=ng|_ng)", x).group(1)) if re.search(r"(\d{1,2})(?=ng|_ng)", x) else None
                    )
                    temp_df["HeLa_amount"] = temp_df["HeLa_amount"].replace(2, 0.2)
                else:
                    messagebox.showwarning("Missing Column", "'File.Name' column not found in the data!")

                temp_df["Creation_Date"] = creation_date
                temp_df["User_Initials"] = user_initials
                hela_qc_database = pd.concat([hela_qc_database, temp_df], ignore_index=True)

            hela_qc_database["Creation_Date"] = hela_qc_database["Creation_Date"].dt.strftime("%Y-%m-%d")
            output_path = os.path.join(folder_path, "HeLa_QC_Database.csv")

            if os.path.exists(output_path):
                overwrite = messagebox.askyesno("File Exists", f"{output_path} already exists. Overwrite?")
                if not overwrite:
                    messagebox.showinfo("Save Canceled", "Save operation canceled by the user.")
                    return

            hela_qc_database.to_csv(output_path, index=False)
            messagebox.showinfo("Save Complete", f"Database saved as:\n{output_path}")

            process_hela_qc_database(hela_qc_database)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def process_hela_qc_database(hela_qc_database):
        try:
            selected_columns = [col for col, var in column_vars.items() if var.get() == 1]

            if not selected_columns:
                messagebox.showerror("Error", "No columns selected for plotting!")
                return

            for column in selected_columns:
                if column not in hela_qc_database.columns:
                    messagebox.showerror("Error", f"'{column}' column not found in the database!")
                    return
            save_plots = save_option.get() == "Yes"
            
            # Group data and calculate mean
            for column in selected_columns:
                data = hela_qc_database.groupby(["Creation_Date", "HeLa_amount"])[column].mean().reset_index()
                data["SE"] = data.groupby("HeLa_amount")[column].transform(lambda x: np.std(x) / np.sqrt(len(x)))

                # Define a custom color palette
                custom_palette = sns.color_palette("Set2", n_colors=len(data["HeLa_amount"].unique()))

                # Plot the results with standard error as error bars
                sns.set(style="whitegrid")
                plt.figure(figsize=(12, 6))

                sns.lineplot(
                    data=data,
                    x="Creation_Date",
                    y=column,
                    hue="HeLa_amount",
                    marker="o",
                    palette=custom_palette,
                    legend=None
                )

                for idx, hela_amount in enumerate(data["HeLa_amount"].unique()):
                    sub_df = data[data["HeLa_amount"] == hela_amount]
                    plt.errorbar(
                        sub_df["Creation_Date"],
                        sub_df[column],
                        yerr=sub_df["SE"],
                        fmt='o',
                        label=f"HeLa Amount {hela_amount} ng",
                        capsize=5,
                        color=custom_palette[idx]
                    )

                plt.title(f"{column} Over Time - timsTOF-SCP")
                plt.xlabel("Time")
                plt.ylabel(column)
                plt.legend(title="HeLa Amount (ng)")
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.grid(False)
                plt.show(block=False)
                plt.pause(0.2)  # Allow time for the plot to render before the next one
                
                if save_plots:
                    plot_path = os.path.join(os.getcwd(), f"{column}_plot.png")
                    plt.savefig(plot_path)

                plt.show(block=False)
                plt.pause(0.2)



        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Tkinter GUI setup
    root = tk.Tk()

    root.geometry("450x650")
    root.title("Proteomics QC Tracker")

    # Welcome text part 1
    welcome_label1 = tk.Label(
        root,
        text="Welcome to the Proteomics QC Tracker!",
        font=("Helvetica", 14),
        wraplength=400,
        justify="center"
    )
    welcome_label1.pack(pady=10)

    # Load and display logo
    img = Image.open("qc_logo.png")
    img = img.resize((150, 150), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    img_label = tk.Label(root, image=img_tk)
    img_label.image = img_tk
    img_label.pack(pady=10)

    # Welcome text part 2
    welcome_label2 = tk.Label(
        root,
        text="Please select QC parameters to plot:",
        font=("Helvetica", 12),
        wraplength=300,
        justify="center"
    )
    welcome_label2.pack(pady=10)
    
    # Columns to select
    columns = [
        "Precursors.Identified",
        "Proteins.Identified",
        "MS1.Signal",
        "MS2.Signal",
        "FWHM.Scans",
        "FWHM.RT",
        "Median.Mass.Acc.MS1",
        "Median.Mass.Acc.MS1.Corrected",
        "Median.Mass.Acc.MS2",
        "Median.Mass.Acc.MS2.Corrected",
        "Average.Peptide.Length",
        "Average.Missed.Tryptic.Cleavages"
    ]

    column_vars = {col: IntVar() for col in columns}

    # Create a frame for the checkboxes
    checkbox_frame = tk.Frame(root)
    checkbox_frame.pack(pady=10)

    # Separate columns into two lists for two columns of checkboxes
    half = len(columns) // 2
    left_columns = columns[:half]
    right_columns = columns[half:]

    # Add checkboxes to the left column
    for i, col in enumerate(left_columns):
        chk = Checkbutton(checkbox_frame, text=col, variable=column_vars[col])
        chk.grid(row=i, column=0, sticky="w")

    # Add checkboxes to the right column
    for i, col in enumerate(right_columns):
        chk = Checkbutton(checkbox_frame, text=col, variable=column_vars[col])
        chk.grid(row=i, column=1, sticky="w")
    
    # Dropdown menu for saving plots
    save_option_label = tk.Label(root, text="Save plots as images?",width= 20, font=("Helvetica", 12),anchor="center")
    save_option_label.pack(pady=5)

    save_option = tk.StringVar(value="No")
    save_dropdown = ttk.Combobox(root, textvariable=save_option, values=["Yes", "No"], state="readonly", width=10)
    save_dropdown.pack(pady=5)

    # Select "stats" folder button (green)
    select_button = tk.Button(root, text="Select Stats Folder", command=select_folder, width=20,bg = "#05E39C",fg = "black")
    select_button.pack(pady=15)

    #Exit button (red)
    exit_button = tk.Button(root, text="Exit", command=root.destroy, width=20, bg = "#CD4D44",fg = "white")
    exit_button.pack(pady=15)

    footer_label = tk.Label(root, text="Developed by Shiri Karagach Rubin", font=("Helvetica", 8), fg="gray")
    footer_label.pack(side="bottom", pady=5)
    
    # Load and display GitHub icon
    github_img = Image.open("github-logo.png")
    github_img = github_img.resize((30, 30), Image.Resampling.LANCZOS)
    github_img_tk = ImageTk.PhotoImage(github_img)

    # Create a frame for the GitHub icon and label
    github_frame = tk.Frame(root)
    github_frame.pack(pady=5)

    # Add the GitHub icon
    github_icon_label = tk.Label(github_frame, image=github_img_tk, cursor="hand2")
    github_icon_label.image = github_img_tk
    github_icon_label.pack(side="left")
    github_icon_label.bind("<Button-1>", lambda e: open_github())

    # Add the GitHub text link
    github_text_label = tk.Label(
        github_frame,
        text="View on GitHub",
        font=("Helvetica", 10, "underline"),
        fg="blue",
        cursor="hand2"
    )
    github_text_label.pack(side="left", padx=5)
    github_text_label.bind("<Button-1>", lambda e: open_github())

    root.mainloop()

if __name__ == "__main__":
    main()
