from src.shortcuts import Path
from .views import *

urlpatterns = [
    Path(register).link(),
    Path(login).link(),
    Path(logout).link(),
    Path(delete).link(),
]
