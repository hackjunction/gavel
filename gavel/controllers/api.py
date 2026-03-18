from gavel import app
from gavel.models import *
import gavel.utils as utils
from flask import Response, request, url_for
import json

@app.route('/api/items.csv')
@app.route('/api/projects.csv')
@utils.requires_auth
def item_dump():
    items = Item.query.order_by(desc(Item.mu)).all()
    data = [['Mu', 'Sigma Squared', 'Name', 'Location', 'Description', 'Active']]
    data += [[
        str(item.mu),
        str(item.sigma_sq),
        item.name,
        item.location,
        item.description,
        item.active
    ] for item in items]
    return Response(utils.data_to_csv_string(data), mimetype='text/csv')

@app.route('/api/annotators.csv')
@app.route('/api/judges.csv')
@utils.requires_auth
def annotator_dump():
    annotators = Annotator.query.all()
    data = [['Name', 'Email', 'Description', 'Secret']]
    data += [[
        str(a.name),
        a.email,
        a.description,
        a.secret
    ] for a in annotators]
    return Response(utils.data_to_csv_string(data), mimetype='text/csv')

@app.route('/api/decisions.csv')
@utils.requires_auth
def decisions_dump():
    decisions = Decision.query.all()
    data = [['Annotator ID', 'Winner ID', 'Loser ID', 'Time']]
    data += [[
        str(d.annotator.id),
        str(d.winner.id),
        str(d.loser.id),
        str(d.time)
    ] for d in decisions]
    return Response(utils.data_to_csv_string(data), mimetype='text/csv')

@app.route('/api/items', methods=['POST'])
@utils.protected_endpoint
def item_import():
    data = request.get_json()
    if not isinstance(data, list):
        return Response(json.dumps({'error': 'Expected a JSON array'}), 400, mimetype='application/json')
    for i, row in enumerate(data):
        for field in ('name', 'location', 'description'):
            if not row.get(field):
                return Response(json.dumps({'error': 'Row %d missing field: %s' % (i + 1, field)}), 400, mimetype='application/json')
    created = []
    def tx():
        for row in data:
            item = Item(row['name'], row['location'], row['description'])
            db.session.add(item)
            created.append(item)
        db.session.commit()
    with_retries(tx)
    return Response(json.dumps([{'id': i.id, 'name': i.name} for i in created]), 201, mimetype='application/json')


@app.route('/api/annotators', methods=['POST'])
@utils.protected_endpoint
def annotator_import():
    data = request.get_json()
    if not isinstance(data, list):
        return Response(json.dumps({'error': 'Expected a JSON array'}), 400, mimetype='application/json')
    for i, row in enumerate(data):
        for field in ('name', 'email', 'description'):
            if not row.get(field):
                return Response(json.dumps({'error': 'Row %d missing field: %s' % (i + 1, field)}), 400, mimetype='application/json')
    created = []
    def tx():
        for row in data:
            annotator = Annotator(row['name'], row['email'], row['description'])
            db.session.add(annotator)
            created.append(annotator)
        db.session.commit()
    with_retries(tx)
    return Response(json.dumps([{
        'id': a.id,
        'name': a.name,
        'email': a.email,
        'login_link': url_for('login', secret=a.secret, _external=True)
    } for a in created]), 201, mimetype='application/json')


# Authorization Basic username:password
@app.route('/api/users-link')
@utils.protected_endpoint
def users_link():
    response = json.dumps([
            {
                'link': url_for('login', secret=a.secret, _external=True),
                'email': a.email,
                'registration': a.description,
            } for a in Annotator.query.all()
        ])
    return Response(response, mimetype='application/json')
