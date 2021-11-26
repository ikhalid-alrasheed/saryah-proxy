from app import *
import datetime as dt
import pandas as pd
from pprint import pprint
# exec(open('database_builder.py').read())
import re

def read_table(table_name, opj):
    table = pd.read_excel("dummy_data.xlsx", sheet_name=table_name)
    for index, record in table.iterrows():
        instance = opj()
        for atter in table.columns :
            setattr(instance, atter, record[atter])
        db.session.add(instance)
    db.session.commit()
    print(f"table {table_name} has been added to the DateBase")
    return None
def Do():
    db.drop_all()
    db.create_all()
    read_table("Users", User)
    read_table("Cars", Cars)
    read_table("Transactions", Transactions)
    read_table("Policies", Policies)
    return


