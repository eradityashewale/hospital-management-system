"""
Script to clear existing medicines and re-import from CSV with correct column mapping
Usage: python reimport_medicines.py [csv_file_path]
"""
import sys
import os
from database import Database
from logger import log_info, log_error

def main():
    # Get CSV file path from command line or use default
    if len(sys.argv) > 1:
        csv_file_path = sys.argv[1]
    else:
        csv_file_path = input("Enter the path to medicine_data.csv file: ").strip().strip('"')
    
    csv_file_path = csv_file_path.strip('"').strip("'")
    
    if not os.path.exists(csv_file_path):
        print(f"Error: File not found: {csv_file_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("Re-importing Medicines from CSV")
    print("=" * 60)
    print(f"CSV file: {csv_file_path}")
    print("\nThis will:")
    print("1. Clear existing medicines from the database")
    print("2. Re-import all medicines with correct column mapping")
    print("-" * 60)
    
    confirm = input("\nDo you want to continue? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        sys.exit(0)
    
    try:
        # Initialize database
        db = Database()
        
        # Clear existing medicines
        print("\nClearing existing medicines...")
        db.cursor.execute("DELETE FROM medicines_master")
        db.conn.commit()
        print("Existing medicines cleared.")
        
        # Import medicines
        print(f"\nStarting import from: {csv_file_path}")
        print("This may take a while for large files...")
        print("-" * 60)
        
        result = db.import_medicines_from_csv(csv_file_path, batch_size=1000)
        
        # Print results
        print("-" * 60)
        if result['success']:
            print("Import completed successfully!")
            print(f"Total rows processed: {result.get('total', 0)}")
            print(f"Successfully imported: {result['imported']}")
            print(f"Failed: {result['failed']}")
            print(f"Skipped (empty medicine name): {result.get('skipped', 0)}")
            
            # Verify a sample
            print("\n" + "-" * 60)
            print("Sample of imported data (first 3 records):")
            print("-" * 60)
            medicines = db.get_all_medicines_master()[:3]
            for i, med in enumerate(medicines, 1):
                print(f"\n{i}. Medicine: {med.get('medicine_name', 'N/A')}")
                print(f"   Company: {med.get('company_name', 'N/A')}")
                print(f"   Category: {med.get('category', 'N/A')}")
                print(f"   Dosage: {med.get('dosage_mg', 'N/A')}")
                print(f"   Form: {med.get('dosage_form', 'N/A')}")
                print(f"   Description: {med.get('description', 'N/A')[:50]}...")
        else:
            print(f"Import failed: {result.get('message', 'Unknown error')}")
            if result.get('imported', 0) > 0:
                print(f"Partially imported: {result['imported']} records")
        
        db.close()
        
    except KeyboardInterrupt:
        print("\n\nImport interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during import: {str(e)}")
        log_error("CSV re-import script failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()



