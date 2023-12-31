import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime
import os


class Account:
    ID = 0

    def __init__(self, balance):
        self.ID = Account.ID
        self.balance = balance
        self.note_history = []  # List to store dictionaries for each operation
        Account.ID += 1

    def update_balance(self, amount, note=""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        operation = {"timestamp": timestamp, "amount": amount, "note": note}
        self.balance += amount
        self.note_history.append(operation)

    def to_dict(self):
        return {"ID": self.ID, "balance": self.balance, "note_history": self.note_history}


class ExpanseTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Expanse Tracker")
        master.geometry("900x600")  # Set fixed window size

        # Initialize account_vars dictionary
        self.account_vars = {}

        # Create UI components
        self.label = tk.Label(master, text="Expanse Tracker App")
        self.label.pack()

        # Create account list
        self.accounts = []

        # Initialize the variable to store the current account frame
        self.current_account_frame = None

        # Frame for buttons
        button_frame = tk.Frame(master)
        button_frame.pack()

        # Label and Entry for updating balance
        tk.Label(button_frame, text="Amount:").pack(side=tk.LEFT)

        # Entry for amount
        self.amount_entry = tk.Entry(button_frame)
        self.amount_entry.pack(side=tk.LEFT)

        # Buttons for positive and negative amounts
        negative_button = tk.Button(button_frame, text="-", command=lambda: self.set_amount(-1))
        negative_button.pack(side=tk.RIGHT)
        positive_button = tk.Button(button_frame, text="+", command=lambda: self.set_amount(1))
        positive_button.pack(side=tk.RIGHT, padx=5)

        # Label and Entry for adding notes
        tk.Label(master, text="Note (optional):").pack()
        self.note_var = tk.StringVar()  # Create a StringVar variable
        self.note_entry = tk.Entry(master, textvariable=self.note_var)
        self.note_entry.pack()

        update_button = tk.Button(master, text="Update Balance", command=self.update_balance)
        update_button.pack()

        # Remove account button
        remove_button = tk.Button(master, text="Remove Account", command=self.remove_account)
        remove_button.pack()

        # Load accounts from file if it exists
        self.load_accounts()

        # Display account information
        self.display_accounts()  # Display accounts after loading

        # Ensure that the account information is visible on startup
        master.update_idletasks()

    def display_accounts(self):
        # Clear the current account frame if it exists
        if self.current_account_frame:
            self.current_account_frame.destroy()

        if self.accounts:
            # Create Frame for the current account
            self.current_account_frame = tk.Frame(self.master)
            self.current_account_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            account = self.accounts[0]  # Assuming you want to display information for the first account
            # Format note history with each operation on a new line
            note_history_text = "\n".join([f"({op['timestamp']}) Amount: {op['amount']}, Note: {op['note']}" for op in account.note_history])

            # Create Text widget with vertical scroll bar inside the Frame
            account_text = tk.Text(self.current_account_frame, wrap=tk.WORD, width=50, height=5)
            account_text.insert(tk.END, f"ID: {account.ID}, Balance: {account.balance}, Note History:\n{note_history_text}")
            account_text.config(state=tk.DISABLED)  # Disable editing
            account_scroll = tk.Scrollbar(self.current_account_frame, command=account_text.yview)
            account_text.config(yscrollcommand=account_scroll.set)

            account_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            account_scroll.pack(side=tk.RIGHT, fill=tk.Y)

            # Save Text widget and Frame in the dictionary
            self.account_vars[account.ID] = {"text": account_text, "frame": self.current_account_frame}

    def update_balance(self):
        try:
            amount = float(self.amount_entry.get())
            note = self.note_var.get()

            # Check if there are any accounts
            if not self.accounts:
                # If no accounts exist, create a new account
                new_account = Account(0.0)
                self.accounts.append(new_account)
            else:
                # Update the balance and note history of the first account
                self.accounts[0].update_balance(amount, note)

            # Save accounts after updating the balance
            self.save_accounts()

            # Display accounts after updating the balance
            self.display_accounts()

            self.amount_entry.delete(0, tk.END)  # Clear the entry field
            self.note_var.set("")  # Clear the note entry field

        except ValueError:
            print("Invalid input. Please enter a valid number.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def remove_account(self):
        if self.accounts:
            confirmation = messagebox.askokcancel("Confirmation", "Are you sure you want to remove the account?")
            if confirmation:
                # Remove the accounts.json file
                file_path = 'accounts.json'
                try:
                    os.remove(file_path)
                    print(f"{file_path} removed.")
                except FileNotFoundError:
                    print(f"{file_path} does not exist.")

                # Create a new account
                new_account = Account(0.0)
                self.accounts = [new_account]

                # Save the updated accounts after removing
                self.save_accounts()

                # Display accounts after updating the balance
                self.display_accounts()

            else:
                print("Account removal canceled.")
        else:
            print("No account to remove.")

    def set_amount(self, sign):
        current_amount = self.amount_entry.get()
        try:
            current_amount = float(current_amount)
        except ValueError:
            current_amount = 0.0
        new_amount = abs(current_amount) * sign
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, str(new_amount))

    def save_accounts(self):
        data = [account.to_dict() for account in self.accounts]
        with open('accounts.json', 'w') as file:
            json.dump(data, file, indent=2)
        print("Accounts saved to accounts.json")

    def load_accounts(self):
        try:
            with open('accounts.json', 'r') as file:
                data = json.load(file)

                if data:
                    # If data is not empty, update accounts and find the maximum ID
                    self.accounts = [Account(acc["balance"]) for acc in data]
                    Account.ID = max(acc["ID"] for acc in data) + 1
                    for acc, acc_data in zip(self.accounts, data):
                        acc.note_history = acc_data.get("note_history", [])
                else:
                    # If data is empty, set Account.ID to 1
                    Account.ID = 1

            # Display accounts after loading
            self.display_accounts()

        except FileNotFoundError:
            print("No save file found.")
            # If no save file is found, create a new account
            new_account = Account(0.0)
            self.accounts.append(new_account)
            # Display accounts after creating a new account
            self.display_accounts()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpanseTrackerApp(root)
    root.mainloop()
