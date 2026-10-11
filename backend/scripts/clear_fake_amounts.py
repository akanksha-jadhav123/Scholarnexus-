"""One-time cleanup of likely page-number amounts like ₹4 in MongoDB.
Review mode is default. Pass --apply to update the records."""
import argparse
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='Actually clear suspicious amounts')
args = parser.parse_args()

query = {'scholarship_amount': {'$gt': 0, '$lt': 100}, '$or': [
    {'source': {'$regex': 'scholars4dev|internationalscholarships', '$options': 'i'}},
    {'provider': {'$regex': 'scholars4dev|internationalscholarships', '$options': 'i'}},
    {'scholarship_name': {'$regex': 'top\\s*\\d+|fully funded|scholarships in', '$options': 'i'}}
]}
records = list(db.Scholarships.find(query, {'scholarship_name': 1, 'provider': 1, 'source': 1, 'scholarship_amount': 1, 'amount_min': 1, 'amount_max': 1}))
print(f'Found {len(records)} suspicious low-amount records:')
for r in records:
    print(f"- {r.get('scholarship_name')} | {r.get('provider')} | amount={r.get('scholarship_amount')}")
if args.apply and records:
    ids = [r['_id'] for r in records]
    result = db.Scholarships.update_many({'_id': {'$in': ids}}, {'$set': {'scholarship_amount': None, 'amount_min': None, 'amount_max': None}})
    print(f'Cleared suspicious amounts on {result.modified_count} records. Re-run the scraper to repopulate only verified values.')
elif records:
    print('Review only: no database changes made. Run with --apply to clear these suspicious values.')
