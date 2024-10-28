import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datasets import load_dataset, get_dataset_split_names
from huggingface_hub import login
import threading
import os
import shutil
import json
from huggingface_hub import HfFolder

class DatasetDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hugging Face Dataset Downloader")
        self.root.geometry("800x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Token entry
        ttk.Label(self.main_frame, text="HF Token:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(self.main_frame, textvariable=self.token_var, width=50, show="*")
        self.token_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Login button
        self.login_btn = ttk.Button(self.main_frame, text="Login", command=self.login_to_hf)
        self.login_btn.grid(row=0, column=3, sticky=tk.W, pady=5, padx=5)
        
        # Dataset name entry
        ttk.Label(self.main_frame, text="Dataset Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dataset_name = tk.StringVar()
        self.dataset_entry = ttk.Entry(self.main_frame, textvariable=self.dataset_name, width=50)
        self.dataset_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Download directory selection
        ttk.Label(self.main_frame, text="Save Location:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.download_path = tk.StringVar()
        self.path_entry = ttk.Entry(self.main_frame, textvariable=self.download_path, width=50)
        self.path_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.browse_btn = ttk.Button(self.main_frame, text="Browse", command=self.browse_directory)
        self.browse_btn.grid(row=2, column=2, sticky=tk.W, pady=5, padx=5)
        
        # Split selection
        ttk.Label(self.main_frame, text="Split:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.split_var = tk.StringVar()
        self.split_combo = ttk.Combobox(self.main_frame, textvariable=self.split_var, state="readonly")
        self.split_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Get splits button
        self.get_splits_btn = ttk.Button(self.main_frame, text="Get Available Splits", command=self.get_splits)
        self.get_splits_btn.grid(row=3, column=2, sticky=tk.W, pady=5, padx=5)
        
        # Download button
        self.download_btn = ttk.Button(self.main_frame, text="Download Dataset", command=self.start_download)
        self.download_btn.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)
        
        # Initialize token status
        self.token = None
        self.check_existing_token()

    def check_existing_token(self):
        """Check if there's an existing token in HfFolder"""
        existing_token = HfFolder.get_token()
        if existing_token:
            self.token = existing_token
            self.token_var.set(existing_token)
            self.status_var.set("Token loaded from system")
            
    def login_to_hf(self):
        """Login to Hugging Face using the provided token"""
        token = self.token_var.get().strip()
        if not token:
            messagebox.showerror("Error", "Please enter your Hugging Face token")
            return
            
        try:
            login(token=token)
            self.token = token
            self.status_var.set("Successfully logged in to Hugging Face")
            messagebox.showinfo("Success", "Successfully logged in to Hugging Face")
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_path.set(directory)
    
    def get_splits(self):
        if not self.token:
            messagebox.showerror("Error", "Please login first")
            return
            
        dataset_name = self.dataset_name.get().strip()
        if not dataset_name:
            messagebox.showerror("Error", "Please enter a dataset name")
            return
            
        try:
            splits = get_dataset_split_names(dataset_name, use_auth_token=self.token)
            self.split_combo['values'] = splits
            if splits:
                self.split_combo.set(splits[0])
            messagebox.showinfo("Success", f"Found splits: {', '.join(splits)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error getting splits: {str(e)}")
    
    def start_download(self):
        if not self.token:
            messagebox.showerror("Error", "Please login first")
            return
        thread = threading.Thread(target=self.download_dataset)
        thread.daemon = True
        thread.start()
    
    def save_dataset_to_disk(self, dataset, save_path):
        # Create directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        # Save dataset info
        info = {
            'num_rows': dataset.num_rows,
            'features': str(dataset.features),
            'split': self.split_var.get()
        }
        
        with open(os.path.join(save_path, 'dataset_info.json'), 'w') as f:
            json.dump(info, f, indent=4)
        
        # Save the dataset in different formats
        try:
            # As CSV
            dataset.to_csv(os.path.join(save_path, 'dataset.csv'))
            # As JSON
            dataset.to_json(os.path.join(save_path, 'dataset.json'))
            # As Parquet
            dataset.to_parquet(os.path.join(save_path, 'dataset.parquet'))
        except Exception as e:
            print(f"Error saving in some formats: {str(e)}")
    
    def download_dataset(self):
        dataset_name = self.dataset_name.get().strip()
        split = self.split_var.get()
        save_path = self.download_path.get().strip()
        
        if not all([dataset_name, split, save_path]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        self.progress.start()
        self.status_var.set("Downloading dataset...")
        self.download_btn.state(['disabled'])
        
        try:
            # Download the dataset
            dataset = load_dataset(dataset_name, split=split, use_auth_token=self.token)
            
            # Create a subdirectory with the dataset name
            dataset_dir = os.path.join(save_path, dataset_name.replace('/', '_'))
            
            # Save the dataset to disk
            self.save_dataset_to_disk(dataset, dataset_dir)
            
            success_message = (
                f"Dataset downloaded successfully!\n"
                f"Location: {dataset_dir}\n"
                f"Number of rows: {dataset.num_rows}"
            )
            
            self.status_var.set("Download completed!")
            messagebox.showinfo("Success", success_message)
            
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