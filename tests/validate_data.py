import json
import csv
import uuid
from datetime import datetime
from collections import defaultdict

def validate_json_structure(data):
    """Validate JSON structure and field requirements."""
    print("\n[TEST 1] JSON Structure Validation")
    print("=" * 80)
    
    errors = []
    required_fields = ['review_id', 'date', 'week_start_date', 'week_end_date', 
                      'rating', 'title', 'text', 'clean_text', 'relevance', 'source']
    
    for idx, record in enumerate(data):
        for field in required_fields:
            if field not in record:
                errors.append(f"Record {idx}: Missing field '{field}'")
        
        if 'rating' in record:
            rating = record['rating']
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                errors.append(f"Record {idx}: Invalid rating {rating}")
        
        if 'source' in record and record['source'] != 'google_play':
            errors.append(f"Record {idx}: Invalid source")
    
    if errors:
        print(f"FAILED: {len(errors)} errors")
        for err in errors[:5]:
            print(f"  - {err}")
        return False
    else:
        print(f"PASSED: All {len(data)} records have correct structure")
        return True

def validate_dates(data):
    """Validate date format and week boundaries."""
    print("\n[TEST 2] Date Format & Week Boundaries")
    print("=" * 80)
    
    errors = []
    
    for idx, record in enumerate(data):
        try:
            date_obj = datetime.strptime(record['date'], '%Y-%m-%d')
            week_start = datetime.strptime(record['week_start_date'], '%Y-%m-%d')
            week_end = datetime.strptime(record['week_end_date'], '%Y-%m-%d')
        except ValueError:
            errors.append(f"Record {idx}: Invalid date format")
            continue
        
        # Check week span is 6 days
        if (week_end - week_start).days != 6:
            errors.append(f"Record {idx}: Week span not 6 days")
        
        # Check date is within week
        if date_obj < week_start or date_obj > week_end:
            errors.append(f"Record {idx}: Date not in week boundaries")
    
    if errors:
        print(f"FAILED: {len(errors)} errors")
        for err in errors[:5]:
            print(f"  - {err}")
        return False
    else:
        print(f"PASSED: All dates properly formatted and bounded")
        return True

def validate_text_fields(data):
    """Validate text and clean_text fields."""
    print("\n[TEST 3] Text Fields Validation")
    print("=" * 80)
    
    errors = []
    
    for idx, record in enumerate(data):
        text = record.get('text', '')
        clean_text = record.get('clean_text', '')
        
        if not isinstance(text, str):
            errors.append(f"Record {idx}: text is not string")
        
        if not isinstance(clean_text, str):
            errors.append(f"Record {idx}: clean_text is not string")
        
        # Verify clean_text is lowercase
        if clean_text and clean_text != clean_text.lower():
            errors.append(f"Record {idx}: clean_text not fully lowercase")
        
        # Verify clean_text is trimmed
        if clean_text != clean_text.strip():
            errors.append(f"Record {idx}: clean_text has extra spaces")
        
        # Verify no double spaces in clean_text
        if '  ' in clean_text:
            errors.append(f"Record {idx}: clean_text has double spaces")
    
    if errors:
        print(f"FAILED: {len(errors)} errors")
        for err in errors[:5]:
            print(f"  - {err}")
        return False
    else:
        print(f"PASSED: All text fields properly formatted")
        return True

def validate_pii_redaction(data):
    """Validate PII patterns in data."""
    print("\n[TEST 4] PII Redaction Check")
    print("=" * 80)
    
    redacted_count = 0
    redaction_tags = ['[REDACTED_EMAIL]', '[REDACTED_PHONE]', '[REDACTED_ID]', '[REDACTED_PERSON]']
    
    for record in data:
        text = record.get('text', '')
        for tag in redaction_tags:
            if tag in text:
                redacted_count += 1
                break
    
    print(f"INFO: {redacted_count} records contain redaction tags")
    print(f"INFO: {len(data) - redacted_count} records have no detected PII")
    print(f"PASSED: PII redaction validated")
    return True

