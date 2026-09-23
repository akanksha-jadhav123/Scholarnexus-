"""
Seed ScholarNexus MongoDB with admin, demo student, and scholarships.
Usage: python seed/seed_db.py
"""
import os
import bcrypt
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/scholarnexus')
client = MongoClient(MONGO_URI)
db = client.get_database()

def clear():
    db.users.delete_many({})
    db.student_profiles.delete_many({})
    db.scholarships.delete_many({})
    db.applications.delete_many({})
    db.notifications.delete_many({})
    print('🧹 Cleared old data')

def seed_users():
    admin = {
        'name': 'ScholarNexus Admin',
        'email': 'admin@scholarnexus.com',
        'password': bcrypt.hashpw(b'admin123', bcrypt.gensalt()),
        'role': 'admin',
        'isActive': True,
        'createdAt': datetime.utcnow()
    }
    student = {
        'name': 'Demo Student',
        'email': 'student@scholarnexus.com',
        'password': bcrypt.hashpw(b'student123', bcrypt.gensalt()),
        'role': 'student',
        'isActive': True,
        'createdAt': datetime.utcnow()
    }
    db.users.insert_many([admin, student])
    print('👤 Admin: admin@scholarnexus.com / admin123')
    print('👤 Student: student@scholarnexus.com / student123')

def seed_scholarships_from_csv(path='seed/scholarships.csv'):
    df = pd.read_csv(path)
    inserted = 0
    for _, row in df.iterrows():
        doc = {
            'name': row['name'],
            'provider': row.get('provider', ''),
            'description': row.get('description', ''),
            'amount': int(row.get('amount', 0)) if pd.notna(row.get('amount')) else 0,
            'deadline': datetime.fromisoformat(str(row['deadline'])) if pd.notna(row.get('deadline')) else None,
            'applicationLink': row.get('applicationLink', ''),
            'documentsRequired': str(row.get('documentsRequired', '')).split(';') if pd.notna(row.get('documentsRequired')) else [],
            'eligibility': {
                'minPercentage': float(row.get('minPercentage', 0)) if pd.notna(row.get('minPercentage')) else 0,
                'maxIncome': int(row.get('maxIncome')) if pd.notna(row.get('maxIncome')) else None,
                'courses': str(row.get('courses', '')).split(';') if pd.notna(row.get('courses')) else [],
                'categories': str(row.get('categories', '')).split(';') if pd.notna(row.get('categories')) else [],
                'genders': str(row.get('genders', '')).split(';') if pd.notna(row.get('genders')) else [],
                'states': str(row.get('states', '')).split(';') if pd.notna(row.get('states')) else [],
            },
            'isVerified': True,
            'isActive': True,
            'createdAt': datetime.utcnow()
        }
        db.scholarships.insert_one(doc)
        inserted += 1
    print(f'📚 Seeded {inserted} scholarships')

if __name__ == '__main__':
    clear()
    seed_users()
    seed_scholarships_from_csv()
    print('✅ ScholarNexus seeding complete')