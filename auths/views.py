from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect

from _database.sql import SQL
from src.shortcuts import router, encrypt


def set_login_cookies(user_id: str, password: str):
    response = redirect("/")
    response.set_cookie(
        key="credentials",
        value=user_id + " " + password,
        httponly=True,
    )
    return response


@router
def register():
    def get(request: WSGIRequest):
        return render(request, "auth/register.html", {"user": None})

    def post(request: WSGIRequest):
        user_id, username, password, confirm_password = request.POST.get("user_id").replace(" ", "_").lower()[:16], \
                                                        request.POST.get("username"), request.POST.get("password"), \
                                                        request.POST.get("confirm_password")
        if password != confirm_password:
            return render(request, "auth/register.html", {"error": "Passwords don't match!", "user": None})
        if SQL("User").select("*").where(f'user_id = "{user_id}"').run(as_object=True):
            return render(request, "auth/register.html", {"error": "User with this ID already exists!", "user": None})
        SQL("User").insert(user_id=f'"{user_id}"', username=f'"{username}"', password=f'"{encrypt(password)}"').run()
        return set_login_cookies(user_id, encrypt(password))

    return {"GET": get, "POST": post}


@router
def login():
    def get(request: WSGIRequest):
        return render(request, "auth/login.html", {"user": None})

    def post(request: WSGIRequest):
        user_id, password = request.POST.get("user_id"), encrypt(request.POST.get("password"))
        if SQL("User").select("*").where(f'user_id = "{user_id}" AND password = "{password}"').run(as_object=True):
            return set_login_cookies(user_id, password)
        return render(request, "auth/login.html", {"user": None, "error": "Invalid ID or Password!"})

    return {"GET": get, "POST": post}


def logout(_):
    response = redirect("/")
    response.delete_cookie("credentials")
    return response


def delete(request: WSGIRequest):
    credentials = request.COOKIES.get("credentials")
    if not credentials: return redirect("/")
    user_id, password = credentials.split(" ")
    SQL("User").delete().where(f'user_id = "{user_id}" AND password = "{password}"').run()
    return redirect("/")
