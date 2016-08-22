from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Machine, Permission, Comment
from . import api
from .decorators import permission_required


@api.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['RIVALROCKETS_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1, _external=True)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())


@api.route('/machines/<int:id>/comments/')
def get_machine_comments(id):
    machine = Machine.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = machine.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['RIVALROCKETS_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1, _external=True)
    return jsonify({
        'machines': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/machines/<int:id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_machine_comment(id):
    machine = Machine.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.machine = machine
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, \
           {'Location': url_for('api.get_comment', id=comment.id,
                             _external=True)}
