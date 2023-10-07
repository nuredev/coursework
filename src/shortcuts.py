from dataclasses import dataclass
from functools import wraps
from hashlib import sha512
from typing import Optional, List

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseBadRequest
from django.urls import path

from _database.scheme import User, Mark
from _database.sql import SQL


class Path:
    def __init__(self, fn):
        self.fn = fn

    def link(self, *paths):
        if not paths: return path(self.fn.__name__, self.fn, name=self.fn.__name__)
        return path("/".join(paths), self.fn, name=self.fn.__name__)


def router(fn):
    @wraps(fn)
    def wrapper(request: WSGIRequest, *args, **kwargs):
        pg = fn().get(request.method)
        if pg is not None: return pg(request, *args, **kwargs)
        return HttpResponseBadRequest(b"Invalid request method!")

    return wrapper


def encrypt(string: str):
    return sha512(bytes(string, "utf-8")).hexdigest()


def fetch_user(request: WSGIRequest) -> Optional[User]:
    credentials = request.COOKIES.get("credentials")
    if not credentials: return None
    user_id, password = credentials.split(" ")
    return SQL("User").select("*").where(
        f'user_id = "{user_id}" AND password = "{password}"').run(as_object=True, first=True)


def fetch_topics(where: str = None):
    return SQL("Topic").select("*").where(where).run(as_object=True, first=bool(where))


def fetch_questions(where: str = None):
    return SQL("Question").select("*").where(where).run(as_object=True)


@dataclass
class TopicRatio:
    topic_id: int
    ratio: float


def feed_auto(user: User):
    #  Get all questions by user, set their ratio to 0.1 as those are ones user is probably not good at
    questions = SQL("Question").select("*").where(f'user_id = "{user.user_id[1:]}"').run(as_object=True)
    topics = [TopicRatio(q.topic_id, 0.1) for q in questions]

    #  Get all answers by user that weren't replies to their own questions
    answers = SQL("Answer").select("*").where(
        f'user_id = "{user.user_id[1:]}" AND question_id NOT IN ({", ".join([str(q.question_id) for q in questions])})'
    ).run(as_object=True)
    for answer in answers:
        topic_id = SQL("Question").select("*").where(f'question_id = {answer.question_id}').run(
            as_object=True, first=True).topic_id
        new_topics = []
        for topic in topics:
            if topic_id == topic.topic_id:
                new_topics.append(TopicRatio(topic_id, 0.6))
            else:
                new_topics.append(TopicRatio(topic_id, 1.0))
        topics = new_topics
    new_topics = []
    for topic in topics:
        if topic not in new_topics: new_topics.append(topic)

    topics.sort(key=lambda m: m.ratio, reverse=True)

    if not topics: return []

    questions = []
    for topic in topics[:3]:
        questions = [*questions, *SQL("Question").select("*").where(f'NOT user_id = "{user.user_id[1:]}" AND topic_id = {topic.topic_id} AND is_solved = FALSE').run(
            as_object=True)[:4]]

    qs = SQL("Question").select("*").where(
        f'NOT user_id = "{user.user_id[1:]}" AND question_id NOT IN '
        f'({",".join([str(q.question_id) for q in questions])}) AND is_solved = FALSE').run(as_object=True)

    return [*questions, *qs[:6 - len(questions)]]
