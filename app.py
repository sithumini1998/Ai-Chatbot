import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import threading
import json

class HuggingFaceChatbot:
    def __init__(self, master):
        self.master = master
        master.title("HuggingFace AI Chatbot")
        master.geometry("600x550")
        master.configure(bg='#ececec')  # Changed background color to a lighter shade

        # Chat History
        self.chat_history = scrolledtext.ScrolledText(
            master, 
            wrap=tk.WORD, 
            width=70, 
            height=20, 
            font=('Arial', 11),  # Increased font size
            bg='#f7f7f7',        # Light gray background for chat history
            fg='#333333'         # Dark text for better readability
        )
        self.chat_history.grid(
            row=0, 
            column=0, 
            columnspan=3, 
            padx=20, 
            pady=20
        )
        self.chat_history.config(state=tk.DISABLED)

        # User Input
        self.user_input = tk.Entry(
            master, 
            width=50, 
            font=('Arial', 12), 
            bd=2, 
            relief='solid',  # Border around the input field
            bg='#ffffff',
            fg='#333333'
        )
        self.user_input.grid(
            row=1, 
            column=0, 
            padx=20, 
            pady=10
        )
        self.user_input.bind('<Return>', self.send_message)

        # Send Button
        self.send_button = tk.Button(
            master, 
            text="Send", 
            command=self.send_message,
            bg='#4CAF50', 
            fg='white', 
            font=('Arial', 12, 'bold'),  # Larger font and bold
            relief='flat',  # Flat button style
            activebackground='#45a049'  # Button color on hover
        )
        self.send_button.grid(
            row=1, 
            column=1, 
            padx=10, 
            pady=10
        )

        # API Key Entry
        self.api_key_label = tk.Label(
            master, 
            text="Hugging Face API Key:", 
            font=('Arial', 12)
        )
        self.api_key_label.grid(row=2, column=0, padx=20, pady=5, sticky="e")
        
        self.api_key_entry = tk.Entry(
            master, 
            width=50, 
            show="*", 
            font=('Arial', 12), 
            bd=2, 
            relief='solid', 
            bg='#ffffff',
            fg='#333333'
        )
        self.api_key_entry.grid(row=2, column=1, padx=20, pady=5)

        # Model Selection Dropdown
        self.models = [
            "facebook/blenderbot-400M-distill",
            "mistralai/Mistral-7B-Instruct-v0.1",
            "google/flan-t5-large"
        ]
        self.model_var = tk.StringVar(master)
        self.model_var.set(self.models[0])  # default value
        
        self.model_dropdown = tk.OptionMenu(
            master, 
            self.model_var, 
            *self.models
        )
        self.model_dropdown.grid(
            row=3, 
            column=0, 
            columnspan=2, 
            padx=20, 
            pady=10
        )

        # Style Adjustments
        self.master.option_add('*Font', 'Arial 10')  # Default font for all widgets

    def send_message(self, event=None):
        # Get API key from entry
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter your Hugging Face API Key")
            return

        # Get user message
        user_message = self.user_input.get()
        if not user_message:
            return

        # Clear input field
        self.user_input.delete(0, tk.END)

        # Update chat history with user message
        self.update_chat_history("You", user_message)

        # Disable send button during processing
        self.send_button['state'] = tk.DISABLED

        # Run AI response in a separate thread
        threading.Thread(
            target=self.get_ai_response, 
            args=(api_key, user_message), 
            daemon=True
        ).start()

    def get_ai_response(self, api_key, message):
        try:
            # Get selected model
            selected_model = self.model_var.get()

            # Hugging Face Inference API endpoint
            API_URL = f"https://api-inference.huggingface.co/models/{selected_model}"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Payload for the API request
            payload = {
                "inputs": message,
                "parameters": {
                    "max_new_tokens": 250
                }
            }

            # Send POST request to Hugging Face API
            response = requests.post(
                API_URL, 
                headers=headers, 
                data=json.dumps(payload),
                timeout=60
            )

            # Check response
            if response.status_code == 200:
                # Extract AI response
                ai_response = response.json()[0]['generated_text']
                
                # Update chat history with AI response
                self.master.after(
                    0, 
                    self.update_chat_history, 
                    "AI", 
                    ai_response
                )
            else:
                # Handle error
                error_message = f"API Error: {response.status_code}\n{response.text}"
                self.master.after(
                    0, 
                    messagebox.showerror, 
                    "API Error", 
                    error_message
                )

        except Exception as e:
            # Detailed error handling
            error_message = f"Error: {str(e)}"
            self.master.after(
                0, 
                messagebox.showerror, 
                "API Error", 
                error_message
            )
        finally:
            # Re-enable send button
            self.master.after(0, self.enable_send_button)

    def enable_send_button(self):
        self.send_button['state'] = tk.NORMAL

    def update_chat_history(self, sender, message):
        # Enable text widget for editing
        self.chat_history['state'] = tk.NORMAL
        
        # Append new message
        self.chat_history.insert(
            tk.END, 
            f"{sender}: {message}\n\n"
        )
        
        # Scroll to the end
        self.chat_history.see(tk.END)
        
        # Disable text widget
        self.chat_history['state'] = tk.DISABLED

def main():
    root = tk.Tk()
    chatbot = HuggingFaceChatbot(root)
    root.mainloop()

if __name__ == "__main__":
    main()
