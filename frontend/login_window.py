"""
Login Window Module for Hospital Management System
Handles user authentication before accessing the main application
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Backend imports
from backend.database import Database

# Utils imports
from utils.logger import log_info, log_error, log_warning, log_debug


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
        self.root.title("MediFlow - Login")
        self.root.geometry("450x700")
        self.root.configure(bg='#f5f7fa')
        self.root.resizable(False, False)
        self.root.minsize(450, 700)
        
        # Set window icon for branding
        self.set_window_icon()
        
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
    
    def set_window_icon(self):
        """Set the window icon for branding - supports PNG and ICO"""
        try:
            # Determine the icon path - works for both development and compiled versions
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
            else:
                # In development, look in assets folder relative to project root
                current_file = os.path.abspath(__file__)
                project_root = os.path.dirname(os.path.dirname(current_file))
                base_path = os.path.join(project_root, 'assets')
            
            # Try different logo file names in order of preference
            possible_icons = [
                'icon.ico',
                'logo.ico',
                'icon.png',
                'logo.png',
                'hospital_logo.png'
            ]
            
            icon_path = None
            for icon_name in possible_icons:
                icon_path = os.path.join(base_path, icon_name)
                if os.path.exists(icon_path):
                    break
            
            # Fallback: try in project root (for backward compatibility)
            if not icon_path and not getattr(sys, 'frozen', False):
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                for icon_name in possible_icons:
                    icon_path = os.path.join(project_root, icon_name)
                    if os.path.exists(icon_path):
                        break
            
            if icon_path and os.path.exists(icon_path):
                # If it's a PNG, convert to ICO for window icon, or use temp ICO
                if icon_path.lower().endswith('.png'):
                    try:
                        # Try to convert PNG to temp ICO for window icon
                        from PIL import Image
                        img = Image.open(icon_path)
                        temp_ico = os.path.join(os.path.dirname(icon_path), 'temp_icon.ico')
                        # Create ICO with multiple sizes
                        sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
                        images = [img.resize(size, Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS) for size in sizes]
                        images[0].save(temp_ico, format='ICO', sizes=[(s[0], s[1]) for s in sizes])
                        self.root.iconbitmap(temp_ico)
                        log_info(f"Login window icon set from PNG: {icon_path}")
                        # Clean up temp file after a delay
                        self.root.after(1000, lambda: os.remove(temp_ico) if os.path.exists(temp_ico) else None)
                    except Exception as e:
                        log_debug(f"Could not convert PNG to ICO for window icon: {e}")
                else:
                    # It's already an ICO file
                    self.root.iconbitmap(icon_path)
                    log_info(f"Login window icon set: {icon_path}")
            else:
                log_debug("Icon file not found - using default icon")
        except Exception as e:
            log_error("Failed to set login window icon", e)
            # Don't fail the application if icon can't be set
    
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
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_login_ui(self):
        """Create login UI elements"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#f5f7fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Header with logo
        header_frame = tk.Frame(main_frame, bg='#1e3a8a', relief=tk.FLAT, bd=0)
        header_frame.pack(fill=tk.X, pady=0, padx=0)
        
        # Logo container
        logo_container = tk.Frame(header_frame, bg='#1e3a8a')
        logo_container.pack(pady=25)
        
        # Try to load actual logo image (PNG or ICO), fallback to text
        logo_image = None
        logo_path = None
        
        try:
            # Determine base path
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
            else:
                # In development, look in assets folder relative to project root
                current_file = os.path.abspath(__file__)
                project_root = os.path.dirname(os.path.dirname(current_file))
                base_path = os.path.join(project_root, 'assets')
            
            # Try different logo file names in order of preference
            possible_logos = [
                'logo.png',
                'hospital_logo.png', 
                'icon.png',
                'icon.ico',
                'logo.ico'
            ]
            
            logo_path = None
            for logo_name in possible_logos:
                logo_path = os.path.join(base_path, logo_name)
                if os.path.exists(logo_path):
                    break
            
            # Fallback: try in project root (for backward compatibility)
            if not logo_path and not getattr(sys, 'frozen', False):
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                for logo_name in possible_logos:
                    logo_path = os.path.join(project_root, logo_name)
                    if os.path.exists(logo_path):
                        break
            
            if logo_path and os.path.exists(logo_path):
                # Load and resize logo image for display
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(logo_path)
                    # Convert RGBA to RGB if needed for better compatibility
                    if img.mode == 'RGBA':
                        # Create white background
                        bg = Image.new('RGB', img.size, (255, 255, 255))
                        bg.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                        img = bg
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Resize to 80x80 for login window
                    img = img.resize((80, 80), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)
                    logo_image = ImageTk.PhotoImage(img)
                    log_info(f"Loaded logo image: {logo_path}")
                except ImportError:
                    log_debug("PIL/Pillow not available - using text logo")
                    logo_image = None
                except Exception as e:
                    log_error(f"Could not load logo image from {logo_path}: {e}")
                    logo_image = None
            else:
                log_debug("No logo file found (looking for logo.png, hospital_logo.png, icon.png, or icon.ico)")
        except Exception as e:
            log_debug(f"Error checking for logo: {e}")
            logo_image = None
        
        # Display logo (image or text fallback)
        if logo_image:
            logo_icon_label = tk.Label(
                logo_container,
                image=logo_image,
                bg='#1e3a8a'
            )
            logo_icon_label.image = logo_image  # Keep a reference
            logo_icon_label.pack(pady=(0, 10))
        else:
            # Fallback to styled medical cross
            logo_icon = tk.Label(
                logo_container,
                text="✚",
                font=('Segoe UI', 48, 'bold'),
                bg='#1e3a8a',
                fg='white'
            )
            logo_icon.pack(pady=(0, 10))
        
        # Product name
        product_label = tk.Label(
            logo_container,
            text="MediFlow",
            font=('Segoe UI', 32, 'bold'),
            bg='#1e3a8a',
            fg='white'
        )
        product_label.pack(pady=(0, 5))
        
        # Tagline
        tagline_label = tk.Label(
            logo_container,
            text="HOSPITAL MANAGEMENT SYSTEM",
            font=('Segoe UI', 9, 'bold'),
            bg='#1e3a8a',
            fg='#93c5fd'
        )
        tagline_label.pack(pady=(0, 0))
        
        # Company name below header
        company_frame = tk.Frame(main_frame, bg='#f5f7fa')
        company_frame.pack(fill=tk.X, pady=(15, 5))
        
        company_label = tk.Label(
            company_frame,
            text="Powered by Nexvora Solutions",
            font=('Segoe UI', 10, 'italic'),
            bg='#f5f7fa',
            fg='#6366f1'
        )
        company_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(
            company_frame,
            text="Please login to continue",
            font=('Segoe UI', 11),
            bg='#f5f7fa',
            fg='#6b7280'
        )
        subtitle_label.pack(pady=(5, 20))
        
        # Login form container - make it visible and properly sized
        form_frame = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1, highlightbackground='#e5e7eb', highlightthickness=1)
        form_frame.pack(fill=tk.X, padx=40, pady=(0, 30), ipady=10)
        
        # Add padding inside form
        form_inner = tk.Frame(form_frame, bg='white')
        form_inner.pack(fill=tk.X, padx=30, pady=25)
        
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
        
        # Login button - make it clearly visible
        button_container = tk.Frame(form_inner, bg='white')
        button_container.pack(fill=tk.X, pady=(15, 10))
        
        login_button = tk.Button(
            button_container,
            text="LOGIN",
            font=('Segoe UI', 13, 'bold'),
            bg='#1a237e',
            fg='white',
            activebackground='#3949ab',
            activeforeground='white',
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            padx=30,
            pady=15,
            command=self.attempt_login,
            width=25,
            height=2
        )
        login_button.pack(fill=tk.X, pady=(0, 10))
        login_button.bind('<Enter>', lambda e: login_button.config(bg='#3949ab'))
        login_button.bind('<Leave>', lambda e: login_button.config(bg='#1a237e'))
        
        # Make sure button is on top and visible
        login_button.lift()
        login_button.update_idletasks()
        
        # Error message label (initially hidden) - place before info
        self.error_label = tk.Label(
            form_inner,
            text="",
            font=('Segoe UI', 10, 'bold'),
            bg='white',
            fg='#ef4444',
            wraplength=350,
            justify=tk.CENTER
        )
        self.error_label.pack(fill=tk.X, pady=(5, 10))
        
        # Default credentials info (for initial setup)
        info_frame = tk.Frame(form_inner, bg='white')
        info_frame.pack(fill=tk.X, pady=(5, 0))
        
        info_label = tk.Label(
            info_frame,
            text="Default: admin / admin",
            font=('Segoe UI', 9),
            bg='white',
            fg='#9ca3af',
            cursor='hand2'
        )
        info_label.pack()
        
        # Force update to ensure everything is visible
        form_inner.update_idletasks()
        self.root.update_idletasks()
    
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

