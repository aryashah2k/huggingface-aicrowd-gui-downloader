import tkinter as tk
from tkinter import ttk, messagebox
from datasets import load_dataset, get_dataset_split_names
import threading
import os

class DatasetDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hugging Face Dataset Downloader")
        self.root.geometry("600x400")
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Dataset name entry
        ttk.Label(self.main_frame, text="Dataset Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.dataset_name = tk.StringVar()
        self.dataset_entry = ttk.Entry(self.main_frame, textvariable=self.dataset_name, width=50)
        self.dataset_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Split selection
        ttk.Label(self.main_frame, text="Split:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.split_var = tk.StringVar()
        self.split_combo = ttk.Combobox(self.main_frame, textvariable=self.split_var, state="readonly")
        self.split_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Get splits button
        self.get_splits_btn = ttk.Button(self.main_frame, text="Get Available Splits", command=self.get_splits)
        self.get_splits_btn.grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)
        
        # Download button
        self.download_btn = ttk.Button(self.main_frame, text="Download Dataset", command=self.start_download)
        self.download_btn.grid(row=2, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
    def get_splits(self):
        dataset_name = self.dataset_name.get().strip()
        if not dataset_name:
            messagebox.showerror("Error", "Please enter a dataset name")
            return
            
        try:
            splits = get_dataset_split_names(dataset_name)
            self.split_combo['values'] = splits
            if splits:
                self.split_combo.set(splits[0])
            messagebox.showinfo("Success", f"Found splits: {', '.join(splits)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error getting splits: {str(e)}")
    
    def start_download(self):
        thread = threading.Thread(target=self.download_dataset)
        thread.daemon = True
        thread.start()
    
    def download_dataset(self):
        dataset_name = self.dataset_name.get().strip()
        split = self.split_var.get()
        
        if not dataset_name:
            messagebox.showerror("Error", "Please enter a dataset name")
            return
            
        if not split:
            messagebox.showerror("Error", "Please select a split")
            return
        
        self.progress.start()
        self.status_var.set("Downloading dataset...")
        self.download_btn.state(['disabled'])
        
        try:
            dataset = load_dataset(dataset_name, split=split)
            self.status_var.set(f"Downloaded {dataset.num_rows} rows successfully!")
            messagebox.showinfo("Success", f"Dataset downloaded successfully!\nNumber of rows: {dataset.num_rows}")
        except Exception as e:
            self.status_var.set("Error downloading dataset")
            messagebox.showerror("Error", f"Error downloading dataset: {str(e)}")
        finally:
            self.progress.stop()
            self.download_btn.state(['!disabled'])

if __name__ == "__main__":
    root = tk.Tk()
    app = DatasetDownloaderApp(root)
    root.mainloop()