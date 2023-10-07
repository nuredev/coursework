from datetime import datetime, timedelta

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from _database.scheme import TABLES
from _database.sql import SQL
from src.shortcuts import fetch_user

editButton = '<button class="button single edit" onclick="editRow(this)"><svg xmlns="http://www.w3.org/2000/svg" ' \
             'width="16" height="16" ' \
             'viewBox="0 0 16 16" fill="currentColor" class="eyecons"><path d="m15.086 5.328c1.2188-1.2189 ' \
             '1.2188-3.195 0-4.4139-1.2189-1.2188-3.195-1.2188-4.4139-1e-7l-10.672 ' \
             '10.672v4.4141h4.4141l5.3359-5.336zm-5.0859-0.91396 1.5859 1.5859-8 8h-1.5859v-1.5859z" ' \
             'fill-rule="evenodd" /></svg></button>'
deleteButton = '<button class="button single delete" onclick="deleteRow(this)"><svg ' \
               'xmlns="http://www.w3.org/2000/svg" width="16" height="16" ' \
               'viewBox="0 0 16 16" fill="currentColor" class="eyecons"><path d="m6 0c-1.108 0-2 0.892-2 2h-2c-0.554 ' \
               '0-1 0.446-1 1s0.446 1 1 1v9c0 1.662 1.338 3 3 3h6c1.662 0 3-1.338 3-3v-9c0.554 0 1-0.446 ' \
               '1-1s-0.446-1-1-1h-2c0-1.108-0.892-2-2-2h-4zm-2 4h8v9c0 0.554-0.446 1-1 1h-6c-0.554 ' \
               '0-1-0.446-1-1v-9zm2.334 2c-0.554 0-1 0.446-1 1v4c0 0.554 0.446 1 1 1s1-0.446 ' \
               '1-1v-4c0-0.554-0.446-1-1-1zm3.332 0c-0.554 0-1 0.446-1 1v4c0 0.554 0.446 1 1 1 0.554 0 1-0.446 ' \
               '1-1v-4c0-0.554-0.446-1-1-1z" fill-rule="evenodd" /></svg></button> '


def render_table(sql):
    return HttpResponse(f'''
        <table>
            <thead>
                <tr>
                    {"".join(["<td>" + str(i) + "</td>" for i in sql[0]])}
                    <td></td><td></td>
                </tr>
            </thead>
            <tbody>''' + "".join([
        '<tr>' + "".join([
            f'<td class="column" data-column="{sql[0][idx]}">{column}</td>' if column is not None else
            f'<td class="column null" data-column="{sql[0][idx]}">[NULL]</td>'
            for idx, column in enumerate(row)
        ]) + f'<td>{editButton}</td><td>{deleteButton}</td></tr>' for row in sql[1:]
    ]) + "</tbody></table>")


@xframe_options_exempt
@csrf_exempt
def run_sql(request: WSGIRequest):
    sql_runner = SQL("")
    sql_runner.command = [request.POST.get("command").replace(";", "")]
    sql = sql_runner.run(describe=True)
    if type(sql) is str: return HttpResponse(f'<section class="bar red"><strong>Error:</strong> {sql}</section>')
    return render_table(sql)


def fetch_table(request: WSGIRequest, table_name: str):
    sql = SQL(table_name).select("*").run(describe=True)
    if type(sql) is str: return HttpResponse(f'<section class="bar red"><strong>Error:</strong> {sql}</section>')
    return render_table(sql)


def delete_from_table(request: WSGIRequest, table_name: str, column: str, value: str):
    if value.isnumeric():
        SQL(table_name).delete().where(f'{column} = {value}').run()
    else:
        SQL(table_name).delete().where(f'{column} = "{value}"').run()
    return HttpResponse(b"OK")


def table_info(request: WSGIRequest, table_name: str):
    def get_type(name: str):
        match name.split(":")[0]:
            case "INTEGER":
                return "number"
            case "VARCHAR":
                return "text"
            case "CHAR":
                return "text"
            case "TEXT":
                return "textarea"
            case "DATETIME":
                return "datetime-local"

    def get_options(name: str) -> list:
        if name == "rating_id" and table_name != "Mark": return ['<option value="auto">[AUTO]</option>']
        sql = SQL(name.split("_")[0].capitalize()).select("*").run()
        return [
            f'<option value="{option[0]}">({option[0]}) {option[1]}</option>'
            for option in sql
        ]

    fields = [
        {
            "name": field.split("  ")[0],
            "default": "" if field.split("  ")[1] != "DATETIME" else (datetime.now() + timedelta(hours=2)).strftime(
                "%Y-%m-%dT%H:%M:%S"),
            "type": get_type(field.split("  ")[1].replace(")", "").replace("(", ":")),
            "optional": "NOT NULL" not in field,
            "primary_key": "PRIMARY KEY" in field,
            "foreign_key": bool(
                [f for f in TABLES.get(table_name) if "REFERENCES" in f and field.split("  ")[0] in f]),
        } for field in TABLES.get(table_name) if
        ("PRIMARY KEY" not in field or "AUTOINCREMENT" not in field) and ("creation_date" not in field) and (
                    "FOREIGN KEY" not in field)
    ]

    output = []

    for field in fields:
        if field.get("foreign_key"):
            output.append(f"""
                <div class="inputbox">
                    <select id="{field.get('name')}" name="{field.get('name')}">
                        {"".join(get_options(field.get('name')))}
                    </select>
                    <label for="{field.get('name')}">{field.get('name').replace("_", " ").capitalize()}</label>
                </div>
            """)
        elif field.get("type") == "textarea":
            output.append(f"""
                <div class="inputbox">
                    <textarea name="{field.get('name')}" placeholder=" " id="{field.get('name')}"></textarea>
                    <label for="{field.get('name')}">{field.get('name').replace("_", " ").capitalize()}</label>
                </div>
            """)
        else:
            output.append(f"""
                <div class="inputbox">
                    <input name="{field.get('name')}" type="{field.get('type')}" value="{field.get('default')}" {"" if not field.get('max') else f'maxlength="{field.get("max")}"'} placeholder=" " id="{field.get('name')}">
                    <label for="{field.get('name')}">{field.get('name').replace("_", " ").capitalize()}</label>
                </div>
            """)

    return HttpResponse(bytes("\n".join(output), "utf-8"))


def vote(request: WSGIRequest, rating_id: int, is_positive: int):
    user = fetch_user(request)
    if not user: return HttpResponseNotAllowed(b"NOT ALLOWED")
    SQL("Mark").delete().where(f'user_id = "{user.user_id[1:]}" AND rating_id = {rating_id}').run()
    if is_positive in [0, 1]: SQL("Mark").insert(is_positive=is_positive, user_id=f'"{user.user_id[1:]}"', rating_id=rating_id).run()
    return HttpResponse(b"OK")
