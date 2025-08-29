import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ---- Database Connection ----
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Ria_Enterprise"
    )

# ---- Main CRUD Class ----
class CRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enterprise Management System")
        self.root.geometry("1000x700")
        self.root.configure(bg="deeppink")

        style = ttk.Style()
        style.configure("DeepPink.TFrame", background="deeppink")

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.create_tab(notebook, "product", ["ProductID", "ProductName", "Quantity", "MfgDate", "ExpDate"])
        self.create_tab(notebook, "customer", ["CustomerID", "Firstname", "LastName", "City", "LoyaltyPoints"])
        self.create_tab(notebook, "orders", ["OrderID", "CustomerID", "ProductID", "EmpID", "OrderDate", "Quantity"])
        self.create_tab(notebook, "employee", ["EmpID", "EmpName", "Position", "HireDate", "Salary"])
        self.create_tab(notebook, "branches", ["Branch_id", "Branch_name", "Branch_location"])

    # ---- Generic Fetch Function ----
    def fetch_data(self, query, params=()):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return rows

    # ---- Generic Execute Function ----
    def execute_query(self, query, params=()):
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Operation successful")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- Generic Tab Creator ----
    def create_tab(self, notebook, table_name, columns):
        frame = ttk.Frame(notebook, style="pink.TFrame")
        notebook.add(frame, text=table_name.capitalize())

        entries = {}
        for i, col in enumerate(columns):
            label = ttk.Label(frame, text=col)
            label.grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[col] = entry

        # CRUD Buttons
        ttk.Button(frame, text="Add", command=lambda: self.add_record(table_name, columns, entries)).grid(row=0, column=2, padx=5)
        ttk.Button(frame, text="Update", command=lambda: self.update_record(table_name, columns, entries)).grid(row=1, column=2, padx=5)
        ttk.Button(frame, text="Delete", command=lambda: self.delete_record(table_name, columns[0], entries)).grid(row=2, column=2, padx=5)
        ttk.Button(frame, text="View", command=lambda: self.view_records(table_name, tree)).grid(row=3, column=2, padx=5)

        # Treeview
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
        tree.grid(row=len(columns)+1, column=0, columnspan=3, padx=5, pady=5)

        setattr(self, f"{table_name}_entries", entries)
        setattr(self, f"{table_name}_tree", tree)

    def add_record(self, table_name, columns, entries):
        vals = tuple(entries[col].get() for col in columns)
        placeholders = ",".join(["%s"] * len(columns))
        query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        self.execute_query(query, vals)
        self.view_records(table_name, getattr(self, f"{table_name}_tree"))

    def update_record(self, table_name, columns, entries):
        pk = columns[0]
        vals = tuple(entries[col].get() for col in columns)
        set_clause = ",".join([f"{col}=%s" for col in columns[1:]])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {pk}=%s"
        params = vals[1:] + (vals[0],)
        self.execute_query(query, params)
        self.view_records(table_name, getattr(self, f"{table_name}_tree"))

    def delete_record(self, table_name, pk_col, entries):
        pk_val = entries[pk_col].get()
        query = f"DELETE FROM {table_name} WHERE {pk_col}=%s"
        self.execute_query(query, (pk_val,))
        self.view_records(table_name, getattr(self, f"{table_name}_tree"))

    def view_records(self, table_name, tree):
        rows = self.fetch_data(f"SELECT * FROM {table_name}")
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", tk.END, values=row)

# ---- Run ----
root = tk.Tk()
app = CRUDApp(root)
root.mainloop()
