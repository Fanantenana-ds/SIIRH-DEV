# create_tables.py
import sys
import os

# Manampy ny path ao amin'ny 'app' mba ho hita ny db.py
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from db import Base, engine

def main():
    """Mamorona ny table rehetra mifanaraka amin'ny model ao amin'ny db.py"""
    Base.metadata.create_all(engine)
    print("Table 'candidatures' created successfully!")

if __name__ == "__main__":
    main()
