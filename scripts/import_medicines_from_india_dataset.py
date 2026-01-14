"""
Script to import medicines from A_Z_medicines_dataset_of_India.csv into the database
This script is specifically designed for the India medicines dataset CSV format.

CSV Columns:
- id, name, price(₹), Is_discontinued, manufacturer_name, type, pack_size_label, short_composition1, short_composition2

Database Columns:
- medicine_name, company_name, dosage_mg, dosage_form, category, description, is_pediatric

Usage: python scripts/import_medicines_from_india_dataset.py [csv_file_path]
       If no path provided, it will use A_Z_medicines_dataset_of_India.csv in the root directory
"""
import sys
import os
import csv
import re
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Backend imports
from backend.database import Database

# Utils imports
from utils.logger import log_info, log_error

def extract_dosage_from_composition(composition1, composition2):
    """Extract dosage information from composition fields"""
    dosage_parts = []
    
    # Combine both composition fields
    compositions = []
    if composition1:
        compositions.append(composition1.strip())
    if composition2:
        compositions.append(composition2.strip())
    
    combined = ' '.join(compositions)
    
    # Try to extract dosage information (e.g., "500mg", "30mg/5ml")
    if combined:
        # Look for patterns like "500mg", "30mg/5ml", etc.
        # Pattern to match dosage: numbers followed by mg, ml, mcg, etc.
        dosage_pattern = r'(\d+(?:\.\d+)?\s*(?:mg|ml|mcg|g|IU|%)\s*(?:/\s*\d+\s*(?:mg|ml|mcg|g))?)'
        matches = re.findall(dosage_pattern, combined, re.IGNORECASE)
        if matches:
            dosage_parts.extend(matches)
    
    return ' + '.join(dosage_parts) if dosage_parts else ''

def extract_form_from_pack_size(pack_size):
    """Extract dosage form from pack_size_label"""
    if not pack_size:
        return ''
    
    pack_size_lower = pack_size.lower()
    
    # Common forms
    if 'tablet' in pack_size_lower:
        return 'Tablet'
    elif 'capsule' in pack_size_lower:
        return 'Capsule'
    elif 'syrup' in pack_size_lower:
        return 'Syrup'
    elif 'injection' in pack_size_lower or 'injectable' in pack_size_lower:
        return 'Injection'
    elif 'cream' in pack_size_lower or 'ointment' in pack_size_lower:
        return 'Cream'
    elif 'drops' in pack_size_lower:
        return 'Drops'
    elif 'suspension' in pack_size_lower:
        return 'Suspension'
    elif 'powder' in pack_size_lower:
        return 'Powder'
    elif 'inhaler' in pack_size_lower:
        return 'Inhaler'
    elif 'gel' in pack_size_lower:
        return 'Gel'
    elif 'spray' in pack_size_lower:
        return 'Spray'
    else:
        # Return the pack_size_label as is if no specific form found
        return pack_size

def is_pediatric_medicine(name, pack_size, composition):
    """Determine if medicine is pediatric based on name, pack size, and composition"""
    name_lower = name.lower() if name else ''
    pack_lower = pack_size.lower() if pack_size else ''
    comp_lower = composition.lower() if composition else ''
    
    # Check for pediatric indicators
    pediatric_keywords = ['kid', 'child', 'pediatric', 'paediatric', 'infant', 'baby', 'drops', 'syrup']
    
    for keyword in pediatric_keywords:
        if keyword in name_lower or keyword in pack_lower or keyword in comp_lower:
            return 1
    
    # Check if it's a syrup or drops (commonly pediatric)
    if 'syrup' in pack_lower or 'drops' in pack_lower:
        return 1
    
    return 0

