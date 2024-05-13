from flask import Flask, request, jsonify
from flask.views import MethodView
from models import Announcement, Session
from sqlalchemy.exc import IntegrityError

announcement_app = Flask('announcement')
@announcement_app.before_request
def before_request():
    session = Session()
    request.session = session
@announcement_app.after_request
def after_request(response: Flask.response_class):
    request.session.close()
    return response


class HttpError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
@announcement_app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({'error': str(error.message)})
    response.status_code = error.status_code
    return response

def get_announcement_by_id(announcement_id: int):
    announcement = request.session.query(Announcement).get(announcement_id)
    if announcement is None:
        raise HttpError(404, 'Announcement not found')
    return announcement

def add_announcement(announcement: Announcement):
    try:
        request.session.add(announcement)
        request.session.commit()
    except IntegrityError:
        raise HttpError(409, 'Announcement already exists')

class AnnouncementView(MethodView):
    def get(self, announcement_id: int):
        announcement_obj = get_announcement_by_id(announcement_id)
        return jsonify(announcement_obj.dict)

    def post(self):
        announcement_data = request.json
        new_announcement = Announcement(**announcement_data)
        add_announcement(new_announcement)
        return jsonify(new_announcement.dict), 201

    def delete(self, announcement_id: int):
        announcement_obj = get_announcement_by_id(announcement_id)
        request.session.delete(announcement_obj)
        request.session.commit()
        return jsonify({'status': 'deleted'})


    def patch(self, announcement_id: int):
        announcement_data = request.json
        announcement_obj = get_announcement_by_id(announcement_id)
        for field, value in announcement_data.items():
            setattr(announcement_obj, field, value)
        request.session.commit()
        return jsonify(announcement_obj.dict)

announcement_view = AnnouncementView.as_view('announcement_view')

announcement_app.add_url_rule('/announcement/<int:announcement_id>', view_func=announcement_view,
                               methods=['GET', 'DELETE', 'PATCH'])

announcement_app.add_url_rule('/announcement', view_func=announcement_view,
                               methods=['POST'])

if __name__ == '__main__':
    announcement_app.run()
