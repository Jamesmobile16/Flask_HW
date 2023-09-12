import requests
from flask import Flask, jsonify, request
from flask.views import MethodView
from models import Session, Adv
from schema import CreateAdv, PatchAdv, VALIDATION_CLASS
from pydantic import ValidationError

app = Flask('app')


class HttpError(Exception):  # Класс для обработки ошибок
    def __init__(self, status_code: int, message: dict | list | str):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def http_error_handler(error: HttpError):
    error_message = {
        'status': 'error',
        'description': error.message
    }
    response = jsonify(error_message)
    response.status_code = error.status_code
    return response


def validation_json(json_data: dict, validation_model: VALIDATION_CLASS):
    try:
        model_object = validation_model(**json_data)
        model_object_dict = model_object.dict(exclude_none=True)
    except ValidationError as err:
        raise HttpError(400, message=err.errors())
    return model_object_dict


def get_adv(session: Session, adv_id: int):
    adv = session.get(Adv, adv_id)
    if adv is None:
        raise HttpError(404, message="adv doesn't exist")
    return adv


class AdvView(MethodView):

    def get(self, adv_id: int):
        with Session() as session:
            adv = get_adv(session, adv_id)
            return jsonify({'id': adv_id,
                            'title': adv.title,
                            'description': adv.description,
                            'created_at': adv.created_at.isoformat(),
                            'author': adv.author
                            })

    def post(self):
        json_data = validation_json(request.json, CreateAdv)
        with Session() as session:
            adv = Adv(**json_data)
            session.add(adv)
            session.commit()
            return jsonify({'id': adv.id})

    def patch(self, adv_id: int):
        json_data = validation_json(request.json, PatchAdv)
        with Session() as session:
            adv = get_adv(session, adv_id)
            for field, value in json_data.items():
                setattr(adv, field, value)
            session.add(adv)
            session.commit()
            return jsonify({'id': adv_id,
                            'title': adv.title,
                            'description': adv.description,
                            'created_at': adv.created_at.isoformat(),
                            'author': adv.author})

    def delete(self, adv_id: int):
        with Session() as session:
            adv = get_adv(session, adv_id)
            session.delete(adv)
            session.commit()
            return jsonify({'status': 'completed'})


app.add_url_rule(
    '/adv/<int:adv_id>',
    view_func=AdvView.as_view('with_adv_id'),
    methods=['GET', 'PATCH', 'DELETE']
)

app.add_url_rule(
    '/adv/',
    view_func=AdvView.as_view('create_adv'),
    methods=['POST']
)

if __name__ == '__main__':
    app.run()