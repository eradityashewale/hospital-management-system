"""
Login Window Module for Hospital Management System
Handles user authentication before accessing the main application
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from logger import log_info, log_error, log_warning


class LoginWindow:
    """Login window for user authentication"""
    
    def __init__(self, root, on_success_callback):
        """
        Initialize login window
        
        Args:
            root: Tkinter root window
            on_success_callback: Callback function to call on successful login
        """
        self.root = root
        self.on_success_callback = on_success_callback
        self.db = Database()
        self.authenticated_user = None
        
        # Configure window
        self.root.title("Hospital Management System - Login")
        self.root.geometry("450x600")
        self.root.configure(bg='#f5f7fa')
        self.root.resizable(False, False)
        self.root.minsize(450, 600)
        
        # Create UI first
        self.create_login_ui()
        
        # Center the window after UI is created
        self.root.update_idletasks()
        self.center_window()
        
        # Make sure window is visible
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.attempt_login())
        
        # Focus on username field
        self.username_entry.focus()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Update window to ensure it's visible
        self.root.update()
        
        log_info("Login window initialized")
    
    def on_closing(self):
        """Handle window closing - exit application if user closes login window"""
        log_info("Login window closed by user")
        self.root.quit()
        self.root.destroy()
    
    def center_window(self):
        """Center the login window on screen"""
        self.root.update_idletasks()
        # Use fixed dimensions since we know the size
        width = 450
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_login_ui(self):
        """Create login UI elements"""
        # Main container with scrollable area if needed
        main_frame = tk.Frame(self.root, bg='#f5f7fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#f5f7fa')
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Hospital icon/emoji
        icon_label = tk.Label(
            header_frame,
            text="🏥",
            font=('Segoe UI', 48),
            bg='#f5f7fa',
            fg='#1a237e'
        )
        icon_label.pack(pady=(0, 10))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Hospital Management System",
            font=('Segoe UI', 20, 'bold'),
            bg='#f5f7fa',
            fg='#1a237e'
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Please login to continue",
            font=('Segoe UI', 11),
            bg='#f5f7fa',
            fg='#6b7280'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Login form container - ensure it's visible
        form_frame = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1, highlightbackground='#e5e7eb', highlightthickness=1)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Add padding inside form
        form_inner = tk.Frame(form_frame, bg='white')
        form_inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        # Username field
        username_label = tk.Label(
            form_inner,
            text="Username",
            font=('Segoe UI', 11, 'bold'),
            bg='white',
            fg='#374151',
            anchor='w'
        )
        username_label.pack(fill=tk.X, pady=(0, 8))
        
        username_container = tk.Frame(form_inner, bg='white')
        username_container.pack(fill=tk.X, pady=(0, 20))
        
        self.username_entry = tk.Entry(
            username_container,
            font=('Segoe UI', 11),
            relief=tk.SOLID,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3b82f6',
            highlightbackground='#d1d5db',
            insertbackground='#374151'
        )
        self.username_entry.pack(fill=tk.X, ipady=10, padx=1, pady=1)
        
        # Password field
        password_label = tk.Label(
            form_inner,
            text="Password",
            font=('Segoe UI', 11, 'bold'),
            bg='white',
            fg='#374151',
            anchor='w'
        )
        password_label.pack(fill=tk.X, pady=(0, 8))
        
        password_container = tk.Frame(form_inner, bg='white')
        password_container.pack(fill=tk.X, pady=(0, 25))
        
        self.password_entry = tk.Entry(
            password_container,
            font=('Segoe UI', 11),
            relief=tk.SOLID,
            bd=1,
            show='*',
            highlightthickness=1,
            highlightcolor='#3b82f6',
            highlightbackground='#d1d5db',
            insertbackground='#374151',
            width=30
        )
        self.password_entry.pack(fill=tk.X, ipady=10, padx=1, pady=1)
        
        # Login button
        login_button = tk.Button(
            form_inner,
            text="Login",
            font=('Segoe UI', 12, 'bold'),
            bg='#1a237e',
            fg='white',
            activebackground='#3949ab',
            activeforeground='white',
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            padx=20,
            pady=12,
            command=self.attempt_login,
            width=20
        )
        login_button.pack(fill=tk.X, pady=(10, 15))
        
        # Default credentials info (for initial setup)
        info_frame = tk.Frame(form_inner, bg='white')
        info_frame.pack(fill=tk.X)
        
        info_label = tk.Label(
            info_frame,
            text="Default: admin / admin",
            font=('Segoe UI', 9),
            bg='white',
            fg='#9ca3af',
            cursor='hand2'
        )
        info_label.pack()
        
        # Error message label (initially hidden)
        self.error_label = tk.Label(
            form_inner,
            text="",
            font=('Segoe UI', 10),
            bg='white',
            fg='#ef4444',
            wraplength=300
        )
        self.error_label.pack(fill=tk.X, pady=(5, 0))
    
    def attempt_login(self):
        """Attempt to authenticate user"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Clear previous error
        self.error_label.config(text="")
        
        # Validate input
        if not username:
            self.show_error("Please enter your username")
            self.username_entry.focus()
            return
        
        if not password:
            self.show_error("Please enter your password")
            self.password_entry.focus()
            return
        
        # Attempt authentication
        try:
            user = self.db.authenticate_user(username, password)
            
            if user:
                self.authenticated_user = user
                log_info(f"Login successful for user: {username}")
                # Call success callback first, then close login window
                if self.on_success_callback:
                    self.on_success_callback(user)
                self.root.quit()
            else:
                self.show_error("Invalid username or password")
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
                log_warning(f"Login failed for username: {username}")
        
        except Exception as e:
            log_error("Error during login", e)
            self.show_error("An error occurred. Please try again.")
            messagebox.showerror("Error", f"Login error: {str(e)}")
    
    def show_error(self, message: str):
        """Display error message"""
        self.error_label.config(text=message)
        self.root.update_idletasks()


def show_login_window(on_success_callback):
    """
    Show login window and return authenticated user
    
    Args:
        on_success_callback: Function to call with authenticated user on success
        
    Returns:
        Authenticated user dict or None
    """
    login_root = tk.Tk()
    login_app = LoginWindow(login_root, on_success_callback)
    login_root.mainloop()
    login_root.destroy()
    
    return login_app.authenticated_user

