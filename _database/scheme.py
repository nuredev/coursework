from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Union, List, Dict, Literal


@dataclass
class User:
    user_id: str
    username: str
    description: str
    password: str
    picture: str
    creation_date: Union[datetime, str]

    def __str__(self):
        try:
            return f"""
                    <section class="search_result">
                        <header>
                            <img src="{self.picture}">
                            <h1>{self.username}</h1>
                            <span class="space"></span>
                            <span>~{self.ratio * 100}%</span>
                        </header>
                        <p>{self.description}</p>
                        <footer>
                            <a href="/user/{self.user_id}">{self.user_id}</a>
                            <span class="space"></span>
                            <span>{self.creation_date}</span>
                        </footer>
                    </section>
                    """
        except:
            return f"""
                    <section class="search_result">
                        <header>
                            <img src="{self.picture}">
                            <h1>{self.username}</h1>
                            <span class="space"></span>
                        </header>
                        <p>{self.description}</p>
                        <footer>
                            <a href="/user/{self.user_id}">{self.user_id}</a>
                            <span class="space"></span>
                            <span>{self.creation_date}</span>
                        </footer>
                    </section>
                    """

    def __post_init__(self):
        self.user_id = f'@{self.user_id}'
        self.password = '[encrypted]'
        self.picture = self.picture or "https://pwco.com.sg/wp-content/uploads/2020/05/" \
                                       "Generic-Profile-Placeholder-v3-800x800.png"
        creation_date = self.creation_date + timedelta(hours=2)
        self.creation_date = creation_date.strftime("%d %b %Y - %H:%M:%S")
        if not self.description: self.description = "No description"


@dataclass
class Topic:
    topic_id: int
    name: str
    description: str
    picture: str

    def __str__(self):
        try:
            return f"""
                    <section class="search_result">
                        <header>
                            <img src="{self.picture}">
                            <h1><a href="/browse/@{self.topic_id}">{self.name}</a></h1>
                            <span class="space"></span>
                            <span>~{self.ratio * 100}%</span>
                        </header>
                        <p>{self.description}</p>
                    </section>
                    """
        except:
            return f"""
                    <section class="search_result">
                        <header>
                            <img src="{self.picture}">
                            <h1><a href="/browse/@{self.topic_id}">{self.name}</a></h1>
                            <span class="space"></span>
                        </header>
                        <p>{self.description}</p>
                    </section>
                    """

    def __post_init__(self):
        if not self.description: self.description = "No description"


@dataclass
class Rating:
    rating_id: int


@dataclass
class Question:
    question_id: int
    snippet: str
    message_body: str
    is_solved: Union[int, bool]
    creation_date: Union[datetime, str]
    user_id: str
    topic_id: int
    rating_id: int

    def __str__(self):
        try:
            return f"""
                    <section class="search_result">
                        <header>
                            <h1><a href="/browse/question/{self.question_id}">{self.snippet}</a></h1>
                            <span class="space"></span>
                            <span>~{self.ratio * 100}%</span>
                        </header>
                        <p>{self.message_body}</p>
                        <footer>
                            <a href="/user/@{self.user_id}">By @{self.user_id}</a>
                            <span class="space"></span>
                            <span>{self.creation_date}</span>
                        </footer>
                    </section>
                    """
        except:
            return f"""
                    <section class="search_result">
                        <header>
                            <h1><a href="/browse/question/{self.question_id}">{self.snippet}</a></h1>
                            <span class="space"></span>
                        </header>
                        <p>{self.message_body}</p>
                        <footer>
                            <a href="/user/@{self.user_id}">By @{self.user_id}</a>
                            <span class="space"></span>
                            <span>{self.creation_date}</span>
                        </footer>
                    </section>
                    """
    
    def __post_init__(self):
        creation_date = self.creation_date + timedelta(hours=2)
        self.creation_date = creation_date.strftime("%d %b %Y - %H:%M:%S")
        self.message_body = self.message_body.replace("\n", "<br>")


