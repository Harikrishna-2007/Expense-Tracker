import sqlite3
import datetime
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
import tkinter.messagebox as mb

# Functions
def list_all_expenses():
  global connector, table

  table.delete(*table.get_children())

  all_data = connector.execute('SELECT * FROM ExpenseTracker')
  data = all_data.fetchall()

  for values in data:
     table.insert('', END, values=values)


def view_expense_details():
  global table
  global date, payee, desc, amnt, MoP

  if not table.selection():
     mb.showerror('No expense selected', 'Please select an expense from the table to view its details')

  current_selected_expense = table.item(table.focus())
  values = current_selected_expense['values']

  expenditure_date = datetime.date(int(values[1][:4]), int(values[1][5:7]), int(values[1][8:]))

  date.set_date(expenditure_date) ; payee.set(values[2]) ; desc.set(values[3]) ; amnt.set(values[4]) ; MoP.set(values[5])


def clear_fields():
  global desc, payee, amnt, MoP, date, table

  today_date = datetime.datetime.now().date()

  desc.set('') ; payee.set('') ; amnt.set(0.0) ; MoP.set('Cash'), date.set_date(today_date)
  table.selection_remove(*table.selection())


def remove_expense():
  if not table.selection():
     mb.showerror('No record selected!', 'Please select a record to delete!')
     return

  current_selected_expense = table.item(table.focus())
  values_selected = current_selected_expense['values']

  surety = mb.askyesno('Are you sure?', f'Are you sure that you want to delete the record of {values_selected[2]}')

  if surety:
     connector.execute('DELETE FROM ExpenseTracker WHERE ID=%d' % values_selected[0])
     connector.commit()

     list_all_expenses()
     mb.showinfo('Record deleted successfully!', 'The record you wanted to delete has been deleted successfully')


def remove_all_expenses():
  surety = mb.askyesno('Are you sure?', 'Are you sure that you want to delete all the expense items from the database?', icon='warning')

  if surety:
     table.delete(*table.get_children())

     connector.execute('DELETE FROM ExpenseTracker')
     connector.commit()

     clear_fields()
     list_all_expenses()
     mb.showinfo('All Expenses deleted', 'All the expenses were successfully deleted')
  else:
     mb.showinfo('Ok then', 'The task was aborted and no expense was deleted!')


def add_another_expense():
  global date, payee, desc, amnt, MoP
  global connector

  if not date.get() or not payee.get() or not desc.get() or not amnt.get() or not MoP.get():
     mb.showerror('Fields empty!', "Please fill all the missing fields before pressing the add button!")
  else:
     connector.execute(
     'INSERT INTO ExpenseTracker (Date, Payee, Description, Amount, ModeOfPayment) VALUES (?, ?, ?, ?, ?)',
     (date.get_date(), payee.get(), desc.get(), amnt.get(), MoP.get())
     )
     connector.commit()

     clear_fields()
     list_all_expenses()
     mb.showinfo('Expense added', 'The expense whose details you just entered has been added to the database')


def edit_expense():
  global table

  def edit_existing_expense():
     global date, amnt, desc, payee, MoP
     global connector, table

     current_selected_expense = table.item(table.focus())
     contents = current_selected_expense['values']

     connector.execute('UPDATE ExpenseTracker SET Date = ?, Payee = ?, Description = ?, Amount = ?, ModeOfPayment = ? WHERE ID = ?',
                       (date.get_date(), payee.get(), desc.get(), amnt.get(), MoP.get(), contents[0]))
     connector.commit()

     clear_fields()
     list_all_expenses()

     mb.showinfo('Data edited', 'We have updated the data and stored in the database as you wanted')
     edit_btn.destroy()
     return

  if not table.selection():
     mb.showerror('No expense selected!', 'You have not selected any expense in the table for us to edit; please do that!')
     return

  view_expense_details()

  edit_btn = Button(data_entry_frame, text='Edit expense', font=btn_font, width=30,
                    bg=hlb_btn_bg, command=edit_existing_expense)
  edit_btn.place(x=10, y=395)


def selected_expense_to_words():
  global table

  if not table.selection():
     mb.showerror('No expense selected!', 'Please select an expense from the table for us to read')
     return

  current_selected_expense = table.item(table.focus())
  values = current_selected_expense['values']

  message = f'Your expense can be read like: \n"You paid {values[4]} to {values[2]} for {values[3]} on {values[1]} via {values[5]}"'

  mb.showinfo('Here\'s how to read your expense', message)


def expense_to_words_before_adding():
  global date, desc, amnt, payee, MoP

  if not date or not desc or not amnt or not payee or not MoP:
     mb.showerror('Incomplete data', 'The data is incomplete, meaning fill all the fields first!')

  message = f'Your expense can be read like: \n"You paid {amnt.get()} to {payee.get()} for {desc.get()} on {date.get_date()} via {MoP.get()}"'

  add_question = mb.askyesno('Read your record like: ', f'{message}\n\nShould I add it to the database?')

  if add_question:
     add_another_expense()
  else:
     mb.showinfo('Ok', 'Please take your time to add this record')
      
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
