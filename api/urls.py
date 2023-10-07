from src.shortcuts import Path
from .views import *

urlpatterns = [
    Path(run_sql).link(),
    Path(fetch_table).link("fetch_table/<str:table_name>"),
    Path(delete_from_table).link("delete/<str:table_name>/<str:column>/<str:value>"),
    Path(table_info).link("info/<str:table_name>"),
    Path(vote).link("vote/<int:rating_id>/<int:is_positive>"),
]
