from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Machine, Revision, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden


@api.route('/revisions/')
def get_revisions():
    page = request.args.get('page', 1, type=int)
    pagination = Revision.query.paginate(
        page, per_page=current_app.config['RIVALROCKETS_REVISIONS_PER_PAGE'],
        error_out=False)
    revisions = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_revisions', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_revisions', page=page+1, _external=True)
    return jsonify({
        'revisions': [revision.to_json() for revision in revisions],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/revisions/<int:id>')
def get_revision(id):
    revision = Revision.query.get_or_404(id)
    return jsonify(revision.to_json())


@api.route('/machines/<int:id>/revisions/')
def get_machine_revisions(id):
    machine = Machine.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = machine.revisions.order_by(Revision.timestamp.asc()).paginate(
        page, per_page=current_app.config['RIVALROCKETS_REVISIONS_PER_PAGE'],
        error_out=False)
    revisions = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_revisions', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_revisions', page=page+1, _external=True)
    return jsonify({
        'machines': [revision.to_json() for revision in revisions],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/machines/<int:id>/revisions/', methods=['POST'])
@permission_required(Permission.CREATE_MACHINE_DATA)
def new_machine_revision(id):
    machine = Machine.query.get_or_404(id)
    revision = Revision.from_json(request.json)
    revision.author = g.current_user
    revision.machine = machine
    db.session.add(revision)
    db.session.commit()
    return jsonify(revision.to_json()), 201, \
           {'Location': url_for('api.get_revision', id=revision.id, _external=True)}


@api.route('/revisions/<int:id>', methods=['PUT'])
@permission_required(Permission.CREATE_MACHINE_DATA)
def edit_revision(id):
    revision = Revision.query.get_or_404(id)
    if g.current_user != revision.author and \
            not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    revision.system_name = request.json.get('system_name', revision.system_name)
    revision.system_notes = request.json.get('system_notes', revision.system_notes)
    db.session.add(revision)
    return jsonify(revision.to_json())

