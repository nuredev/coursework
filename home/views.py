from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Union, Dict

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect

from _database.scheme import Rating, User, Mark, Redaction, Answer, Question, Topic
from _database.sql import SQL, count_marks
from src.shortcuts import router, fetch_user, encrypt, fetch_topics, fetch_questions, feed_auto


@router
def feed():
    def get(request: WSGIRequest):
        usr = fetch_user(request)
        if not usr: return redirect("auth/login")

        return render(request, "index/feed.html", {"user": fetch_user(request), "questions": feed_auto(usr)})

    return {"GET": get}


@router
def profile():
    def get(request: WSGIRequest):
        return render(request, "index/profile.html", {"user": fetch_user(request)})

    def post(request: WSGIRequest):
        username, picture, description, password, confirm_password = request.POST.get("username"), request.POST.get(
            "picture"), request.POST.get("description"), request.POST.get("password"), request.POST.get(
            "confirm_password")
        SQL("User").update(
            username=f'"{username}"',
            picture=f'"{picture}"',
        ).where(f'user_id = "{fetch_user(request).user_id[1:]}"').run()
        if description and description != "No description":
            SQL("User").update(
                description=f'"{description}"'
            ).where(f'user_id = "{fetch_user(request).user_id[1:]}"').run()
        if password:
            if password == confirm_password:
                SQL("User").update(password=f'"{encrypt(password)}"').where(
                    f'user_id = "{fetch_user(request).user_id[1:]}"').run()
            else:
                return render(request, "index/profile.html",
                              {"user": fetch_user(request), "error": "Passwords don't match!"})
        return get(request)

    return {"GET": get, "POST": post}


@router
def browse():
    def get(request: WSGIRequest):
        return render(request, "index/browse.html", {"user": fetch_user(request), "topics": fetch_topics()})

    return {"GET": get}


@router
def browse_topic():
    def get(request: WSGIRequest, index: str):
        return render(request, "index/browse/topic.html",
                      {"user": fetch_user(request),
                       "topic": fetch_topics(f'topic_id = {index[1:]}'),
                       "questions": fetch_questions(f'topic_id = {index[1:]}')})

    def post(request: WSGIRequest, index: str):  # Ask a question
        snippet, message_body = request.POST.get("snippet"), request.POST.get("message_body")
        rating_id = SQL("Rating").select("rating_id").order_by("rating_id DESC").run(as_object=True,
                                                                                     first=True) or Rating(-1)
        SQL("Rating").insert(rating_id=rating_id.rating_id + 1).run()
        if not fetch_user(request): return redirect("/auth/login")
        SQL("Question").insert(
            snippet=f'"{snippet}"',
            message_body=f'"{message_body}"',
            user_id=f'"{fetch_user(request).user_id[1:]}"',
            topic_id=index[1:],
            rating_id=rating_id.rating_id + 1
        ).run()
        return redirect(
            f'/browse/question/{SQL("Question").select("*").order_by("question_id DESC").run(as_object=True, first=True).question_id}')

    return {"GET": get, "POST": post}


@router
def browse_question():
    def get(request: WSGIRequest, question_id: int):
        return render(request, "index/browse/question.html", {
            "user": fetch_user(request),
            "question": SQL("Question").select("*").where(f'question_id = {question_id}').run(as_object=True,
                                                                                              first=True),
            "answers": SQL("Answer").select("*").where(f'question_id = {question_id}').order_by(
                f'(SELECT COUNT(*) FROM Mark WHERE Mark.rating_id = Answer.rating_id) DESC').run(as_object=True),
            "now": datetime.now().strftime("%d %b %Y - %H:%M:%S")
        })

    def post(request: WSGIRequest, question_id: int):
        rating_id = SQL("Rating").select("rating_id").order_by("rating_id DESC").run(
            as_object=True, first=True) or Rating(-1)
        SQL("Rating").insert(rating_id=rating_id.rating_id + 1).run()
        SQL("Answer").insert(
            summary=f'"{request.POST.get("summary")}"',
            message_body='"' + request.POST.get("message_body").replace('"', "'") + '"',
            user_id=f'"{fetch_user(request).user_id[1:]}"',
            question_id=question_id,
            resource_links=f'"{request.POST.get("sources")}"',
            rating_id=rating_id.rating_id + 1,
        ).run()
        return redirect(f"/browse/question/{question_id}")

    return {"GET": get, "POST": post}


