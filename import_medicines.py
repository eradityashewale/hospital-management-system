"""
Script to import medicines from CSV file into the database
Usage: python import_medicines.py [csv_file_path]
"""
import sys
import os
import csv
from database import Database
from logger import log_info, log_error

def main():
    # Get CSV file path from command line or use default
    if len(sys.argv) > 1:
        csv_file_path = sys.argv[1]
    else:
        csv_file_path = input("Enter the path to medicine_data.csv file: ").strip().strip('"')
    
    # Remove quotes if present
    csv_file_path = csv_file_path.strip('"').strip("'")
    
    # Check if file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: File not found: {csv_file_path}")
        print("Please provide the correct path to the CSV file.")
        sys.exit(1)
    
    # Validate file extension
    file_ext = os.path.splitext(csv_file_path)[1].lower()
    if file_ext == '.db':
        print(f"Error: You provided a database file (.db) instead of a CSV file.")
        print(f"File provided: {csv_file_path}")
        print(f"\nPlease provide the path to the CSV file (medicine_data.csv)")
        print(f"Expected file should end with .csv")
        sys.exit(1)
    elif file_ext not in ['.csv', '.txt']:
        print(f"Warning: File extension '{file_ext}' is not typically a CSV file.")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("Import cancelled.")
            sys.exit(1)
    
    # Check if file is binary (quick check)
    try:
        with open(csv_file_path, 'rb') as f:
            chunk = f.read(512)
            # Check for null bytes or SQLite magic bytes (SQLite files start with "SQLite format 3")
            if b'\x00' in chunk or chunk.startswith(b'SQLite format 3'):
                print(f"Error: The file appears to be a binary file (possibly a database file), not a CSV file.")
                print(f"File provided: {csv_file_path}")
                print(f"\nPlease provide the path to the CSV file (medicine_data.csv)")
                sys.exit(1)
    except Exception as e:
        print(f"Warning: Could not validate file type: {e}")
    
    print(f"Starting import from: {csv_file_path}")
    print("IMPORTING ALL MEDICINES FROM CSV")
    print("=" * 80)
    
    try:
        # Initialize database
        db = Database()
        
        # Read and process all medicines
        medicines_to_import = []
        batch_size = 1000  # Process in batches for better performance
        
        # Try different encodings if UTF-8 fails
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        file_encoding = None
        
        for encoding in encodings_to_try:
            try:
                # Test if we can read the file with this encoding
                with open(csv_file_path, 'r', encoding=encoding) as test_file:
                    test_file.read(1024)
                file_encoding = encoding
                print(f"Successfully detected file encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if not file_encoding:
            print(f"Error: Could not read file with any of the attempted encodings: {encodings_to_try}")
            print("The file may be corrupted or in an unsupported format.")
            sys.exit(1)
        
        # Use the successfully detected encoding
        with open(csv_file_path, 'r', encoding=file_encoding) as file:
            # Detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            delimiter = ','
            try:
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
            except Exception:
                common_delimiters = [',', ';', '\t', '|']
                for delim in common_delimiters:
                    first_line = sample.split('\n')[0] if '\n' in sample else sample
                    if first_line.count(delim) > 0:
                        delimiter = delim
                        break
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            # Map CSV columns to database columns (same logic as database.py)
            column_mapping = {}
            fieldnames_lower = [col.lower().strip() for col in reader.fieldnames]
            
            for csv_col in reader.fieldnames:
                csv_col_lower = csv_col.lower().strip()
                
                # Medicine name mapping
                if 'medicine_name' not in column_mapping:
                    if csv_col_lower in ['product_name', 'medicine_name', 'drug_name', 'name']:
                        column_mapping['medicine_name'] = csv_col
                    elif 'medicine' in csv_col_lower and 'name' in csv_col_lower:
                        column_mapping['medicine_name'] = csv_col
                    elif 'product' in csv_col_lower and 'name' in csv_col_lower:
                        column_mapping['medicine_name'] = csv_col
                    elif csv_col_lower in ['medicine', 'drug', 'medication']:
                        column_mapping['medicine_name'] = csv_col
                    elif 'name' in csv_col_lower and csv_col_lower not in ['company_name', 'company name']:
                        if 'medicine_name' not in column_mapping:
                            column_mapping['medicine_name'] = csv_col
                
                # Company name mapping
                if 'company_name' not in column_mapping:
                    if csv_col_lower in ['product_manufactured', 'manufacturer', 'company_name', 'company', 'maker', 'brand']:
                        column_mapping['company_name'] = csv_col
                    elif 'company' in csv_col_lower and 'name' in csv_col_lower:
                        column_mapping['company_name'] = csv_col
                    elif 'manufactured' in csv_col_lower or 'manufacturer' in csv_col_lower:
                        column_mapping['company_name'] = csv_col
                
                # Category mapping
                if 'category' not in column_mapping:
                    if csv_col_lower in ['sub_category', 'category', 'type', 'class', 'classification', 'drug_category']:
                        column_mapping['category'] = csv_col
                    elif 'category' in csv_col_lower:
                        column_mapping['category'] = csv_col
                
                # Dosage mapping
                if csv_col_lower in ['salt_composition', 'dosage', 'dose', 'strength']:
                    if 'dosage_mg' not in column_mapping:
                        column_mapping['dosage_mg'] = csv_col
                elif 'dosage' in csv_col_lower or 'dose' in csv_col_lower or 'strength' in csv_col_lower:
                    if 'dosage_mg' not in column_mapping and ('mg' in csv_col_lower or 'form' not in csv_col_lower):
                        column_mapping['dosage_mg'] = csv_col
                    elif 'dosage_form' not in column_mapping and 'form' in csv_col_lower:
                        column_mapping['dosage_form'] = csv_col
                elif 'form' in csv_col_lower and 'dosage_form' not in column_mapping:
                    column_mapping['dosage_form'] = csv_col
                
                # Description mapping
                if 'description' not in column_mapping:
                    if csv_col_lower in ['medicine_desc', 'description', 'desc', 'details', 'notes', 'remarks']:
                        column_mapping['description'] = csv_col
                    elif 'desc' in csv_col_lower:
                        column_mapping['description'] = csv_col
                
                # Pediatric mapping
                if 'is_pediatric' not in column_mapping:
                    if csv_col_lower in ['pediatric', 'paediatric', 'child', 'children', 'is_pediatric', 'pediatric_use']:
                        column_mapping['is_pediatric'] = csv_col
            
            # If medicine_name still not found, use first column as fallback
            if 'medicine_name' not in column_mapping and reader.fieldnames:
                column_mapping['medicine_name'] = reader.fieldnames[0]
            
            print(f"\nColumn Mapping Detected:")
            print(f"  medicine_name: {column_mapping.get('medicine_name', 'NOT FOUND')}")
            print(f"  company_name: {column_mapping.get('company_name', 'NOT FOUND')}")
            print(f"  category: {column_mapping.get('category', 'NOT FOUND')}")
            print(f"  dosage_mg: {column_mapping.get('dosage_mg', 'NOT FOUND')}")
            print(f"  dosage_form: {column_mapping.get('dosage_form', 'NOT FOUND')}")
            print(f"  description: {column_mapping.get('description', 'NOT FOUND')}")
            print(f"  is_pediatric: {column_mapping.get('is_pediatric', 'NOT FOUND')}")
            print("=" * 80)
            
            # Process all rows
            count = 0
            skipped_count = 0
            error_count = 0
            
            print("\nProcessing CSV file...")
            print("Showing detailed data for first 10 medicines, then progress updates...\n")
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    medicine_data = {}
                    
                    # Extract data using column mapping
                    medicine_data['medicine_name'] = row.get(column_mapping.get('medicine_name', reader.fieldnames[0] if reader.fieldnames else ''), '').strip()
                    
                    if not medicine_data['medicine_name']:
                        skipped_count += 1
                        if count < 10:
                            print(f"\nRow {row_num}: SKIPPED - Empty medicine name")
                        continue
                    
                    medicine_data['company_name'] = row.get(column_mapping.get('company_name', ''), '').strip() if column_mapping.get('company_name') else ''
                    medicine_data['category'] = row.get(column_mapping.get('category', ''), '').strip() if column_mapping.get('category') else ''
                    medicine_data['dosage_mg'] = row.get(column_mapping.get('dosage_mg', ''), '').strip() if column_mapping.get('dosage_mg') else ''
                    medicine_data['dosage_form'] = row.get(column_mapping.get('dosage_form', ''), '').strip() if column_mapping.get('dosage_form') else ''
                    medicine_data['description'] = row.get(column_mapping.get('description', ''), '').strip() if column_mapping.get('description') else ''
                    
                    # Handle is_pediatric
                    pediatric_val = row.get(column_mapping.get('is_pediatric', ''), '0').strip() if column_mapping.get('is_pediatric') else '0'
                    if pediatric_val.lower() in ['yes', 'true', '1', 'y']:
                        medicine_data['is_pediatric'] = 1
                    else:
                        medicine_data['is_pediatric'] = 0
                    
                    medicines_to_import.append(medicine_data)
                    count += 1
                    
                    # Print detailed data for first 10 medicines
                    if count <= 10:
                        print(f"\n{'='*80}")
                        print(f"MEDICINE #{count} (Row {row_num}):")
                        print(f"{'='*80}")
                        print(f"  Medicine Name: {medicine_data['medicine_name']}")
                        print(f"  Company Name: {medicine_data['company_name'] or '(empty)'}")
                        print(f"  Category: {medicine_data['category'] or '(empty)'}")
                        print(f"  Dosage (mg): {medicine_data['dosage_mg'] or '(empty)'}")
                        print(f"  Dosage Form: {medicine_data['dosage_form'] or '(empty)'}")
                        print(f"  Description: {medicine_data['description'] or '(empty)'}")
                        print(f"  Is Pediatric: {medicine_data['is_pediatric']}")
                        print(f"{'='*80}")
                    # Show progress every 1000 medicines
                    elif count % 1000 == 0:
                        print(f"Processed {count:,} medicines... (Row {row_num:,})")
                    
                except Exception as e:
                    error_count += 1
                    if count < 10:
                        print(f"\nRow {row_num}: ERROR - {str(e)}")
                    continue
            
            print(f"\n{'='*80}")
            print(f"CSV Processing Complete!")
            print(f"  Total medicines extracted: {count:,}")
            print(f"  Skipped (empty name): {skipped_count:,}")
            print(f"  Errors: {error_count:,}")
            print(f"{'='*80}")
        
        # Import the medicines in batches
        print(f"\n\n{'='*80}")
        print(f"IMPORTING {len(medicines_to_import):,} MEDICINES TO DATABASE...")
        print(f"Using batch size: {batch_size}")
        print(f"{'='*80}\n")
        
        imported = 0
        failed = 0
        total_batches = (len(medicines_to_import) + batch_size - 1) // batch_size
        
        # Process in batches
        for batch_idx in range(0, len(medicines_to_import), batch_size):
            batch = medicines_to_import[batch_idx:batch_idx + batch_size]
            current_batch_num = (batch_idx // batch_size) + 1
            
            try:
                # Use the database method to add medicines in batch
                batch_imported = db.batch_add_medicines_to_master(batch)
                imported += batch_imported
                failed += (len(batch) - batch_imported)
                
                # Show progress
                if current_batch_num % 10 == 0 or current_batch_num == total_batches:
                    print(f"Batch {current_batch_num:,}/{total_batches:,} - Imported: {imported:,}, Failed: {failed:,}")
                
                # Show detailed info for first batch
                if current_batch_num == 1:
                    print(f"\nFirst batch ({len(batch)} medicines):")
                    for idx, medicine_data in enumerate(batch[:10], 1):  # Show first 10 of first batch
                        status = "✓" if idx <= batch_imported else "✗"
                        print(f"  {status} Medicine #{idx}: '{medicine_data['medicine_name']}'")
                    if len(batch) > 10:
                        print(f"  ... and {len(batch) - 10} more in this batch")
                    print()
                    
            except Exception as e:
                failed += len(batch)
                print(f"✗ Batch {current_batch_num} - ERROR: {str(e)}")
                continue
        
        # Print final results
        print(f"\n{'='*80}")
        print("IMPORT SUMMARY:")
        print(f"{'='*80}")
        print(f"Total medicines processed: {len(medicines_to_import):,}")
        print(f"Successfully imported: {imported:,}")
        print(f"Failed: {failed:,}")
        if imported > 0:
            success_rate = (imported / len(medicines_to_import)) * 100
            print(f"Success rate: {success_rate:.2f}%")
        print(f"{'='*80}")
        
        # Verify by retrieving from database
        print(f"\n{'='*80}")
        print("VERIFYING DATA IN DATABASE:")
        print(f"{'='*80}")
        
        try:
            # Get total count
            db.cursor.execute("SELECT COUNT(*) as total FROM medicines_master")
            total_count = db.cursor.fetchone()['total']
            print(f"\nTotal medicines in database: {total_count:,}")
            
            # Get sample of most recent medicines
            db.cursor.execute("SELECT * FROM medicines_master ORDER BY medicine_id DESC LIMIT 10")
            rows = db.cursor.fetchall()
            
            if rows:
                print(f"\nSample of 10 most recently added medicines:\n")
                for idx, row in enumerate(rows, 1):
                    print(f"Medicine #{idx} from Database:")
                    print(f"  ID: {row['medicine_id']}")
                    print(f"  Medicine Name: {row['medicine_name']}")
                    print(f"  Company Name: {row['company_name'] or '(empty)'}")
                    print(f"  Category: {row['category'] or '(empty)'}")
                    print(f"  Dosage (mg): {row['dosage_mg'] or '(empty)'}")
                    print(f"  Dosage Form: {row['dosage_form'] or '(empty)'}")
                    print(f"  Description: {row['description'] or '(empty)'}")
                    print(f"  Is Pediatric: {row['is_pediatric']}")
                    print(f"  Created At: {row.get('created_at', 'N/A')}")
                    print("-" * 80)
            else:
                print("No medicines found in database.")
        except Exception as e:
            print(f"Error verifying data: {str(e)}")
        
        db.close()
        
    except KeyboardInterrupt:
        print("\n\nImport interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during import: {str(e)}")
        import traceback
        traceback.print_exc()
        log_error("CSV import script failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()


