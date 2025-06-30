import sqlite3
import datetime
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
import tkinter.messagebox as mb

# Connect to the SQLite database
connector = sqlite3.connect("ExpenseTracker.db")
cursor = connector.cursor()

# Create the table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS ExpenseTracker (
    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Date TEXT,
    Payee TEXT,
    Description TEXT,
    Amount REAL,
    Mode_of_Payment TEXT
)
''')
connector.commit()

# GUI setup
root = Tk()
root.title("Expense Tracker")
root.geometry("900x600")
root.resizable(False, False)

# Variables
date = StringVar()
payee = StringVar()
desc = StringVar()
amnt = DoubleVar()
MoP = StringVar()

# Function to add a new expense
def add_expense():
    if not (date.get() and payee.get() and desc.get() and amnt.get() and MoP.get()):
        mb.showerror("Error", "Please fill all fields.")
        return

    connector.execute(
        'INSERT INTO ExpenseTracker (Date, Payee, Description, Amount, Mode_of_Payment) VALUES (?, ?, ?, ?, ?)',
        (date.get(), payee.get(), desc.get(), amnt.get(), MoP.get())
    )
    connector.commit()
    mb.showinfo("Success", "Expense added successfully!")
    list_all_expenses()
    clear_fields()

# Function to list all expenses
def list_all_expenses():
    table.delete(*table.get_children())
    all_data = connector.execute('SELECT * FROM ExpenseTracker')
    for row in all_data:
        table.insert('', END, values=row)

# Function to view details of selected expense
def view_expense_details():
    if not table.selection():
        mb.showerror("Error", "Please select a record to view.")
        return

    selected = table.item(table.focus())['values']
    date.set(selected[1])
    payee.set(selected[2])
    desc.set(selected[3])
    amnt.set(selected[4])
    MoP.set(selected[5])

# Function to clear all input fields
def clear_fields():
    today = datetime.datetime.now().date()
    date_entry.set_date(today)
    payee.set('')
    desc.set('')
    amnt.set(0.0)
    MoP.set('Cash')
    table.selection_remove(*table.selection())

# Function to delete selected expense
def remove_expense():
    if not table.selection():
        mb.showerror("Error", "Please select a record to delete.")
        return

    selected = table.item(table.focus())['values']
    confirm = mb.askyesno("Confirm", f"Delete record for {selected[2]}?")
    if confirm:
        connector.execute('DELETE FROM ExpenseTracker WHERE ID=?', (selected[0],))
        connector.commit()
        list_all_expenses()
        mb.showinfo("Deleted", "Record deleted successfully.")

# Function to delete all records
def remove_all_expenses():
    confirm = mb.askyesno("Confirm", "Delete ALL records?", icon="warning")
    if confirm:
        connector.execute('DELETE FROM ExpenseTracker')
        connector.commit()
        list_all_expenses()
        mb.showinfo("Deleted", "All records have been deleted.")

# --- GUI Layout ---

# Input frame
frame = Frame(root, bg="#f0f0f0", padx=10, pady=10)
frame.pack(fill=X)

Label(frame, text="Date:").grid(row=0, column=0, sticky=W)
date_entry = DateEntry(frame, textvariable=date, date_pattern="yyyy-mm-dd", width=15)
date_entry.grid(row=0, column=1, padx=10)

Label(frame, text="Payee:").grid(row=0, column=2, sticky=W)
Entry(frame, textvariable=payee).grid(row=0, column=3, padx=10)

Label(frame, text="Description:").grid(row=1, column=0, sticky=W)
Entry(frame, textvariable=desc, width=40).grid(row=1, column=1, columnspan=3, pady=5)

Label(frame, text="Amount:").grid(row=2, column=0, sticky=W)
Entry(frame, textvariable=amnt).grid(row=2, column=1)

Label(frame, text="Payment Mode:").grid(row=2, column=2, sticky=W)
OptionMenu(frame, MoP, "Cash", "Credit Card", "Debit Card", "UPI", "Bank Transfer").grid(row=2, column=3, padx=10)
MoP.set("Cash")

# Buttons frame
btn_frame = Frame(root, pady=10)
btn_frame.pack()

Button(btn_frame, text="Add Expense", command=add_expense, width=15, bg="#4caf50", fg="white").grid(row=0, column=0, padx=10)
Button(btn_frame, text="View Details", command=view_expense_details, width=15).grid(row=0, column=1, padx=10)
Button(btn_frame, text="Clear Fields", command=clear_fields, width=15).grid(row=0, column=2, padx=10)
Button(btn_frame, text="Delete Selected", command=remove_expense, width=15, bg="#f44336", fg="white").grid(row=0, column=3, padx=10)
Button(btn_frame, text="Delete All", command=remove_all_expenses, width=15, bg="#d32f2f", fg="white").grid(row=0, column=4, padx=10)

# Table frame
table_frame = Frame(root)
table_frame.pack(fill=BOTH, expand=True)

scroll = Scrollbar(table_frame, orient=VERTICAL)
table = ttk.Treeview(table_frame, yscrollcommand=scroll.set, columns=("ID", "Date", "Payee", "Description", "Amount", "MoP"), show="headings")
scroll.config(command=table.yview)
scroll.pack(side=RIGHT, fill=Y)

for col in ("ID", "Date", "Payee", "Description", "Amount", "MoP"):
    table.heading(col, text=col)
    table.column(col, anchor=CENTER)

table.pack(fill=BOTH, expand=True)

# Load existing data
list_all_expenses()

# Run the app
root.mainloop()
