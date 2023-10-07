from typing import Union, List

from colorama import Fore
from django.db import connection

from _database.scheme import TABLES, User, Mark, Redaction, Answer, Question, Rating, Topic


def count_marks(marks: List[Mark]) -> int:
    result = 0
    for mark in marks:
        result += 1 if mark.is_positive else -1
    return result


def execute(prompt: str, ignore: bool = False, describe: bool = False) -> Union[tuple, str]:
    with connection.cursor() as cursor:
        try:
            cursor.execute(prompt)
            result = cursor.fetchall()
            if describe: result = tuple([[i[0] for i in cursor.description], *result])
        except Exception as e:
            result = str(e)
            if not ignore:
                print(Fore.LIGHTBLACK_EX + f"\n[Executing]\n{Fore.MAGENTA}{prompt}" + Fore.RESET)
                print(Fore.RED + f"Error: {e}\n" + Fore.RESET)
    return result


class SQL:
    def __init__(self, table: str):
        self.table = table
        self.command = []

    def select(self, target: str):
        self.command.append(f"SELECT {target} FROM {self.table}")
        return self

    def insert(self, **kwargs):
        self.command.append(f"INSERT INTO {self.table} ( " + ", ".join(kwargs.keys())
                            + " ) VALUES ( " + ", ".join([str(v) for v in kwargs.values()]) + ")")
        return self

    def update(self, **kwargs):
        self.command.append(f"UPDATE {self.table} SET " + ", ".join(
            [f"{key}={list(kwargs.values())[i]}" for i, key in enumerate(kwargs.keys())]
        ))
        return self

    def create(self):
        self.command += [f"CREATE TABLE {self.table} (", ", ".join(TABLES[self.table]), ")"]
        return self

    def delete(self):
        self.command.append(f"DELETE FROM {self.table}")
        return self

    def where(self, condition):
        if condition: self.command.append(f"WHERE {condition}")
        return self

    def order_by(self, ordering: str):
        self.command.append(f"ORDER BY {ordering}")
        return self

    def run(self, as_object: bool = False, first: bool = False, ignore: bool = False, describe: bool = False,
            ratio: float = None) -> Union[tuple, str, List[Union[User, Mark, Redaction, Answer, Question, Rating, Topic
    ]], Union[User, Mark, Redaction, Answer, Question, Rating, Topic]]:
        sql = execute(" ".join(self.command) + ";", ignore, describe)
        if not as_object: return sql
        if not sql: return [] if not first else None
        result = []
        if self.table == "User":
            result = [User(*row) for row in sql if row]
        elif self.table == "Topic":
            result = [Topic(*row) for row in sql if row]
        elif self.table == "Rating":
            result = [Rating(*row) for row in sql if row]
        elif self.table == "Question":
            for row in sql:
                if row:
                    q = Question(*row)
                    q.rating = count_marks(
                        SQL("Mark").select("*").where(f"rating_id = {q.rating_id}").run(as_object=True))
                    q.user = SQL("User").select("*").where(f"user_id = \"{q.user_id}\"").run(as_object=True, first=True)
                    q.topic = SQL("Topic").select("*").where(f"topic_id = {q.topic_id}").run(as_object=True, first=True)
                    q.rating_users_positive = [f'@{i.user_id}' for i in
                                               SQL("Mark").select("*").where(f"rating_id = {q.rating_id}").run(
                                                   as_object=True) if i.is_positive]
                    q.rating_users_negative = [f'@{i.user_id}' for i in
                                               SQL("Mark").select("*").where(f"rating_id = {q.rating_id}").run(
                                                   as_object=True) if not i.is_positive]
                    q.ratings = len(SQL("Mark").select("*").where(f"rating_id = {q.rating_id}").run(as_object=True))
                    result.append(q)
        elif self.table == "Answer":
            for row in sql:
                if row:
                    q = Answer(*row)
                    q.rating = count_marks(
                        SQL("Mark").select("*").where(f"rating_id = {q.rating_id}").run(as_object=True))
                    q.user = SQL("User").select("*").where(f"user_id = \"{q.user_id}\"").run(as_object=True, first=True)
                    q.redactions = SQL("Redaction").select("*").where(f"answer_id = {q.answer_id}").order_by(f'creation_date DESC').run(as_object=True)
                    q.rating_users_positive = [f'@{i.user_id}' for i in
                                               SQL("Mark").select("*").where(f"rating_id = {q.rating_id}").run(
                                                   as_object=True) if i.is_positive]
                    q.rating_users_negative = [f'@{i.user_id}' for i in
                                               SQL("Mark").select("*").where(f"rating_id = {q.rating_id}").run(
                                                   as_object=True) if not i.is_positive]
                    q.ratings = len(SQL("Mark").select("*").where(f"rating_id = {q.rating_id}").run(as_object=True))
                    result.append(q)
        elif self.table == "Redaction":
            result = [Redaction(*row) for row in sql]
        elif self.table == "Mark":
            result = [Mark(*row) for row in sql]
        if ratio is not None:
            for row in result:
                row.ratio = ratio
                return row
        return result if not first or not result else result[0]