def browse_question_close(request: WSGIRequest, question_id: int):
    SQL("Question").update(is_solved=1).where(
        f'question_id = {question_id} AND user_id = "{fetch_user(request).user_id[1:]}"').run()
    return redirect(f"/browse/question/{question_id}")


def browse_question_reopen(request: WSGIRequest, question_id: int):
    SQL("Question").update(is_solved=0).where(
        f'question_id = {question_id} AND user_id = "{fetch_user(request).user_id[1:]}"').run()
    return redirect(f"/browse/question/{question_id}")


@router
def manage():
    def get(request: WSGIRequest):
        return render(request, "index/manage.html", {"user": fetch_user(request)})

    def post(request: WSGIRequest):
        table = request.POST.get("table")
        sql = SQL(table).select("*").where(f'{table.lower()}_id = "{request.POST.get("id")}"').run(as_object=True,
                                                                                                   first=True)
        if sql is not None and type(sql) is not list and type(sql) is not tuple:
            data: dict = request.POST.dict()
            for i in ["csrfmiddlewaretoken", "table", "id"]: data.pop(i)
            new_data = {}
            for key in data:
                value = data[key]
                if value == "[NULL]":
                    new_data[key] = "NULL"
                elif value == "[AUTO]":
                    rating_id = SQL("Rating").select("rating_id").order_by("rating_id DESC").run(
                        as_object=True, first=True) or Rating(-1)
                    SQL("Rating").insert(rating_id=rating_id.rating_id + 1).run()
                    new_data[key] = rating_id.rating_id + 1
                elif value != "[encrypted]":
                    new_data[key] = f'"{value}"' if not key == "password" else f'"{encrypt(value)}"'
            SQL(table).update(**new_data).where(f'{table.lower()}_id = "{request.POST.get("id")}"').run()
        else:
            data: dict = request.POST.dict()
            for i in ["csrfmiddlewaretoken", "table", "id"]: data.pop(i)
            new_data = {}
            for key in data:
                value = data[key]
                if value == "[NULL]":
                    new_data[key] = "NULL"
                elif value == "auto":
                    rating_id = SQL("Rating").select("rating_id").order_by("rating_id DESC").run(
                        as_object=True, first=True) or Rating(-1)
                    SQL("Rating").insert(rating_id=rating_id.rating_id + 1).run()
                    new_data[key] = rating_id.rating_id + 1
                elif value != "[encrypted]":
                    new_data[key] = f'"{value}"' if not key == "password" else f'"{encrypt(value)}"'
            uuid = {f'{table.lower()}_id': f'"{request.POST.get(f"{table.lower()}_id")}"'} if request.POST.get(
                f"{table.lower()}_id") else {}
            SQL(table).insert(**uuid, **new_data).run()
        return redirect(f"/manage#{table}")

    return {"GET": get, "POST": post}


@router
def user():
    def get(request: WSGIRequest, user_id: str):
        questions = SQL("Question").select("*").where(f'user_id = "{user_id[1:]}"').run(as_object=True)
        answers = SQL("Answer").select("*").where(f'user_id = "{user_id[1:]}"').run(as_object=True)
        q_marks = [SQL("Mark").select("*").where(f"rating_id = {q.rating_id}").run(as_object=True, first=True) for q in
                   questions]
        a_marks = [SQL("Mark").select("*").where(f"rating_id = {a.rating_id}").run(as_object=True, first=True) for a in
                   answers]
        print(q_marks, a_marks)
        return render(request, "index/user.html", {
            "user": fetch_user(request),
            "profile": SQL("User").select("*").where(f'user_id = "{user_id[1:]}"').run(as_object=True, first=True),
            "questions": questions,
            "answers": answers,
            "question_count": len(questions),
            "answer_count": len(answers),
            "user_rating": count_marks([
                *q_marks,
                *a_marks
            ]),
            "ratings": len(q_marks) + len(a_marks),
            "now": datetime.now().strftime("%d %b %Y - %H:%M:%S")
        })

    def post(request: WSGIRequest, user_id: str):
        return get(request, user_id)

    return {"GET": get, "POST": post}


