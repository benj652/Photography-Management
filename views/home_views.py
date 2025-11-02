from flask import Blueprint, render_template
from flask_login import login_required, current_user


home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/')
#@login_required
def home():
    items = [
        {
            'id': 101,
            'name': 'Canon EOS R6',
            'quantity': 2,
            'tags': 'camera, full-frame',
            'location': 'Studio A',
            'expires': '—',
            'last_updated': '2025-10-10 14:32',
            'updated_by': 'benj@example.com',
        },
        {
            'id': 102,
            'name': 'Sigma 35mm f/1.4',
            'quantity': 1,
            'tags': 'lens, prime',
            'location': 'Equipment Locker',
            'expires': '—',
            'last_updated': '2025-09-21 09:05',
            'updated_by': 'alice@example.com',
        },
        {
            'id': 103,
            'name': 'SanDisk 128GB',
            'quantity': 10,
            'tags': 'memory, sd-card',
            'location': 'Accessories Bin',
            'expires': '2028-01-01',
            'last_updated': '2025-10-01 11:11',
            'updated_by': 'chris@example.com',
        },
        {
            'id': 104,
            'name': 'Light Stand',
            'quantity': 5,
            'tags': 'lighting, support',
            'location': 'Studio B',
            'expires': '—',
            'last_updated': '2025-08-12 16:40',
            'updated_by': 'dana@example.com',
        },
        {
            'id': 105,
            'name': 'Tripod',
            'quantity': 3,
            'tags': 'support, travel',
            'location': 'Field Kit',
            'expires': '—',
            'last_updated': '2025-07-30 10:00',
            'updated_by': 'erin@example.com',
        },
        
    ]

    print(f"Current user: {current_user}")
    return render_template('home.html', items=items)
