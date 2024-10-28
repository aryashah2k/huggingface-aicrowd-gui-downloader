import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os

class AICrowdDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("AIcrowd Dataset Downloader")
        self.geometry("600x500")
        
        # Create main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # API Key Section
        ttk.Label(main_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W)
        self.api_key = ttk.Entry(main_frame, width=50)
        self.api_key.grid(row=0, column=1, columnspan=2, pady=5)
        
        # Challenge Name Section
        ttk.Label(main_frame, text="Challenge Name:").grid(row=1, column=0, sticky=tk.W)
        self.challenge_name = ttk.Entry(main_frame, width=50)
        self.challenge_name.grid(row=1, column=1, columnspan=2, pady=5)
        
        # Download Location Section
        ttk.Label(main_frame, text="Download Location:").grid(row=2, column=0, sticky=tk.W)
        self.download_path = ttk.Entry(main_frame, width=40)
        self.download_path.grid(row=2, column=1, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_location).grid(row=2, column=2)
        
        # Download Type Selection
        self.download_type = tk.StringVar(value="index")
        ttk.Radiobutton(main_frame, text="Download by Index", variable=self.download_type, 
                       value="index").grid(row=3, column=0, columnspan=3, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="Download by Filename", variable=self.download_type, 
                       value="filename").grid(row=4, column=0, columnspan=3, sticky=tk.W)
        
        # Input Section
        ttk.Label(main_frame, text="Enter Index/Filename:").grid(row=5, column=0, sticky=tk.W)
        self.input_value = ttk.Entry(main_frame, width=50)
        self.input_value.grid(row=5, column=1, columnspan=2, pady=5)
        ttk.Label(main_frame, text="(Use comma for multiple values)").grid(row=6, column=1, sticky=tk.W)
        
        # List Datasets Button
        ttk.Button(main_frame, text="List Available Datasets", 
                  command=self.list_datasets).grid(row=7, column=0, columnspan=3, pady=10)
        
        # Download Button
        ttk.Button(main_frame, text="Download Dataset(s)", 
                  command=self.download_dataset).grid(row=8, column=0, columnspan=3, pady=10)
        
        # Output Text Area
        self.output_text = tk.Text(main_frame, height=10, width=60)
        self.output_text.grid(row=9, column=0, columnspan=3, pady=10)
        
    def browse_location(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.download_path.delete(0, tk.END)
            self.download_path.insert(0, folder_path)
    
    def run_command(self, command):
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()
            return output + error
        except Exception as e:
            return f"Error: {str(e)}"
    
    def list_datasets(self):
        if not self.api_key.get() or not self.challenge_name.get():
            messagebox.showerror("Error", "Please provide API key and challenge name")
            return
            
        # Login to AIcrowd
        login_cmd = f'aicrowd login --api-key {self.api_key.get()}'
        self.run_command(login_cmd)
        
        # List datasets
        list_cmd = f'aicrowd dataset list --challenge {self.challenge_name.get()}'
        output = self.run_command(list_cmd)
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, output)
    
    def download_dataset(self):
        if not all([self.api_key.get(), self.challenge_name.get(), 
                   self.download_path.get(), self.input_value.get()]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Change to download directory
        os.chdir(self.download_path.get())
        
        # Login to AIcrowd
        login_cmd = f'aicrowd login --api-key {self.api_key.get()}'
        self.run_command(login_cmd)
        
        # Prepare download command
        values = [v.strip() for v in self.input_value.get().split(',')]
        
        if self.download_type.get() == "index":
            download_items = ' '.join(values)
        else:
            download_items = ' '.join(f'"{v}"' for v in values)
        
        download_cmd = (f'aicrowd dataset download --challenge {self.challenge_name.get()} '
                       f'{download_items}')
        
        output = self.run_command(download_cmd)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, output)

if __name__ == "__main__":
    app = AICrowdDownloader()
    app.mainloop()