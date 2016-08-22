from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Machine


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/<int:id>/machines/')
def get_user_machines(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.machines.order_by(Machine.timestamp.desc()).paginate(
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
