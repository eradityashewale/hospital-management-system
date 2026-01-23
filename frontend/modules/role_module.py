"""
User Management Module
Allows admin to create and manage users with direct module permissions
"""
import tkinter as tk
from tkinter import ttk, messagebox

# Backend imports
from backend.database import Database

# Utils imports
from utils.logger import (log_button_click, log_dialog_open, log_dialog_close, 
                   log_database_operation, log_error, log_info, log_warning, log_debug)


class RoleModule:
    """User management interface - renamed from RoleModule for backward compatibility"""
    
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db
        # Get root window for focus management
        self.root = parent.winfo_toplevel()
        
        self.create_ui()
        # Defer refresh to make UI appear faster
        self.parent.after(10, self.refresh_list)
    
    def create_ui(self):
        """Create user interface"""
        # Header with modern styling
        header = tk.Label(
            self.parent,
            text="User Management",
            font=('Segoe UI', 24, 'bold'),
            bg='#f5f7fa',
            fg='#1a237e'
        )
        header.pack(pady=20)
        
        # Description
        desc_label = tk.Label(
            self.parent,
            text="Create and manage users with direct module access permissions",
            font=('Segoe UI', 11),
            bg='#f5f7fa',
            fg='#6b7280'
        )
        desc_label.pack(pady=(0, 20))
        
        # Top frame for add button
        top_frame = tk.Frame(self.parent, bg='#f5f7fa')
        top_frame.pack(fill=tk.X, padx=25, pady=15)
        
        # Add user button
        add_user_btn = tk.Button(
            top_frame,
            text="+ Create New User",
            command=self.add_user,
            font=('Segoe UI', 11, 'bold'),
            bg='#3b82f6',
            fg='white',
            padx=25,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#2563eb',
            activeforeground='white'
        )
        add_user_btn.pack(side=tk.RIGHT, padx=10)
        
        # Container for list
        content_container = tk.Frame(self.parent, bg='#f5f7fa')
        content_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
        
        # List frame
        list_frame = tk.Frame(content_container, bg='#f5f7fa')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for user list
        columns = ('Username', 'Full Name', 'Email', 'Permissions')
        
        # Configure style
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
        
        style.configure("Treeview", 
                       font=('Segoe UI', 10), 
                       rowheight=35, 
                       background='white', 
                       foreground='#374151',
                       fieldbackground='white')
        style.configure("Treeview.Heading", 
                       font=('Segoe UI', 11, 'bold'), 
                       background='#6366f1', 
                       foreground='white',
                       relief=tk.FLAT)
        style.map("Treeview.Heading",
                 background=[('active', '#4f46e5')])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', 
                                height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Configure columns
        self.tree.heading('Username', text='Username')
        self.tree.heading('Full Name', text='Full Name')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Permissions', text='Module Permissions')
        
        self.tree.column('Username', width=150, anchor=tk.W)
        self.tree.column('Full Name', width=200, anchor=tk.W)
        self.tree.column('Email', width=200, anchor=tk.W)
        self.tree.column('Permissions', width=300, anchor=tk.W)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind double-click to edit
        self.tree.bind('<Double-1>', lambda e: self.edit_user())
        
        # Right-click context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit User", command=self.edit_user)
        self.context_menu.add_command(label="Delete User", command=self.delete_user)
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Action buttons frame
        button_frame = tk.Frame(content_container, bg='#f5f7fa')
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        edit_btn = tk.Button(
            button_frame,
            text="Edit User",
            command=self.edit_user,
            font=('Segoe UI', 10, 'bold'),
            bg='#6366f1',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#4f46e5',
            activeforeground='white'
        )
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(
            button_frame,
            text="Delete User",
            command=self.delete_user,
            font=('Segoe UI', 10, 'bold'),
            bg='#ef4444',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#dc2626',
            activeforeground='white'
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        try:
            item = self.tree.selection()[0]
            self.context_menu.post(event.x_root, event.y_root)
        except IndexError:
            pass
    
    def refresh_list(self):
        """Refresh the user list"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Fetch users from database
            users = self.db.get_all_users()
            
            # Add users to treeview
            for user in users:
                permissions = user.get('permissions', [])
                permissions_str = ', '.join([p.capitalize() for p in permissions]) if permissions else 'No permissions'
                
                self.tree.insert('', tk.END, values=(
                    user['username'],
                    user.get('full_name', ''),
                    user.get('email', ''),
                    permissions_str
                ), tags=(user['id'],))
            
            log_info(f"Refreshed user list: {len(users)} users")
        except Exception as e:
            log_error("Error refreshing user list", e)
            messagebox.showerror("Error", f"Failed to refresh user list: {str(e)}")
    
    def add_user(self):
        """Open dialog to add a new user"""
        log_button_click("Add User")
        self.user_dialog(None)
    
    def edit_user(self):
        """Open dialog to edit selected user"""
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a user to edit")
                return
            
            item = self.tree.item(selected[0])
            tags = item['tags']
            if not tags:
                messagebox.showerror("Error", "Could not find user ID")
                return
            
            user_id = int(tags[0])
            log_button_click(f"Edit User: {user_id}")
            
            # Get user details
            user = self.db.get_user_by_id(user_id)
            if not user:
                messagebox.showerror("Error", "User not found")
                return
            
            self.user_dialog(user)
        except Exception as e:
            log_error("Error editing user", e)
            messagebox.showerror("Error", f"Failed to edit user: {str(e)}")
    
    def user_dialog(self, user_data=None):
        """Dialog for creating/editing a user"""
        is_edit = user_data is not None
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit User" if is_edit else "Create New User")
        dialog.geometry("550x750")
        dialog.configure(bg='#f5f7fa')
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (750 // 2)
        dialog.geometry(f'550x750+{x}+{y}')
        
        log_dialog_open("User Dialog")
        
        # Main container
        main_container = tk.Frame(dialog, bg='#f5f7fa')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Form frame with scrollbar
        form_frame = tk.Frame(main_container, bg='white', relief=tk.FLAT, bd=1, 
                             highlightbackground='#e5e7eb', highlightthickness=1)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(form_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", update_scroll_region)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mousewheel to canvas
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        inner_frame = scrollable_frame
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Update scroll region after widgets are created
        def update_after_creation():
            dialog.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        dialog.after(100, update_after_creation)
        
        # Username
        tk.Label(inner_frame, text="Username *", font=('Segoe UI', 11, 'bold'),
                bg='white', fg='#374151', anchor='w').pack(fill=tk.X, pady=(0, 5))
        username_var = tk.StringVar(value=user_data['username'] if is_edit else '')
        username_entry = tk.Entry(inner_frame, textvariable=username_var,
                                 font=('Segoe UI', 11), width=40)
        username_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Full Name
        tk.Label(inner_frame, text="Full Name", font=('Segoe UI', 11, 'bold'),
                bg='white', fg='#374151', anchor='w').pack(fill=tk.X, pady=(0, 5))
        full_name_var = tk.StringVar(value=user_data.get('full_name', '') if is_edit else '')
        full_name_entry = tk.Entry(inner_frame, textvariable=full_name_var,
                                   font=('Segoe UI', 11), width=40)
        full_name_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Email
        tk.Label(inner_frame, text="Email *", font=('Segoe UI', 11, 'bold'),
                bg='white', fg='#374151', anchor='w').pack(fill=tk.X, pady=(0, 5))
        email_var = tk.StringVar(value=user_data.get('email', '') if is_edit else '')
        email_entry = tk.Entry(inner_frame, textvariable=email_var,
                              font=('Segoe UI', 11), width=40)
        email_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Password
        tk.Label(inner_frame, text="Password *", font=('Segoe UI', 11, 'bold'),
                bg='white', fg='#374151', anchor='w').pack(fill=tk.X, pady=(0, 5))
        password_var = tk.StringVar()
        password_entry = tk.Entry(inner_frame, textvariable=password_var,
                                 font=('Segoe UI', 11), width=40, show='*')
        password_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        if is_edit:
            tk.Label(inner_frame, text="(Leave blank to keep current password)",
                    font=('Segoe UI', 9), bg='white', fg='#6b7280', anchor='w').pack(fill=tk.X, pady=(0, 10))
        
        # Module permissions - Direct assignment
        tk.Label(inner_frame, text="Module Access Permissions *", font=('Segoe UI', 11, 'bold'),
                bg='white', fg='#374151', anchor='w').pack(fill=tk.X, pady=(0, 5))
        
        # Help text
        tk.Label(inner_frame, text="Select which modules this user can access:",
                font=('Segoe UI', 9), bg='white', fg='#6b7280', anchor='w').pack(fill=tk.X, pady=(0, 10))
        
        # Permissions frame with border
        permissions_container = tk.Frame(inner_frame, bg='white')
        permissions_container.pack(fill=tk.X, pady=(0, 15))
        
        # Create a frame with border for permissions
        permissions_frame = tk.Frame(permissions_container, bg='#f9fafb', relief=tk.SOLID, bd=1,
                                     highlightbackground='#e5e7eb', highlightthickness=1)
        permissions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        modules = [
            ('patient', 'Patient Management'),
            ('doctor', 'Doctor Management'),
            ('appointments', 'Appointments'),
            ('prescription', 'Prescriptions'),
            ('billing', 'Billing'),
            ('report', 'Reports')
        ]
        permission_vars = {}
        
        # Get current permissions if editing
        current_permissions = []
        if is_edit:
            current_permissions = self.db.get_user_permissions(user_data['id'])
        
        # Create checkboxes in a 2-column grid for better visibility
        row = 0
        col = 0
        for module_key, module_label in modules:
            var = tk.BooleanVar()
            if is_edit:
                var.set(module_key in current_permissions)
            permission_vars[module_key] = var
            
            check = tk.Checkbutton(
                permissions_frame,
                text=module_label,
                variable=var,
                font=('Segoe UI', 10),
                bg='#f9fafb',
                fg='#374151',
                activebackground='#f9fafb',
                activeforeground='#6366f1',
                selectcolor='white',
                anchor='w',
                padx=10,
                pady=8
            )
            check.grid(row=row, column=col, sticky='w', padx=15, pady=8)
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        # Configure grid weights so columns expand properly
        permissions_frame.grid_columnconfigure(0, weight=1)
        permissions_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons - Fixed at bottom outside scrollable area
        button_frame = tk.Frame(main_container, bg='#f5f7fa')
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        def save_user():
            username = username_var.get().strip()
            full_name = full_name_var.get().strip()
            email = email_var.get().strip()
            password = password_var.get()
            permissions = [mod for mod, var in permission_vars.items() if var.get()]
            
            if not username:
                messagebox.showwarning("Validation Error", "Username is required")
                return
            
            if not email:
                messagebox.showwarning("Validation Error", "Email is required")
                return
            
            if not is_edit and not password:
                messagebox.showwarning("Validation Error", "Password is required")
                return
            
            if not permissions:
                messagebox.showwarning("Validation Error", "At least one module permission must be selected")
                return
            
            try:
                if is_edit:
                    # Update user
                    update_data = {
                        'username': username,
                        'full_name': full_name,
                        'email': email
                    }
                    if password:
                        update_data['password'] = password
                    
                    success = self.db.update_user(user_data['id'], **update_data)
                    if success:
                        # Update permissions
                        self.db.set_user_permissions(user_data['id'], permissions)
                        messagebox.showinfo("Success", "User updated successfully")
                        log_database_operation("UPDATE", "users", True, f"User ID: {user_data['id']}")
                    else:
                        messagebox.showerror("Error", "Failed to update user")
                else:
                    # Create user with direct permissions
                    user_id = self.db.create_user(username, password, full_name, email, permissions)
                    if user_id:
                        messagebox.showinfo("Success", f"User created successfully!\n\nUsername: {username}\nPassword: {password}\n\nUser can now login with these credentials.\n\nUser will only see: {', '.join([m.capitalize() for m in permissions])}")
                        log_database_operation("INSERT", "users", True, f"User: {username}")
                    else:
                        messagebox.showerror("Error", "Failed to create user. Username may already exist.")
                
                dialog.destroy()
                self.refresh_list()
            except Exception as e:
                log_error("Error saving user", e)
                messagebox.showerror("Error", f"Failed to save user: {str(e)}")
        
        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=save_user,
            font=('Segoe UI', 11, 'bold'),
            bg='#10b981',
            fg='white',
            padx=25,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#059669',
            activeforeground='white'
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            font=('Segoe UI', 11),
            bg='#6b7280',
            fg='white',
            padx=25,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#4b5563',
            activeforeground='white'
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Focus on username entry
        username_entry.focus()
        
        def on_closing():
            log_dialog_close("User Dialog")
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_closing)
    
    def delete_user(self):
        """Delete selected user"""
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a user to delete")
                return
            
            item = self.tree.item(selected[0])
            tags = item['tags']
            if not tags:
                messagebox.showerror("Error", "Could not find user ID")
                return
            
            user_id = int(tags[0])
            username = item['values'][0]
            
            # Confirm deletion
            if not messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete user '{username}'?\n\n"
                                      "This action cannot be undone."):
                return
            
            log_button_click(f"Delete User: {user_id}")
            
            success = self.db.delete_user(user_id)
            if success:
                messagebox.showinfo("Success", "User deleted successfully")
                log_database_operation("DELETE", "users", True, f"User ID: {user_id}")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Failed to delete user")
        except Exception as e:
            log_error("Error deleting user", e)
            messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