@router
def search():
    def post(request: WSGIRequest):
        query = request.POST.get("query")
        table_name = request.POST.get("table")
        table_rows = SQL(table_name).select("*").run(as_object=True)
        sort = request.POST.get("sort")
        is_ascending = int(request.POST.get("is_ascending"))
        filter_topic = request.POST.get("topic")
        filter_solved = int(request.POST.get("is_solved"))
        matches = []
        object_matches: List[Union[User, Mark, Redaction, Answer, Question, Rating, Topic]] = []

        if query:
            def match(table_id: str, *attributes: str):
                for row in table_rows:
                    for attribute in attributes:
                        if not str(getattr(row, attribute)).lower().find(query.lower()) > -1:
                            text = str(getattr(row, attribute)).lower().split(" ")
                            length = len(query.lower().split(" "))
                            for k in range(int(len(text) / length)):
                                ratio = SequenceMatcher(a=" ".join(text[k * length:k * length + length]),
                                                        b=query.lower()).quick_ratio()
                                if ratio > 0.8: matches.append(
                                    f'{table_id}|{attribute}|{round(ratio, 3)}=={getattr(row, attribute)}')
                        else:
                            matches.append(f'{table_id}|{attribute}|1.0=={getattr(row, attribute)}')
                            break

            match table_name:
                case "User":
                    match("user_id", "username", "user_id", "description")
                case "Question":
                    match("question_id", "snippet", "message_body")
                case "Answer":
                    match("answer_id", "summary", "message_body")
                case "Topic":
                    match("topic_id", "name", "description")

            for match in matches:
                keys, value = match.split("==")[0], "==".join(match.split("==")[1:])
                key, attribute, ratio = keys.split("|")[0], keys.split("|")[1], float(keys.split("|")[2])
                object_matches.append(
                    SQL(key[:-3].capitalize()).select("*").where(attribute + " = " + f'"{value}"').run(as_object=True,
                                                                                                       first=True,
                                                                                                       ratio=ratio))
        else:
            for sql in SQL(table_name).select("*").run(as_object=True):
                sql.ratio = 1.0
                object_matches.append(sql)

        object_matches = [o for o in object_matches if o]
        match sort:
            case "creation_date":
                object_matches.sort(key=lambda o: datetime.strptime(o.creation_date, "%d %b %Y - %H:%M:%S"),
                                    reverse=not is_ascending)
            case "relevance":
                object_matches.sort(key=lambda o: o.ratio, reverse=not is_ascending)

        if filter_topic != "*" and table_name in ["Question", "Answer"]:
            new_list = []
            for i, match in enumerate(object_matches):
                if match.topic_id == int(filter_topic):
                    new_list.append(match)
            object_matches = new_list
        if filter_solved and table_name in ["Question"]:
            new_list = []
            for i, match in enumerate(object_matches):
                if match.is_solved:
                    new_list.append(match)
            object_matches = new_list

        results = [str(r) for r in object_matches]
        return render(request, "index/search_results.html", {
            "results": "\n".join(results),
            "query": query,
            "table": table_name,
            "sort": sort,
            "is_ascending": int(is_ascending),
            "topics": fetch_topics(),
            "filter_topic": int(filter_topic if filter_topic != "*" else -1),
            "filter_solved": int(filter_solved),
        })

    return {"POST": post}


@router
def redact():
    def post(request: WSGIRequest, question_id: int, answer_id: int):
        SQL("Redaction").insert(
            user_id=f'"{fetch_user(request).user_id[1:]}"',
            answer_id=answer_id,
            message_body=f'"{request.POST.get("message_body")}"',
        ).run()
        return redirect(f"/browse/question/{question_id}#answer{answer_id}")

    return {"POST": post}


