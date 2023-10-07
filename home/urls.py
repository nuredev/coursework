from src.shortcuts import Path
from .views import *

urlpatterns = [
    Path(feed).link(""),
    Path(profile).link(),
    Path(browse).link(),
    Path(browse_topic).link("browse/<str:index>"),
    Path(browse_question).link("browse/question/<int:question_id>"),
    Path(browse_question_close).link("browse/question/<int:question_id>/close"),
    Path(browse_question_reopen).link("browse/question/<int:question_id>/reopen"),
    Path(manage).link(),
    Path(user).link("user/<str:user_id>"),
    Path(search).link("search"),
    Path(statistics).link("statistics"),
    Path(redact).link("redact/<int:question_id>/<int:answer_id>"),
]
