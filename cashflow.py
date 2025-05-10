from tkinter import *
import sqlite3
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import datetime
import threading
from datetime import timedelta

class cashflowClass:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1000x600+220+130")
        self.root.title("CashFlow Management System")
        self.root.config(bg="white")
        self.root.focus_force()
        self.all_entries = []  # store all transactions


        # Title
        title = Label(self.root, text="Cash Flow Overview", font=("Arial", 20, "bold"), bg="white", fg="#e50000")
        title.pack(pady=10)

        # Alert Display Area
        self.alert_frame = Frame(self.root, bg="#FFCCCB")
        self.alert_label = Label(self.alert_frame, text="", font=("Arial", 12, "bold"), bg="#FFCCCB", fg="red")
        self.alert_label.pack(pady=5, padx=10, fill=X)
        self.alert_frame.pack(fill=X, expand=False)

        # Dropdown Frame
        dropdown_frame = Frame(self.root, bg="white")
        dropdown_frame.pack(pady=5)

        # Year
        Label(dropdown_frame, text="Year:", font=("Arial", 12), bg="white").grid(row=0, column=0, padx=5)
        current_year = datetime.datetime.now().year
        self.year_var = StringVar()
        year_options = [str(year) for year in range(current_year - 16, current_year + 10)]
        self.year_combo = ttk.Combobox(dropdown_frame, textvariable=self.year_var, values=year_options, state="readonly", width=10)
        self.year_combo.current(16)
        self.year_combo.grid(row=0, column=1, padx=5)

        # Month
        Label(dropdown_frame, text="Month:", font=("Arial", 12), bg="white").grid(row=0, column=2, padx=5)
        self.month_var = StringVar()
        months = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]
        self.month_combo = ttk.Combobox(dropdown_frame, textvariable=self.month_var, values=months, state="readonly", width=15)
        self.month_combo.current(datetime.datetime.now().month - 1)
        self.month_combo.grid(row=0, column=3, padx=5)

        # Entry Frame
        self.entry_frame = Frame(self.root, bg="white")
        self.entry_frame.pack(pady=10)

        # Search Button
        search_btn = Button(dropdown_frame, text="Search", command=self.filter_by_month, bg="#007acc", fg="white", font=("Arial", 10, "bold"), width=10)
        search_btn.grid(row=0, column=4, padx=10)

        # Connect to database
        self.con = sqlite3.connect(database=r'imsc.db')
        self.cur = self.con.cursor()





        
        # Fixed Transactions Frame
        self.fixed_transactions_frame = Frame(self.root, bg="white")
        self.fixed_transactions_frame.pack(fill=X, padx=20, pady=10)

        # Fixed Transactions UI Elements
        Label(self.fixed_transactions_frame, text="Fixed Transactions", font=("Arial", 12, "bold"), bg="white").grid(row=0, column=0, columnspan=6, pady=5)
        Label(self.fixed_transactions_frame, text="Name:", bg="white").grid(row=1, column=0, padx=5)
        self.fixed_name_var = StringVar()
        Entry(self.fixed_transactions_frame, textvariable=self.fixed_name_var, width=15).grid(row=1, column=1, padx=5)
        Label(self.fixed_transactions_frame, text="Amount:", bg="white").grid(row=1, column=2, padx=5)
        self.fixed_amount_var = StringVar()
        Entry(self.fixed_transactions_frame, textvariable=self.fixed_amount_var, width=10).grid(row=1, column=3, padx=5)
        Label(self.fixed_transactions_frame, text="Day of Month:", bg="white").grid(row=1, column=4, padx=5)
        self.fixed_day_var = IntVar()
        Spinbox(self.fixed_transactions_frame, from_=1, to=31, textvariable=self.fixed_day_var, width=5).grid(row=1, column=5, padx=5)
        Label(self.fixed_transactions_frame, text="Type:", bg="white").grid(row=1, column=6, padx=5)
        self.fixed_type_var = StringVar()
        type_combo = ttk.Combobox(self.fixed_transactions_frame, textvariable=self.fixed_type_var, values=["Income", "Expense"], state="readonly", width=10)
        type_combo.grid(row=1, column=7, padx=5)
        self.fixed_type_var.set("Expense")
        Button(self.fixed_transactions_frame, text="Add Fixed", command=self.add_fixed_transaction, bg="#4CAF50", fg="white").grid(row=1, column=8, padx=5)
        Button(self.fixed_transactions_frame, text="Delete Selected", command=self.delete_fixed_transaction, bg="#e50000", fg="white").grid(row=1, column=9, padx=5)
        Button(self.fixed_transactions_frame, text="Mark as Paid", command=self.mark_as_paid, bg="#4CAF50", fg="white").grid(row=1, column=10, padx=5)

        # Fixed Transactions Table with Scrollbar
        self.fixed_transactions_table = ttk.Treeview(self.fixed_transactions_frame, columns=("name", "amount", "day", "type", "last_paid"), show="headings", height=4)
        for col, heading in [("name", "Name"), ("amount", "Amount (₹)"), ("day", "Day"), ("type", "Type"), ("last_paid", "Last Paid")]:
            self.fixed_transactions_table.heading(col, text=heading)
            self.fixed_transactions_table.column(col, width=100, anchor=CENTER)
        self.fixed_transactions_table.grid(row=2, column=0, columnspan=11, pady=5, sticky="nsew")
        scrollbar = ttk.Scrollbar(self.fixed_transactions_frame, orient=VERTICAL, command=self.fixed_transactions_table.yview)
        self.fixed_transactions_table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=2, column=11, sticky='ns')

        # Create tables and migrate schema
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS fixed_transactions (
                name TEXT UNIQUE,
                amount REAL,
                day INTEGER,
                type TEXT,
                last_paid_date TEXT
            )
        """)
        
        cols = [col[1] for col in self.cur.execute("PRAGMA table_info(fixed_transactions)")]
        if 'last_paid_date' not in cols:
            self.cur.execute("ALTER TABLE fixed_transactions ADD COLUMN last_paid_date TEXT")
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value REAL
        )
        """)
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            date TEXT,
            type TEXT,
            income REAL,
            expense REAL,
            loan REAL,
            balance REAL,
            month TEXT,
            year TEXT
        )
        """)
        self.con.commit()

        # Load and initial checks
        self.load_fixed_transactions()
        self.check_balance_for_upcoming_transactions()  # show immediate alerts
        self.start_alert_check()
        self.balance = self.get_latest_balance()


        #self.check_monthly_transactions()  

        self.verify_database()


        # Add this after your Search button
        show_all_btn = Button(
            dropdown_frame, 
            text="Show All", 
            command=self.show_all_transactions,  # We'll define this next
            bg="#4CAF50",  # Green color
            fg="white", 
            font=("Arial", 10, "bold"), 
            width=10
        )
        show_all_btn.grid(row=0, column=5, padx=10)  # Adjust column as needed


        # Type selection (only one combo box)
        Label(self.entry_frame, text="Type:", bg="white").grid(row=0, column=0, padx=5)
        self.type_var = StringVar()
        self.type_combo = ttk.Combobox(self.entry_frame, textvariable=self.type_var, 
                                    values=["Salary", "Electricity", "Loan", "Regular Expense", "Other"], 
                                        state="readonly", width=15)
        self.type_combo.grid(row=0, column=1, padx=5)
        self.type_combo.current(0)
        self.type_combo.bind("<<ComboboxSelected>>", self.toggle_other_entry)

        # Entry field for custom type (initially hidden)
        self.other_type_var = StringVar()
        self.other_type_entry = Entry(self.entry_frame, textvariable=self.other_type_var, width=15)
            
        # Move Income and other fields to the right to make space for Other type
        Label(self.entry_frame, text="Income:", bg="white").grid(row=0, column=3, padx=5)  # Changed from column 2 to 3
        self.income_var = StringVar()
        Entry(self.entry_frame, textvariable=self.income_var, width=10).grid(row=0, column=4, padx=5)  # Changed from column 3 to 4

        Label(self.entry_frame, text="Expense:", bg="white").grid(row=0, column=5, padx=5)  # Changed from column 4 to 5
        self.expense_var = StringVar()
        Entry(self.entry_frame, textvariable=self.expense_var, width=10).grid(row=0, column=6, padx=5)  # Changed from column 5 to 6

        Label(self.entry_frame, text="Loan Amount:", bg="white").grid(row=0, column=7, padx=5)  # Changed from column 6 to 7
        self.loan_var = StringVar()
        Entry(self.entry_frame, textvariable=self.loan_var, width=10).grid(row=0, column=8, padx=5)  # Changed from column 7 to 8

        Button(self.entry_frame, text="Add Entry", command=self.add_entry, bg="#e50000", fg="white").grid(row=0, column=9, padx=10)  # Changed from column 8 to 9

        # Table Frame
        table_frame = Frame(self.root)
        table_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        columns = ("datetime", "type", "income", "expense", "loan", "balance")
        self.cashflow_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.cashflow_table.heading("datetime", text="Date & Time")
        self.cashflow_table.heading("type", text="Type")
        self.cashflow_table.heading("income", text="Income (₹)")
        self.cashflow_table.heading("expense", text="Expense (₹)")
        self.cashflow_table.heading("loan", text="Loan Amount (₹)")
        self.cashflow_table.heading("balance", text="Current Balance (₹)")

        self.cashflow_table.pack(fill=BOTH, expand=True)


        # Initialize balance from settings
        self.balance = self.get_latest_balance()   # Add this line


        # Add this to your cashflowClass initialization
        self.cur.execute("SELECT value FROM settings WHERE key='initial_balance'")
        if self.cur.fetchone() is None:
            self.cur.execute("INSERT INTO settings (key, value) VALUES ('initial_balance', 0)")
            self.con.commit()

        # Ensure 'settings' table exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value REAL
        )
        """)

        # Ensure 'transactions' table exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            date TEXT,
            type TEXT,
            income REAL,
            expense REAL,
            loan REAL,
            balance REAL,
            month TEXT,
            year TEXT
        )
        """)
            
        self.verify_database()  # Add this if you want automatic verification
        self.load_transactions()




    def show_alert(self, message):
        # Display the alert message on the UI
        self.alert_label.config(text=message)
        if not self.alert_frame.winfo_ismapped():
            self.alert_frame.pack(fill=X)

    def hide_alert(self):
        # Hide the alert area
        self.alert_label.config(text='')
        if self.alert_frame.winfo_ismapped():
            self.alert_frame.pack_forget()


    

    def verify_balance_consistency(self):
        self.cur.execute("SELECT balance FROM transactions ORDER BY date DESC LIMIT 1")
        last_stored = self.cur.fetchone()
        calculated = self.get_latest_balance()
        
        if last_stored and abs(last_stored[0] - calculated) > 0.01:
            messagebox.showwarning("Balance Mismatch", 
                                f"Stored: {last_stored[0]:.2f} vs Calculated: {calculated:.2f}")



    def mark_as_paid(self):
        selected = self.fixed_transactions_table.selection()
        if not selected:
            return
            
        item = self.fixed_transactions_table.item(selected[0])
        values = item['values']
        try:
            name = values[0]
            amount = float(values[1])  # Convert string to float
            day = int(values[2])       # Convert string to integer
            trans_type = values[3]
            # Add balance check before payment
            current_balance = self.get_latest_balance()
            if trans_type == "Expense":
                new_balance = current_balance - amount
                if new_balance < 0:
                    if not messagebox.askyesno("Confirm", f"Paying {name} will make balance negative (₹{new_balance:.2f}). Continue?"):
                        return


        except (ValueError, IndexError) as e:
            messagebox.showerror("Data Error", f"Invalid transaction data: {str(e)}")
            return
        
        # Get current year/month but use the transaction's day
        now = datetime.datetime.now()
        try:
            scheduled_date = datetime.datetime(now.year, now.month, day)
        except ValueError:
            # Handle invalid day for current month
            last_day = (datetime.datetime(now.year, now.month + 1, 1) - timedelta(days=1)).day
            scheduled_date = datetime.datetime(now.year, now.month, last_day)
        
        # Update last_paid_date with actual payment time
        new_last_paid = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.cur.execute("UPDATE fixed_transactions SET last_paid_date=? WHERE name=?", 
                    (new_last_paid, name))
        
        # Add to transactions with SCHEDULED DATE
        self.add_fixed_transaction_to_paid(name, amount, trans_type)
        self.load_fixed_transactions()    
        self.load_transactions()



    def add_fixed_transaction_to_paid(self, name, amount, trans_type):
        # Use actual payment datetime
        paid_datetime = datetime.datetime.now()
        
        current_balance = self.get_latest_balance()
        if trans_type == "Income":
            new_balance = current_balance + amount
            income, expense = amount, 0
        else:
            new_balance = current_balance - amount
            income, expense = 0, amount
        
        entry = (
            paid_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            name,
            income,
            expense,
            0,
            new_balance,
            paid_datetime.strftime("%B"),
            str(paid_datetime.year)
        )
        
        self.cur.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", entry)
        self.con.commit()
        self.balance = new_balance
        self.show_all_transactions()






    def add_fixed_transaction(self):
        try:
            name = self.fixed_name_var.get().strip()
            amount = float(self.fixed_amount_var.get())
            day = self.fixed_day_var.get()
            trans_type = self.fixed_type_var.get()

            if not name:
                messagebox.showwarning("Input Error", "Please enter a name for the transaction")
                return

            if day < 1 or day > 31:
                messagebox.showwarning("Input Error", "Day must be between 1-31")
                return

            # Insert with NULL for last_paid_date
            self.cur.execute("INSERT INTO fixed_transactions VALUES (?, ?, ?, ?, ?)",
                        (name, amount, day, trans_type, None))  # Added None for last_paid_date
            self.con.commit()
            self.load_fixed_transactions()

            # Clear input fields
            self.fixed_name_var.set("")
            self.fixed_amount_var.set("")
            self.fixed_day_var.set(1)

        except ValueError:
            messagebox.showerror("Input Error", "Invalid amount format")



    def delete_fixed_transaction(self):
        selected = self.fixed_transactions_table.selection()
        if not selected:
            return
            
        item = self.fixed_transactions_table.item(selected[0])
        name = item['values'][0]
        
        self.cur.execute("DELETE FROM fixed_transactions WHERE name=?", (name,))
        self.con.commit()
        self.load_fixed_transactions()

    def load_fixed_transactions(self):
        for item in self.fixed_transactions_table.get_children():
            self.fixed_transactions_table.delete(item)
            
        self.cur.execute("SELECT * FROM fixed_transactions")
        for row in self.cur.fetchall():
            self.fixed_transactions_table.insert("", "end", values=row)

    


    def start_alert_check(self):
        def check():
            self.check_balance_for_upcoming_transactions()
            # Calculate time until next midnight
            now = datetime.datetime.now()
            next_day = now + timedelta(days=1)
            midnight = datetime.datetime.combine(next_day.date(), datetime.time(0, 0))
            wait_ms = (midnight - now).total_seconds() * 1000
            self.root.after(int(wait_ms), check)
        
        # Initial check
        check()


    def check_balance_for_upcoming_transactions(self):
        now = datetime.datetime.now()
        current_day = now.day
        current_month_year = now.strftime("%Y-%m")
        
        # Get all unpaid fixed transactions for current month
        self.cur.execute("""
            SELECT name, amount, type, day 
            FROM fixed_transactions 
            WHERE day <= ? 
            AND (last_paid_date IS NULL OR strftime('%Y-%m', last_paid_date) != ?)
        """, (current_day + 1, current_month_year))  # +1 to show alert 1 day before
        
        upcoming_transactions = self.cur.fetchall()
        current_balance = self.get_latest_balance()
        
        if upcoming_transactions:
            alert_lines = [
                "Pending Scheduled Payments:",
                f"Current Balance: ₹{current_balance:.2f}",
                "--------------------------------------"
            ]
            
            today = datetime.datetime.now().date()
            total_planned = 0
            
            for name, amount, trans_type, day in upcoming_transactions:
                due_date = datetime.date(now.year, now.month, day)
                status = "Tomorrow" if day == (now + timedelta(days=1)).day else "Overdue" if due_date < today else f"Due {due_date.strftime('%d %b')}"
                
                alert_lines.append(f"• {name}: ₹{amount:.2f} ({trans_type}) - {status}")
                
                if trans_type == "Expense":
                    total_planned += amount

            # Add balance warning if needed
            if total_planned > current_balance:
                alert_lines.append(f"\n⚠️ WARNING: Insufficient balance for expenses (₹{total_planned:.2f} planned)")
            
            self.show_alert("\n".join(alert_lines))
        else:
            self.hide_alert()














    def show_all_transactions(self):
        # Clear existing data
        for item in self.cashflow_table.get_children():
            self.cashflow_table.delete(item)

        # Fetch transactions with stored balances
        self.cur.execute("""
            SELECT date, type, income, expense, loan, balance 
            FROM transactions 
            ORDER BY date
        """)
        transactions = self.cur.fetchall()

        # Display stored balances directly
        for date, type_, income, expense, loan, balance in transactions:
            self.cashflow_table.insert("", "end", values=(
                date, type_, 
                f"₹{income:.2f}", 
                f"₹{expense:.2f}", 
                f"₹{loan:.2f}", 
                f"₹{balance:.2f}"
            ))

        self.verify_balance_consistency()

    def set_initial_balance(self):
        dialog = Toplevel(self.root)
        dialog.title("Set Initial Balance")
        dialog.grab_set()

        Label(dialog, text="New Initial Balance:", font=("Arial", 12)).pack(pady=10)
        
        balance_var = StringVar()
        Entry(dialog, textvariable=balance_var, font=("Arial", 12)).pack(pady=5)

        def save_balance():
            try:
                new_balance = float(balance_var.get())
                self.cur.execute("""
                    INSERT OR REPLACE INTO settings (key, value)
                    VALUES ('initial_balance', ?)
                """, (new_balance,))
                self.con.commit()
                messagebox.showinfo("Success", "Initial balance updated")
                dialog.destroy()
                self.show_all_transactions()  # Refresh view
            except ValueError:
                messagebox.showerror("Error", "Invalid number format")

        Button(dialog, text="Save", command=save_balance, bg="#4CAF50", fg="white").pack(pady=10)


    def verify_database(self):
        """Verify database structure"""
        print("Transactions table structure:")
        print(self.cur.execute("PRAGMA table_info(transactions)").fetchall())
        print("\nSettings table structure:")
        print(self.cur.execute("PRAGMA table_info(settings)").fetchall())
    

    def load_transactions(self):
        for item in self.cashflow_table.get_children():
            self.cashflow_table.delete(item)
        
        # Get initial balance
        self.cur.execute("SELECT value FROM settings WHERE key='initial_balance'")
        current_balance = float(self.cur.fetchone()[0])
        
        # Fetch all transactions ordered by date
        self.cur.execute("SELECT date, type, income, expense, loan FROM transactions ORDER BY date")
        transactions = self.cur.fetchall()
        
        for date, type_, income, expense, loan in transactions:
            current_balance += income - expense - loan
            self.cashflow_table.insert("", "end", values=(
                date, type_, income, expense, loan, current_balance
            ))


        # Check and insert initial_balance if not set
            self.cur.execute("SELECT value FROM settings WHERE key='initial_balance'")
            if self.cur.fetchone() is None:
                self.cur.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("initial_balance", 0.0))
                self.con.commit()
        pass


    def toggle_other_entry(self, event=None):
        if self.type_var.get() == "Other":
            self.other_type_entry.grid(row=0, column=2, padx=5)  # Now appears in column 2
        else:
            self.other_type_entry.grid_remove()
            self.other_type_var.set("")

    def add_entry(self):
        try:
            # Get current datetime and date parts
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d %H:%M:%S")
            month = now.strftime("%B")  # Full month name
            year = now.strftime("%Y")   # 4-digit year

            # Validate type
            if self.type_var.get() == "Other":
                entry_type = self.other_type_var.get().strip()
                if not entry_type:
                    messagebox.showwarning("Input Error", "Please enter a custom type for 'Other'")
                    return
            else:
                entry_type = self.type_var.get()

            # Validate numeric inputs
            try:
                income = max(0.0, float(self.income_var.get() or 0))
                expense = max(0.0, float(self.expense_var.get() or 0))
                loan = max(0.0, float(self.loan_var.get() or 0))
            except ValueError:
                messagebox.showerror("Error", "Values must be non-negative numbers")
                return

            # Get current balance and calculate new balance
            current_balance = self.get_latest_balance()
            new_balance = current_balance + income - expense - loan

            # Prevent negative balance
            if (expense > 0 or loan > 0) and new_balance < 0:
                if not messagebox.askyesno("Confirm", "Balance will go negative. Continue?"):
                    return

            # Update balance and proceed
            self.balance = new_balance


            # Create complete entry with all 8 values
            entry = (date_str, entry_type, income, expense, loan, self.balance, month, year)

            # Insert into database
            self.cur.execute("""
            INSERT INTO transactions (date, type, income, expense, loan, balance, month, year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, entry)
            self.con.commit()

            # Add to table (showing only first 6 columns)
            self.cashflow_table.insert("", "end", values=entry[:6])  # Proper insertion

            # Reset form
            self.type_var.set("Salary")
            self.other_type_var.set("")
            self.income_var.set("")
            self.expense_var.set("")
            self.loan_var.set("")
            self.toggle_other_entry()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.con.rollback()

            # Validate numerical values
        try:
            income = max(0.0, float(self.income_var.get() or 0))
            expense = max(0.0, float(self.expense_var.get() or 0))
            loan = max(0.0, float(self.loan_var.get() or 0))
        except ValueError:
            messagebox.showerror("Error", "Values must be non-negative numbers")
            return
    
        # Prevent negative balance
        new_balance = current_balance + income - expense - loan
        if (expense > 0 or loan > 0) and new_balance < 0:
            if not messagebox.askyesno("Confirm", "Balance will go negative. Continue?"):
                return
    
        self.con.commit()
        self.verify_balance_consistency()  # <-- Add this line
        #self.cashflow_table.insert(...)

    def get_latest_balance(self):
        # Check for latest transaction balance
        self.cur.execute("SELECT balance FROM transactions ORDER BY date DESC LIMIT 1")
        last = self.cur.fetchone()
    
        if last:  # If transactions exist
            return float(last[0])
        else:  # No transactions - get initial balance
            self.cur.execute("SELECT value FROM settings WHERE key='initial_balance'")
            initial = self.cur.fetchone()
            return float(initial[0]) if initial else 0.0



    def filter_by_month(self):
        selected_year = self.year_var.get()
        selected_month = self.month_var.get()
        
        try:
            month_num = datetime.datetime.strptime(selected_month, "%B").month
        except ValueError:
            messagebox.showerror("Error", "Invalid month selected")
            return
        
        # Clear table
        for item in self.cashflow_table.get_children():
            self.cashflow_table.delete(item)
        
        # Get initial balance from settings
        self.cur.execute("SELECT value FROM settings WHERE key='initial_balance'")
        initial_balance = float(self.cur.fetchone()[0])
        
        # Calculate sum of transactions before selected month/year
        sum_before_query = """
        SELECT SUM(income - expense - loan) 
        FROM transactions 
        WHERE 
            (year < ?) OR 
            (year = ? AND 
                (CASE month
                    WHEN 'January' THEN 1
                    WHEN 'February' THEN 2
                    WHEN 'March' THEN 3
                    WHEN 'April' THEN 4
                    WHEN 'May' THEN 5
                    WHEN 'June' THEN 6
                    WHEN 'July' THEN 7
                    WHEN 'August' THEN 8
                    WHEN 'September' THEN 9
                    WHEN 'October' THEN 10
                    WHEN 'November' THEN 11
                    WHEN 'December' THEN 12
                END) < ?)
        """
        self.cur.execute(sum_before_query, (selected_year, selected_year, month_num))
        sum_before = self.cur.fetchone()[0] or 0.0
        current_balance = initial_balance + sum_before
        
        # Fetch and process selected month's transactions
        self.cur.execute("""
            SELECT date, type, income, expense, loan 
            FROM transactions 
            WHERE month=? AND year=?
            ORDER BY date
        """, (selected_month, selected_year))
        transactions = self.cur.fetchall()
        
        # Single processing loop
        for date, type_, income, expense, loan in transactions:
            current_balance += income - expense - loan
            self.cashflow_table.insert("", "end", values=(
                date, type_, income, expense, loan, current_balance
            ))

if __name__ == "__main__":
    root = Tk()
    obj = cashflowClass(root)
    root.mainloop()

