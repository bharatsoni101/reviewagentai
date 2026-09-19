from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.database import SessionLocal
from backend.app.models.business import Business
from backend.app.models.user import User
from backend.app.core.security import hash_password


def auth(client, email, password):
    r = client.post('/api/v1/auth/login', json={'email': email, 'password': password})
    assert r.status_code == 200
    return {'Authorization': f"Bearer {r.json()['access_token']}"}


def test_admin_can_list_businesses_and_owners():
    with TestClient(app) as client:
        headers = auth(client, 'admin@reviewagentai.local', 'Admin@12345')
        r = client.get('/api/v1/admin/businesses', headers=headers)
        assert r.status_code == 200
        assert r.json()['total'] >= 2
        owners = client.get('/api/v1/admin/businesses/owners', headers=headers)
        assert owners.status_code == 200
        assert any(x['email'] == 'owner@reviewagentai.local' for x in owners.json())


def test_business_owner_cannot_access_admin_businesses():
    with TestClient(app) as client:
        headers = auth(client, 'owner@reviewagentai.local', 'Owner@12345')
        assert client.get('/api/v1/admin/businesses', headers=headers).status_code == 403
        assert client.get('/api/v1/admin/businesses/owners', headers=headers).status_code == 403


def test_admin_can_create_update_and_toggle_business():
    with TestClient(app) as client:
        headers = auth(client, 'admin@reviewagentai.local', 'Admin@12345')
        unique_email = 'phase20-owner-test@reviewagentai.local'
        with SessionLocal() as db:
            existing = db.query(User).filter_by(email=unique_email).first()
            if existing: db.delete(existing); db.commit()
            temp_owner = User(email=unique_email, password_hash=hash_password('Phase20@12345'), full_name='Phase 20 Owner', role='BUSINESS_OWNER', business_id=None, is_active=True)
            db.add(temp_owner); db.commit(); db.refresh(temp_owner)
            owner_id = temp_owner.id
        owner = {'id': owner_id}
        # Do not steal the demo owner's existing assignment; create without owner first.
        payload = {
            'slug': 'phase20-test-business', 'name': 'Phase 20 Demo', 'description': 'Admin-created business',
            'category': 'Demo', 'google_review_pc_url': 'https://example.com/pc',
            'google_review_mob_url': 'https://example.com/mobile', 'status': 'ACTIVE',
            'prefer_ai_comments': False, 'brand_primary_color': '#123456', 'brand_secondary_color': '#654321',
            'nfc_enabled': False, 'qr_enabled': True, 'customer_settings': {'show_welcome': True},
            'social_links': [{'platform':'WEBSITE','url':'https://example.com','display_order':1,'enabled':True}],
        }
        created = client.post('/api/v1/admin/businesses', json=payload, headers=headers)
        assert created.status_code == 201, created.text
        b = created.json(); bid = b['id']
        assert b['name'] == 'Phase 20 Demo' and b['nfc_enabled'] is False
        updated = client.put(f'/api/v1/admin/businesses/{bid}', json={
            'name':'Phase 20 Updated','slug':'phase20-test-business-updated','owner_user_id': owner['id'],
            'status':'INACTIVE','brand_primary_color':'#abcdef','customer_settings':{'show_welcome':False},
        }, headers=headers)
        assert updated.status_code == 200, updated.text
        data = updated.json()
        assert data['name'] == 'Phase 20 Updated' and data['owner_user_id'] == owner['id'] and data['status'] == 'INACTIVE'
        toggled = client.patch(f'/api/v1/admin/businesses/{bid}/status?new_status=ACTIVE', headers=headers)
        assert toggled.status_code == 200
        assert toggled.json()['status'] == 'ACTIVE'
        with SessionLocal() as db:
            demo = db.get(Business, bid)
            assert demo is not None and demo.slug == 'phase20-test-business-updated'
            linked = db.get(User, owner['id'])
            assert linked.business_id == bid
            linked.business_id = None
            db.delete(demo)
            db.delete(linked)
            db.commit()
