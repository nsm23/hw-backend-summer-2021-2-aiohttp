from aiohttp_apispec import request_schema, response_schema, querystring_schema
from aiohttp_session import get_session
from aiohttp.web_exceptions import (HTTPConflict,
                                    HTTPNotFound,
                                    HTTPBadRequest,
                                    HTTPUnauthorized)
from app.quiz.schemes import (ThemeSchema,
                              ThemeRequestSchema,
                              QuestionSchema,
                              QuestionResponseScheme,
                              QuestionIdScheme,
                              ListQuestionSchema)
from app.web.app import View
from app.web.utils import json_response


# TODO: добавить проверку авторизации для этого View
class ThemeAddView(View):
    # TODO: добавить валидацию с помощью aiohttp-apispec и marshmallow-схем
    @request_schema(ThemeRequestSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        session = await get_session(self.request)
        if not session:
            raise HTTPUnauthorized

        data = self.request["data"]
        theme = await self.store.quizzes.get_theme_by_title(data["title"])
        if theme:
            raise HTTPConflict
        title = (await self.request.json())["title"]
        # TODO: заменить на self.data["title"] после внедрения валидации
        # TODO: проверять, что не существует темы с таким же именем, отдавать 409 если существует
        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(View):
    async def get(self):
        session = await get_session(self.request)
        if not session:
            raise HTTPUnauthorized
        themes = await self.store.quizzes.list_themes()
        raw_themes = [ThemeSchema().dump(theme) for theme in themes]
        return json_response(data={"themes": raw_themes})


class QuestionAddView(View):
    @request_schema(QuestionSchema)
    async def post(self):
        session = await get_session(self.request)
        if not session:
            raise HTTPUnauthorized

        data = self.request["data"]
        if len(data["answers"]) == 1:
            raise HTTPBadRequest
        count = 0
        for answer in data["answers"]:
            if answer["is_correct"]:
                count += 1
        if count != 1:
            raise HTTPBadRequest

        theme = await self.store.quizzes.get_theme_by_id(data["title"])
        if not theme:
            raise HTTPNotFound

        question = await self.store.quizzes.create_question(
            title=data["title"],
            theme_id=data["theme_id"],
            answers=data["answers"]
        )
        return json_response(data=QuestionResponseScheme().dump(question))


class QuestionListView(View):
    @querystring_schema(QuestionIdScheme)
    @response_schema(ListQuestionSchema)
    async def get(self):
        session = await get_session(self.request)
        if not session:
            raise HTTPUnauthorized

        theme_id = None
        if self.request.query:
            theme_id = self.request.query["theme_id"]
        questions = await self.store.quizzes.list_questions(theme_id=theme_id)
        questions_raw = [QuestionResponseScheme().dump(question) for question in questions]
        return json_response(data={"questions": questions_raw})