def main():
    # Get CSV file path
    if len(sys.argv) > 1:
        csv_file_path = sys.argv[1].strip().strip('"').strip("'")
    else:
        # Default to the CSV file in root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_file_path = os.path.join(root_dir, 'A_Z_medicines_dataset_of_India.csv')
    
    # Check if file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: File not found: {csv_file_path}")
        print(f"\nPlease provide the correct path to the CSV file.")
        print(f"Usage: python scripts/import_medicines_from_india_dataset.py [csv_file_path]")
        sys.exit(1)
    
    print("=" * 80)
    print("IMPORTING MEDICINES FROM INDIA DATASET CSV")
    print("=" * 80)
    print(f"CSV File: {csv_file_path}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Initialize database
        db = Database()
        
        # Check current count
        db.cursor.execute("SELECT COUNT(*) FROM medicines_master")
        initial_count = db.cursor.fetchone()[0]
        print(f"\nCurrent medicines in database: {initial_count:,}")
        
        # Ask user if they want to clear existing data
        if initial_count > 0:
            print("\n" + "-" * 80)
            response = input(f"There are {initial_count:,} medicines already in the database.\n"
                           f"Do you want to clear existing medicines before importing? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                print("Clearing existing medicines...")
                db.cursor.execute("DELETE FROM medicines_master")
                db.conn.commit()
                print("Existing medicines cleared.")
            else:
                print("Keeping existing medicines. New medicines will be added (duplicates will be skipped).")
        
        # Read and process CSV
        medicines_to_import = []
        batch_size = 1000
        
        # Try different encodings
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        file_encoding = None
        
        for encoding in encodings_to_try:
            try:
                with open(csv_file_path, 'r', encoding=encoding) as test_file:
                    test_file.read(1024)
                file_encoding = encoding
                print(f"\nFile encoding detected: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if not file_encoding:
            print(f"Error: Could not read file with any of the attempted encodings.")
            sys.exit(1)
        
        print("\nReading CSV file...")
        print("-" * 80)
        
        with open(csv_file_path, 'r', encoding=file_encoding) as file:
            # Detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            delimiter = ','
            try:
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
            except Exception:
                # Try common delimiters
                common_delimiters = [',', ';', '\t', '|']
                for delim in common_delimiters:
                    first_line = sample.split('\n')[0] if '\n' in sample else sample
                    if first_line.count(delim) > 0:
                        delimiter = delim
                        break
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            # Verify expected columns
            expected_columns = ['name', 'manufacturer_name', 'type', 'pack_size_label', 
                              'short_composition1', 'short_composition2']
            missing_columns = [col for col in expected_columns if col not in reader.fieldnames]
            
            if missing_columns:
                print(f"Warning: Some expected columns are missing: {missing_columns}")
                print(f"Available columns: {reader.fieldnames}")
            
            print(f"CSV Columns detected: {', '.join(reader.fieldnames)}")
            print("-" * 80)
            
            # Process rows
            count = 0
            skipped_count = 0
            error_count = 0
            
            print("\nProcessing medicines...")
            print("Showing first 5 medicines, then progress updates every 10,000 records...\n")
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Extract medicine name
                    medicine_name = row.get('name', '').strip()
                    
                    if not medicine_name:
                        skipped_count += 1
                        continue
                    
                    # Skip discontinued medicines
                    is_discontinued = row.get('Is_discontinued', '').strip().upper()
                    if is_discontinued in ['TRUE', '1', 'YES', 'Y']:
                        skipped_count += 1
                        continue
                    
                    # Map CSV columns to database columns
                    medicine_data = {}
                    medicine_data['medicine_name'] = medicine_name
                    medicine_data['company_name'] = row.get('manufacturer_name', '').strip()
                    medicine_data['category'] = row.get('type', '').strip() or 'General'
                    
                    # Extract dosage from composition
                    comp1 = row.get('short_composition1', '').strip()
                    comp2 = row.get('short_composition2', '').strip()
                    medicine_data['dosage_mg'] = extract_dosage_from_composition(comp1, comp2)
                    
                    # Extract form from pack_size_label
                    pack_size = row.get('pack_size_label', '').strip()
                    medicine_data['dosage_form'] = extract_form_from_pack_size(pack_size)
                    
                    # Create description from available data
                    description_parts = []
                    if pack_size:
                        description_parts.append(f"Pack: {pack_size}")
                    if comp1:
                        description_parts.append(f"Composition: {comp1}")
                    if comp2:
                        description_parts.append(f" + {comp2}")
                    
                    medicine_data['description'] = ' | '.join(description_parts) if description_parts else ''
                    
                    # Determine if pediatric
                    medicine_data['is_pediatric'] = is_pediatric_medicine(
                        medicine_name, pack_size, comp1 + ' ' + comp2
                    )
                    
                    medicines_to_import.append(medicine_data)
                    count += 1
                    
                    # Show first 5 medicines
                    if count <= 5:
                        print(f"\nMedicine #{count} (Row {row_num}):")
                        print(f"  Name: {medicine_data['medicine_name']}")
                        print(f"  Company: {medicine_data['company_name'] or '(empty)'}")
                        print(f"  Category: {medicine_data['category']}")
                        print(f"  Dosage: {medicine_data['dosage_mg'] or '(empty)'}")
                        print(f"  Form: {medicine_data['dosage_form'] or '(empty)'}")
                        print(f"  Pediatric: {'Yes' if medicine_data['is_pediatric'] else 'No'}")
                    
                    # Progress updates
                    if count > 5 and count % 10000 == 0:
                        print(f"Processed {count:,} medicines... (Row {row_num:,})")
                
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:
                        print(f"\nError processing row {row_num}: {str(e)}")
                    continue
            
            print(f"\n{'='*80}")
            print(f"CSV Processing Complete!")
            print(f"  Total medicines extracted: {count:,}")
            print(f"  Skipped (empty/discontinued): {skipped_count:,}")
            print(f"  Errors: {error_count:,}")
            print(f"{'='*80}")
        
        # Import to database
        if not medicines_to_import:
            print("\nNo medicines to import!")
            db.close()
            sys.exit(0)
        
        print(f"\n{'='*80}")
        print(f"IMPORTING {len(medicines_to_import):,} MEDICINES TO DATABASE...")
        print(f"Batch size: {batch_size}")
        print(f"{'='*80}\n")
        
        imported = 0
        failed = 0
        total_batches = (len(medicines_to_import) + batch_size - 1) // batch_size
        
        # Process in batches
        for batch_idx in range(0, len(medicines_to_import), batch_size):
            batch = medicines_to_import[batch_idx:batch_idx + batch_size]
            current_batch_num = (batch_idx // batch_size) + 1
            
            try:
                batch_imported = db.batch_add_medicines_to_master(batch)
                imported += batch_imported
                failed += (len(batch) - batch_imported)
                
                # Progress updates
                if current_batch_num % 10 == 0 or current_batch_num == total_batches:
                    progress = (current_batch_num / total_batches) * 100
                    print(f"Batch {current_batch_num:,}/{total_batches:,} ({progress:.1f}%) - "
                          f"Imported: {imported:,}, Failed: {failed:,}")
            
            except Exception as e:
                failed += len(batch)
                print(f"Error in batch {current_batch_num}: {str(e)}")
                continue
        
        # Final summary
        print(f"\n{'='*80}")
        print("IMPORT SUMMARY")
        print(f"{'='*80}")
        print(f"Total medicines processed: {len(medicines_to_import):,}")
        print(f"Successfully imported: {imported:,}")
        print(f"Failed/Skipped (duplicates): {failed:,}")
        if imported > 0:
            success_rate = (imported / len(medicines_to_import)) * 100
            print(f"Success rate: {success_rate:.2f}%")
        print(f"{'='*80}")
        
        # Verify import
        print(f"\n{'='*80}")
        print("VERIFYING DATABASE")
        print(f"{'='*80}")
        
        db.cursor.execute("SELECT COUNT(*) FROM medicines_master")
        final_count = db.cursor.fetchone()[0]
        print(f"\nTotal medicines in database: {final_count:,}")
        print(f"Medicines added in this import: {final_count - initial_count:,}")
        
        # Show sample
        print(f"\nSample of imported medicines (first 5):")
        db.cursor.execute("""
            SELECT medicine_name, company_name, category, dosage_mg, dosage_form 
            FROM medicines_master 
            ORDER BY id DESC 
            LIMIT 5
        """)
        rows = db.cursor.fetchall()
        for idx, row in enumerate(rows, 1):
            print(f"\n{idx}. {row['medicine_name']}")
            print(f"   Company: {row['company_name'] or '(empty)'}")
            print(f"   Category: {row['category'] or '(empty)'}")
            print(f"   Dosage: {row['dosage_mg'] or '(empty)'}")
            print(f"   Form: {row['dosage_form'] or '(empty)'}")
        
        print(f"\n{'='*80}")
        print(f"Import completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        db.close()
        
    except KeyboardInterrupt:
        print("\n\nImport interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during import: {str(e)}")
        import traceback
        traceback.print_exc()
        log_error("India medicines dataset import failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

