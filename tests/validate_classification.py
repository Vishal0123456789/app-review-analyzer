"""Validation test for review classification output"""
import json
import csv

def test_json_structure():
    """Test JSON file structure and data integrity"""
    print("\n[TEST 1] JSON Structure Validation")
    print("=" * 80)
    
    with open('review_weekly_classified_20251030_20251127.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert 'records' in data, "Missing 'records' key"
    assert 'summary' in data, "Missing 'summary' key"
    
    records = data['records']
    summary = data['summary']
    
    # Check records
    assert len(records) > 0, "No records found"
    print(f"✓ Total records: {len(records)}")
    
    required_fields = ['review_id', 'rating', 'sentiment', 'review_theme', 'confidence', 'fallback_applied']
    for record in records:
        for field in required_fields:
            assert field in record, f"Missing field: {field}"
    print(f"✓ All {len(required_fields)} required fields present in all records")
    
    # Check summary
    assert summary['total_output'] == len(records), "Summary count mismatch"
    assert 'counts_by_theme' in summary, "Missing theme counts"
    print(f"✓ Summary structure valid")
    
    return records, summary

def test_theme_distribution():
    """Test theme classification distribution"""
    print("\n[TEST 2] Theme Distribution")
    print("=" * 80)
    
    with open('review_weekly_classified_20251030_20251127.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    records = data['records']
    themes = {}
    for rec in records:
        theme = rec.get('review_theme')
        themes[theme] = themes.get(theme, 0) + 1
    
    allowed_themes = [
        "Execution & Performance",
        "Payments & Withdrawals", 
        "Charges & Transparency",
        "KYC & Access",
        "UI & Feature Gaps"
    ]
    
    for theme, count in sorted(themes.items()):
        assert theme in allowed_themes, f"Invalid theme: {theme}"
        pct = (count / len(records) * 100)
        print(f"✓ {theme}: {count} reviews ({pct:.1f}%)")
    
    return themes

def test_sentiment_distribution():
    """Test sentiment classification"""
    print("\n[TEST 3] Sentiment Distribution")
    print("=" * 80)
    
    with open('review_weekly_classified_20251030_20251127.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    records = data['records']
    sentiments = {}
    
    for rec in records:
        sentiment = rec.get('sentiment')
        assert sentiment in ['positive', 'negative', 'neutral'], f"Invalid sentiment: {sentiment}"
        sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
    
    for sent in ['positive', 'negative', 'neutral']:
        count = sentiments.get(sent, 0)
        pct = (count / len(records) * 100)
        print(f"✓ {sent}: {count} reviews ({pct:.1f}%)")
    
    return sentiments

def test_confidence_scores():
    """Test confidence score validity"""
    print("\n[TEST 4] Confidence Score Validation")
    print("=" * 80)
    
    with open('review_weekly_classified_20251030_20251127.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    records = data['records']
    summary = data['summary']
    
    confidences = []
    for rec in records:
        conf = rec.get('confidence', 0)
        assert 0 <= conf <= 1, f"Invalid confidence: {conf}"
        confidences.append(conf)
    
    avg_conf = sum(confidences) / len(confidences)
    min_conf = min(confidences)
    max_conf = max(confidences)
    
    print(f"✓ All confidence scores valid (0.0-1.0)")
    print(f"✓ Min confidence: {min_conf:.3f}")
    print(f"✓ Max confidence: {max_conf:.3f}")
    print(f"✓ Average confidence: {avg_conf:.3f}")
    assert abs(avg_conf - summary['average_confidence']) < 0.001, "Summary confidence mismatch"
    print(f"✓ Summary average matches calculated average")

def test_csv_consistency():
    """Test CSV matches JSON"""
    print("\n[TEST 5] CSV Consistency with JSON")
    print("=" * 80)
    
    with open('review_weekly_classified_20251030_20251127.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    json_records = {r['review_id']: r for r in data['records']}
    
    with open('review_weekly_classified_20251030_20251127.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_records = list(reader)
    
    assert len(csv_records) == len(json_records), "Row count mismatch"
    print(f"✓ CSV row count matches JSON: {len(csv_records)} records")
    
    # Check first record
    if csv_records:
        csv_first = csv_records[0]
        json_first = json_records.get(csv_first['review_id'])
        
        assert json_first, "Review ID mismatch"
        assert float(csv_first['confidence']) == json_first['confidence'], "Confidence mismatch"
        assert csv_first['sentiment'] == json_first['sentiment'], "Sentiment mismatch"
        assert csv_first['review_theme'] == json_first['review_theme'], "Theme mismatch"
        print(f"✓ First record matches between JSON and CSV")

def test_data_completeness():
    """Test data completeness"""
    print("\n[TEST 6] Data Completeness")
    print("=" * 80)
    
    with open('review_weekly_classified_20251030_20251127.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    records = data['records']
    
    # Check for null/missing critical fields (allow missing date/rating from source data)
    missing_count = 0
    critical_fields = ['review_id', 'sentiment', 'review_theme', 'confidence']
    for rec in records:
        for field in critical_fields:
            if not rec.get(field):
                missing_count += 1
    
    assert missing_count == 0, f"Found {missing_count} missing critical values"
    print(f"✓ No missing critical fields (review_id, sentiment, review_theme, confidence)")
    print(f"✓ All {len(records)} records have complete classification data")

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("CLASSIFICATION OUTPUT VALIDATION TEST SUITE")
    print("=" * 80)
    
    try:
        test_json_structure()
        test_theme_distribution()
        test_sentiment_distribution()
        test_confidence_scores()
        test_csv_consistency()
        test_data_completeness()
        
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