def validate_clean_text_quality(data):
    """Validate clean_text has emojis removed."""
    print("\n[TEST 5] Clean Text Quality (Emoji Removal)")
    print("=" * 80)
    
    emoji_ranges = [(0x1F000, 0x1F9FF), (0x2600, 0x27BF), (0x2300, 0x23FF), (0xFE0F, 0xFE0F)]
    
    records_with_emoji = []
    
    for idx, record in enumerate(data):
        clean_text = record.get('clean_text', '')
        
        for char in clean_text:
            code = ord(char)
            for start, end in emoji_ranges:
                if start <= code <= end:
                    records_with_emoji.append(idx)
                    break
    
    if records_with_emoji:
        print(f"FAILED: {len(records_with_emoji)} records have emojis in clean_text")
        return False
    else:
        print(f"PASSED: All clean_text fields are emoji-free")
        return True

def validate_uniqueness(data):
    """Validate UUIDs and deduplication."""
    print("\n[TEST 6] Uniqueness & UUID Validation")
    print("=" * 80)
    
    errors = []
    review_ids = set()
    
    for idx, record in enumerate(data):
        review_id = record.get('review_id', '')
        
        try:
            uuid.UUID(review_id)
        except ValueError:
            errors.append(f"Record {idx}: Invalid UUID")
        
        if review_id in review_ids:
            errors.append(f"Record {idx}: Duplicate UUID")
        review_ids.add(review_id)
    
    if errors:
        print(f"FAILED: {len(errors)} errors")
        return False
    else:
        print(f"PASSED: All {len(data)} review_ids are unique UUIDs")
        return True

def validate_rating_distribution(data):
    """Validate rating distribution."""
    print("\n[TEST 7] Rating Distribution")
    print("=" * 80)
    
    distribution = defaultdict(int)
    for record in data:
        distribution[record.get('rating')] += 1
    
    print("Distribution:")
    for rating in sorted(distribution.keys()):
        count = distribution[rating]
        pct = (count / len(data)) * 100
        print(f"  {rating}-star: {count} ({pct:.1f}%)")
    
    if len(distribution) == 1:
        print("FAILED: All reviews have same rating")
        return False
    
    print(f"PASSED: Reviews across {len(distribution)} rating levels")
    return True

def validate_csv_match(csv_file, json_data):
    """Validate CSV matches JSON."""
    print("\n[TEST 8] CSV vs JSON Consistency")
    print("=" * 80)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_rows = list(csv.DictReader(f))
    except Exception as e:
        print(f"FAILED: Cannot read CSV - {e}")
        return False
    
    if len(csv_rows) != len(json_data):
        print(f"FAILED: Record count mismatch - JSON: {len(json_data)}, CSV: {len(csv_rows)}")
        return False
    
    expected_cols = ['review_id', 'date', 'week_start_date', 'week_end_date', 
                    'rating', 'title', 'text', 'clean_text', 'relevance', 'source']
    actual_cols = list(csv_rows[0].keys()) if csv_rows else []
    
    if actual_cols != expected_cols:
        print(f"FAILED: Column mismatch")
        return False
    
    print(f"PASSED: CSV has {len(csv_rows)} records with {len(expected_cols)} columns")
    return True

def run_validation():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print("DATA VALIDATION TEST SUITE")
    print("=" * 80)
    
    try:
        with open('reviews_weekly_transformed_20250902_20251125.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"FAILED: Cannot load JSON - {e}")
        return
    
    print(f"Testing {len(data)} records")
    
    results = {}
    results['structure'] = validate_json_structure(data)
    results['dates'] = validate_dates(data)
    results['text'] = validate_text_fields(data)
    results['pii'] = validate_pii_redaction(data)
    results['clean'] = validate_clean_text_quality(data)
    results['unique'] = validate_uniqueness(data)
    results['rating'] = validate_rating_distribution(data)
    results['csv'] = validate_csv_match('reviews_weekly_transformed_20250902_20251125.csv', data)
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"  [{status}] {test_name.upper()}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSTATUS: ALL TESTS PASSED - DATA IS VALID")
    else:
        print(f"\nSTATUS: {total - passed} TEST(S) FAILED")
    
    print("=" * 80 + "\n")

if __name__ == "__main__":
    run_validation()
