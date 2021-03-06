from flask_restful import Resource
from webargs.flaskparser import use_kwargs
from flask_jwt import jwt_required, current_identity
from sqlalchemy.exc import SQLAlchemyError

from bookmark_api import db
from bookmark_api.models import Bookmark

from bookmark_api.resources.schemas import (
    BookmarkListRequestSchema,
    BookmarkListResponseSchema,
    CreateBookmarkRequestSchema,
    EditBookmarkRequestSchema,
    BookmarkResponseSchema
)
from bookmark_api.authorization import (
    client_permission,
    ViewBookmarkPermission,
    EditBookmarkPermission,
    DeleteBookmarkPermission,
    requires_permission
)
from bookmark_api.resources.common import (
    assign_attributes,
    handle_delete
)
from bookmark_api import cache


class BookmarkListResource(Resource):

    @jwt_required()
    @use_kwargs(BookmarkListRequestSchema)
    def get(self, **kwargs):
        if current_identity.role.name == 'admin':
            bookmarks = Bookmark.query.order_by(Bookmark.user_id, Bookmark.created_at.desc()).paginate(**kwargs)
        else:
            bookmarks = Bookmark.query.filter_by(user_id=current_identity.id).\
               order_by(Bookmark.created_at.desc()).paginate(**kwargs)
        return BookmarkListResponseSchema().dump(bookmarks)


class BookmarkResource(Resource):

    @cache.cached()
    @jwt_required()
    @requires_permission(permission_class=ViewBookmarkPermission, field='bookmark_id')
    def get(self, bookmark_id):
        bookmark = Bookmark.query.get_or_404(bookmark_id)
        return BookmarkResponseSchema().dump(bookmark).data

    @jwt_required()
    @client_permission.require()
    @use_kwargs(CreateBookmarkRequestSchema)
    def post(self, **kwargs):
        try:
            params = kwargs['bookmark']
            params.update({"user_id": current_identity.id})
            bookmark = Bookmark(**params)
            db.session.add(bookmark)
            db.session.commit()
            return BookmarkResponseSchema().dump(bookmark).data
        except SQLAlchemyError as e:
            return {'errors': e.args}, 422

    @jwt_required()
    @requires_permission(permission_class=DeleteBookmarkPermission, field='bookmark_id')
    def delete(self, bookmark_id):
        return handle_delete(Bookmark, bookmark_id)

    @jwt_required()
    @requires_permission(permission_class=EditBookmarkPermission, field='bookmark_id')
    @use_kwargs(EditBookmarkRequestSchema)
    def put(self, bookmark_id, **kwargs):
        try:
            bookmark = Bookmark.query.filter_by(id=bookmark_id).first()
            assign_attributes(bookmark, kwargs['bookmark'])
            db.session.commit()
            return None, 204
        except SQLAlchemyError as e:
            return {'errors': e.args}, 422