@dataclass
class Answer:
    answer_id: int
    summary: str
    message_body: str
    resource_links: str
    creation_date: Union[datetime, str]
    user_id: str
    question_id: int
    rating_id: int

    def __str__(self):
        try:
            return f"""
                    <section class="search_result">
                        <header>
                            <h1><a href="/browse/question/{self.question_id}">{self.summary}</a></h1>
                            <span class="space"></span>
                            <span>~{self.ratio * 100}%</span>
                        </header>
                        <p>{self.message_body}</p>
                        <footer>
                            <a href="/user/@{self.user_id}">By @{self.user_id}</a>
                            <span class="space"></span>
                            <span>{self.creation_date}</span>
                        </footer>
                    </section>
                    """
        except:
            return f"""
                    <section class="search_result">
                        <header>
                            <h1><a href="/browse/question/{self.question_id}">{self.summary}</a></h1>
                            <span class="space"></span>
                        </header>
                        <p>{self.message_body}</p>
                        <footer>
                            <a href="/user/@{self.user_id}">By @{self.user_id}</a>
                            <span class="space"></span>
                            <span>{self.creation_date}</span>
                        </footer>
                    </section>
                    """

    def __post_init__(self):
        creation_date = self.creation_date + timedelta(hours=2)
        self.message_body = self.message_body.replace("\n", "<br>")
        self.creation_date = creation_date.strftime("%d %b %Y - %H:%M:%S")


@dataclass
class Redaction:
    redaction_int: int
    message_body: str
    creation_date: Union[datetime, str]
    user_id: str
    answer_id: int

    def __post_init__(self):
        creation_date = self.creation_date + timedelta(hours=2)
        self.creation_date = creation_date.strftime("%d %b %Y - %H:%M:%S")


@dataclass
class Mark:
    mark_id: int
    is_positive: Union[int, bool]
    user_id: str
    rating_id: int

    def __post_init__(self):
        self.is_positive = self.is_positive == 1


TABLES: Dict[str, List[str]] = {
    "User": [
        "user_id  VARCHAR(16)  PRIMARY KEY  NOT NULL",
        "username  VARCHAR(32)  NOT NULL",
        "description  TEXT  NULL",
        "password  CHAR(128)  NOT NULL",
        "picture  VARCHAR(512)  NULL",
        "creation_date  DATETIME  NOT NULL   DEFAULT CURRENT_TIMESTAMP",
    ],
    "Topic": [
        "topic_id  INTEGER  PRIMARY KEY  AUTOINCREMENT",
        "name  VARCHAR(32)  NOT NULL",
        "description  TEXT  NULL",
        "picture  VARCHAR(512)  NULL",
    ],
    "Rating": [
        "rating_id  INTEGER  PRIMARY KEY  AUTOINCREMENT",
    ],
    "Question": [
        "question_id  INTEGER  PRIMARY KEY  AUTOINCREMENT",
        "snippet  VARCHAR(64)  NOT NULL",
        "message_body  TEXT  NOT NULL",
        "is_solved  INTEGER  NOT NULL  DEFAULT FALSE",
        "creation_date  DATETIME  NOT NULL  DEFAULT CURRENT_TIMESTAMP",
        "user_id  VARCHAR(16)  REFERENCES  User(user_id)",
        "topic_id  INTEGER  REFERENCES  Topic(topic_id)",
        "rating_id  INTEGER  REFERENCES  Rating(rating_id)  ON DELETE CASCADE",
    ],
    "Answer": [
        "answer_id  INTEGER  PRIMARY KEY  AUTOINCREMENT",
        "summary  VARCHAR(64)  NOT NULL",
        "message_body  TEXT  NOT NULL",
        "resource_links  TEXT  NULL",
        "creation_date  DATETIME  NOT NULL  DEFAULT CURRENT_TIMESTAMP",
        "user_id  VARCHAR(16)  REFERENCES  User(user_id)",
        "question_id  INTEGER  REFERENCES  Question(question_id)",
        "rating_id  INTEGER  REFERENCES  Rating(rating_id)  ON DELETE CASCADE",
    ],
    "Redaction": [
        "redaction_id  INTEGER  PRIMARY KEY  AUTOINCREMENT",
        "message_body  TEXT  NOT NULL",
        "creation_date  DATETIME  NOT NULL  DEFAULT CURRENT_TIMESTAMP",
        "user_id  VARCHAR(16)  REFERENCES  User(user_id)",
        "answer_id  INTEGER  REFERENCES  Answer(answer_id)",
    ],
    "Mark": [
        "mark_id  INTEGER  PRIMARY KEY  AUTOINCREMENT",
        "is_positive  INTEGER  NOT NULL  DEFAULT TRUE",
        "user_id  VARCHAR(16)  REFERENCES  User(user_id)",
        "rating_id  INTEGER  REFERENCES  Rating(rating_id)",
    ],
}
