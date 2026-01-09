"""
Helper script to convert image files to Windows .ico format
This script helps you create an icon file from your logo image
"""
import os
import sys

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow (PIL) is not installed!")
    print("\nTo install Pillow, run:")
    print("  pip install Pillow")
    print("\nOr if you prefer, use an online converter:")
    print("  https://convertio.co/png-ico/")
    print("  https://icoconvert.com/")
    sys.exit(1)

def convert_to_ico(input_file, output_file='icon.ico', sizes=None):
    """
    Convert an image file to Windows .ico format
    
    Args:
        input_file: Path to input image (PNG, JPG, etc.)
        output_file: Path to output .ico file (default: icon.ico)
        sizes: List of sizes to include in icon (default: common Windows sizes)
    """
    if sizes is None:
        # Common Windows icon sizes
        sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
    
    try:
        # Open the input image
        print(f"Opening image: {input_file}")
        img = Image.open(input_file)
        
        # Convert RGBA if needed (for transparency)
        if img.mode != 'RGBA' and 'transparency' in img.info:
            img = img.convert('RGBA')
        elif img.mode not in ('RGBA', 'RGB'):
            img = img.convert('RGB')
        
        # Create list of resized images
        print("Creating multiple icon sizes...")
        icon_images = []
        for size in sizes:
            # Use high-quality resampling
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)
            print(f"  Created {size[0]}x{size[1]} icon")
        
        # Save as ICO format with multiple sizes
        print(f"\nSaving icon file: {output_file}")
        icon_images[0].save(
            output_file,
            format='ICO',
            sizes=[(s[0], s[1]) for s in sizes]
        )
        
        print(f"\n✓ Success! Icon created: {output_file}")
        print(f"  File size: {os.path.getsize(output_file) / 1024:.2f} KB")
        return True
        
    except FileNotFoundError:
        print(f"ERROR: File not found: {input_file}")
        return False
    except Exception as e:
        print(f"ERROR: Failed to convert image: {e}")
        return False

def main():
    """Main function to handle command line arguments"""
    print("=" * 60)
    print("Image to Icon Converter")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  python {sys.argv[0]} <input_image> [output_icon.ico]")
        print()
        print("Examples:")
        print(f"  python {sys.argv[0]} logo.png")
        print(f"  python {sys.argv[0]} logo.png icon.ico")
        print()
        print("Supported input formats: PNG, JPG, JPEG, BMP, GIF, etc.")
        print()
        
        # Try to find common image files in current directory
        common_names = ['logo.png', 'logo.jpg', 'icon.png', 'icon.jpg', 'hospital_logo.png']
        found_files = [f for f in common_names if os.path.exists(f)]
        
        if found_files:
            print("Found these image files in current directory:")
            for f in found_files:
                print(f"  - {f}")
            print()
            response = input("Would you like to convert one of these? (y/n): ")
            if response.lower() == 'y':
                print()
                for i, f in enumerate(found_files, 1):
                    print(f"{i}. {f}")
                try:
                    choice = int(input("Enter number: ")) - 1
                    if 0 <= choice < len(found_files):
                        input_file = found_files[choice]
                        output_file = 'icon.ico'
                        if convert_to_ico(input_file, output_file):
                            print("\n" + "=" * 60)
                            print("Next steps:")
                            print("1. The icon.ico file has been created")
                            print("2. Run: build_exe.bat")
                            print("3. Run: build_installer.bat")
                            print("4. Your logo will now appear in shortcuts and the app!")
                            print("=" * 60)
                        return
                except (ValueError, IndexError):
                    print("Invalid choice.")
        
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'icon.ico'
    
    if not os.path.exists(input_file):
        print(f"ERROR: Input file does not exist: {input_file}")
        sys.exit(1)
    
    if convert_to_ico(input_file, output_file):
        print("\n" + "=" * 60)
        print("Next steps:")
        print("1. Rebuild the executable: build_exe.bat")
        print("2. Rebuild the installer: build_installer.bat")
        print("3. Your logo will appear in shortcuts and the app window!")
        print("=" * 60)

if __name__ == '__main__':
    main()

