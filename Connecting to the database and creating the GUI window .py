# Connect to database
conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    description TEXT,
    category TEXT,
    amount REAL
)
""")
conn.commit()

# GUI setup
root = Tk()
root.title("Expense Tracker")
root.geometry("700x500")

# --- Input Frame ---
frame1 = Frame(root)
frame1.pack(pady=10)

Label(frame1, text="Date").grid(row=0, column=0, padx=5)
date_entry = DateEntry(frame1, width=12, background='darkblue', foreground='white', borderwidth=2)
date_entry.grid(row=0, column=1, padx=5)

Label(frame1, text="Description").grid(row=0, column=2, padx=5)
desc_entry = Entry(frame1)
desc_entry.grid(row=0, column=3, padx=5)

Label(frame1, text="Category").grid(row=1, column=0, padx=5)
cat_entry = Entry(frame1)
cat_entry.grid(row=1, column=1, padx=5)

Label(frame1, text="Amount").grid(row=1, column=2, padx=5)
amount_entry = Entry(frame1)
amount_entry.grid(row=1, column=3, padx=5)

def add_expense():
    date = date_entry.get()
    desc = desc_entry.get()
    category = cat_entry.get()
    try:
        amount = float(amount_entry.get())
    except ValueError:
        mb.showerror("Invalid Input", "Amount must be a number")
        return

    if desc == "" or category == "":
        mb.showwarning("Input Error", "Please fill all fields")
        return

    cursor.execute("INSERT INTO expenses (date, description, category, amount) VALUES (?, ?, ?, ?)",
                   (date, desc, category, amount))
    conn.commit()
    mb.showinfo("Success", "Expense added successfully")
    clear_fields()
    show_expenses()

def clear_fields():
    desc_entry.delete(0, END)
    cat_entry.delete(0, END)
    amount_entry.delete(0, END)

# --- Button Frame ---
frame2 = Frame(root)
frame2.pack(pady=10)

Button(frame2, text="Add Expense", command=add_expense).grid(row=0, column=0, padx=10)

# --- Treeview Table ---
tree = ttk.Treeview(root, columns=("Date", "Description", "Category", "Amount"), show='headings')
tree.heading("Date", text="Date")
tree.heading("Description", text="Description")
tree.heading("Category", text="Category")
tree.heading("Amount", text="Amount")
tree.pack(fill=BOTH, expand=True, pady=20)

def show_expenses():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT date, description, category, amount FROM expenses")
    for row in cursor.fetchall():
        tree.insert("", END, values=row)

show_expenses()
root.mainloop()
