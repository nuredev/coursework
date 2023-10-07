from django.urls import path, include

from _database.scheme import TABLES
from _database.sql import SQL

urlpatterns = [
    path('', include('home.urls')),
    path('api/', include('api.urls')),
    path('auth/', include('auths.urls')),
]

# Create tables if not present:

print("\n" * 50)

for table in TABLES.keys():
    SQL(table).create().run(ignore=True)
