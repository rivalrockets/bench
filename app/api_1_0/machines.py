from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Machine, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden


@api.route('/machines/')
def get_machines():
    page = request.args.get('page', 1, type=int)
    pagination = Machine.query.paginate(
        page, per_page=current_app.config['RIVALROCKETS_MACHINES_PER_PAGE'],
        error_out=False)
    machines = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_machines', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_machines', page=page+1, _external=True)
    return jsonify({
        'machines': [machine.to_json() for machine in machines],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/machines/<int:id>')
def get_machine(id):
    machine = Machine.query.get_or_404(id)
    return jsonify(machine.to_json())


@api.route('/machines/', methods=['POST'])
@permission_required(Permission.CREATE_MACHINE_DATA)
def new_machine():
    machine = Machine.from_json(request.json)
    machine.author = g.current_user
    db.session.add(machine)
    db.session.commit()
    return jsonify(machine.to_json()), 201, \
        {'Location': url_for('api.get_machine', id=machine.id, _external=True)}


@api.route('/machines/<int:id>', methods=['PUT'])
@permission_required(Permission.CREATE_MACHINE_DATA)
def edit_machine(id):
    machine = Machine.query.get_or_404(id)
    if g.current_user != machine.author_id and \
            not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    machine.system_name = request.json.get('system_name', machine.system_name)
    machine.system_notes = request.json.get('system_notes', machine.system_notes)
    db.session.add(machine)
    return jsonify(machine.to_json())