@router
def statistics():
    def sort_qa(qa: Union[Question, Answer]):
        marks = SQL("Mark").select("*").where(f"rating_id = {qa.rating_id}").run(as_object=True)
        if len(marks) == 0: return 0
        return count_marks(marks) * len(marks)

    def get_best_user_qas():
        result = []
        for usr in SQL("User").select("*").run(as_object=True):
            questions = [q for q in
                         SQL("Question").select("*").where(f'user_id = "{usr.user_id[1:]}"').run(as_object=True)]
            questions.sort(key=lambda o: sort_qa(o), reverse=True)
            answers = [a for a in SQL("Answer").select("*").where(f'user_id = "{usr.user_id[1:]}"').run(as_object=True)]
            answers.sort(key=lambda o: sort_qa(o), reverse=True)
            result.append(f'<details><summary><img src="{usr.picture}" width="32px" height="32px">'
                          f'<span>{usr.user_id}</span></summary><h1>Questions:</h1>' + "".join([
                f'''
                <div>
                    <a href="/browse/question/{o.question_id}">{o.snippet}</a>
                    <span>{o.message_body}</span>
                    <strong>{o.user_id}<span class="space">{o.rating} / {o.ratings}</span>{o.creation_date}</strong>
                </div>
                ''' for o in questions[:5]
            ]) + "<hr><h1>Answers:</h1>" + "".join([
                f'''
                <div>
                    <a href="/browse/question/{o.question_id}#answer{o.answer_id}">{o.summary}</a>
                    <span>{o.message_body}</span>
                    <strong>{o.user_id}<span class="space">{o.rating} / {o.ratings}</span>{o.creation_date}</strong>
                </div>
                ''' for o in answers[:5]
            ]) + '</details>')

        return "".join(result)

    def get_best_topics():
        result = []
        topics: List[Dict[str, Union[int, Topic]]] = []

        for topic in SQL("Topic").select("*").run(as_object=True):
            questions = [q for q in
                         SQL("Question").select("*").where(f'topic_id = {topic.topic_id}').run(as_object=True)]
            topics.append({"topic": topic, "sum": sum([sort_qa(q) for q in questions[:5]])})

        topics.sort(key=lambda t: t.get("sum"), reverse=True)
        for topic in topics[:5]:
            result.append(f'<details><summary><img src="{topic.get("topic").picture}" width="32px" height="32px">'
                          f'<span>{topic.get("topic").name}</span><span class="space"></span>Rating: {topic.get("sum")}</summary></details>')

        return "".join(result[:5])

    def get_user_ratings():
        class RTopic:
            def __init__(self, topic: Topic, rating: int):
                self.topic: Topic = topic
                self.rating = rating

            def add(self, rating: int):
                self.rating += rating

        class UserRating:
            def __init__(self, usr):
                self.user: User = usr
                self.data: List[RTopic] = []

            def set(self, topic: Topic, rating: int):
                for rt in self.data:
                    if rt.topic == topic:
                        return rt.add(rating)
                self.data.append(RTopic(topic, rating))

        result = []
        users: List[UserRating] = []

        for usr in SQL("User").select("*").run(as_object=True):
            users.append(UserRating(usr))
            questions = SQL("Question").select("*").where(f'user_id = "{usr.user_id[1:]}"').run(as_object=True)
            answers = SQL("Answer").select("*").where(f'user_id = "{usr.user_id[1:]}"').run(as_object=True)
            for question in questions:
                users[-1].set(
                    SQL("Topic").select("*").where(f'topic_id = {question.topic_id}').run(as_object=True, first=True),
                    sort_qa(question),
                )
            for answer in answers:
                question = SQL("Question").select("*").where(f'question_id = {answer.question_id}').run(as_object=True,
                                                                                                        first=True)
                users[-1].set(
                    SQL("Topic").select("*").where(f'topic_id = {question.topic_id}').run(as_object=True, first=True),
                    sort_qa(question),
                )
        for rtopic in users:
            result.append(f'<details><summary><img src="{rtopic.user.picture}" width="32px" height="32px">'
                          f'<span>{rtopic.user.user_id}</span></summary>' + "".join([
                f'''<div>
                                <a href="/browse/@{t.topic.topic_id}">{t.topic.name}</a>
                                <span>{t.topic.description}</span>
                                <strong>Rating: {t.rating}</strong>
                            </div>''' for t in rtopic.data
            ]) + "</details>")

        return "".join(result)

    def most_inactive_users():
        result = []
        users = []
        for usr in SQL("User").select("*").run(as_object=True):
            questions = SQL("Question").select("*").where(f'user_id = "{usr.user_id[1:]}"').run(as_object=True)
            answers = SQL("Answer").select("*").where(f'user_id = "{usr.user_id[1:]}"').run(as_object=True)
            combined: List[Union[Question, Answer]] = [*questions, *answers]
            combined.sort(key=lambda o: datetime.strptime(o.creation_date, "%d %b %Y - %H:%M:%S"), reverse=False)
            if not combined:
                users.append([usr, datetime.strptime(usr.creation_date, "%d %b %Y - %H:%M:%S")])
            else:
                users.append([usr, datetime.strptime(combined[0].creation_date, "%d %b %Y - %H:%M:%S")])
        users.sort(key=lambda o: o[1], reverse=False)

        for usr in users[:5]:
            result.append(f'<details><summary><img src="{usr[0].picture}" width="32px" height="32px">'
                          f'<span>{usr[0].user_id}</span><span class="space"></span>Last activity: {usr[1]}</summary></details>')

        return "".join(result)

    def get(request: WSGIRequest):
        return render(request, "index/statistics.html", {
            "best_user_qas": get_best_user_qas(),
            "best_topics": get_best_topics(),
            "user_ratings": get_user_ratings(),
            "most_inactive_users": most_inactive_users(),
        })

    return {"GET": get}
