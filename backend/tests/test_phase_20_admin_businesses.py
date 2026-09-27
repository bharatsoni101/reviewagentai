from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.business import Business
from backend.app.models.fallback_review_comment import FallbackReviewComment
from backend.app.core.security import hash_password

def auth(client, email, password):
    r=client.post('/api/v1/auth/login',json={'email':email,'password':password}); assert r.status_code==200,r.text
    return {'Authorization':'Bearer '+r.json()['access_token']}

def test_admin_can_list_businesses_and_owners():
    with TestClient(app) as client:
        headers=auth(client,'admin@reviewagentai.local','Admin@12345')
        r=client.get('/api/v1/admin/businesses',headers=headers)
        assert r.status_code==200
        data=r.json(); assert 'businesses' in data and 'owners' in data
        assert isinstance(data['businesses'],list) and isinstance(data['owners'],list)

def test_business_owner_cannot_access_admin_businesses():
    with TestClient(app) as client:
        headers=auth(client,'owner@reviewagentai.local','Owner@12345')
        assert client.get('/api/v1/admin/businesses',headers=headers).status_code==403

def test_admin_can_create_update_and_toggle_business():
    with TestClient(app) as client:
        headers=auth(client,'admin@reviewagentai.local','Admin@12345')
        unique_email='phase20-owner-test@reviewagentai.local'
        test_slug='phase20-test-business'
        with SessionLocal() as db:
            existing_business=db.query(Business).filter_by(slug=test_slug).first()
            if existing_business:
                db.delete(existing_business)
                db.commit()
            existing=db.query(User).filter_by(email=unique_email).first()
            if existing:
                db.delete(existing)
                db.commit()
        payload={'slug':test_slug,'name':'Phase 20 Demo','description':'Admin-created business','category':'Demo','google_review_pc_url':'https://example.com/pc','google_review_mob_url':'https://example.com/mobile','status':'ACTIVE','prefer_ai_comments':False,'brand_primary_color':'#123456','brand_secondary_color':'#654321','nfc_enabled':False,'qr_enabled':True,'customer_settings':{'show_welcome':True},'social_links':[{'platform':'WEBSITE','url':'https://example.com','display_order':1,'enabled':True}], 'owner_full_name':'Phase 20 Owner','owner_email':unique_email,'owner_password':'Phase20@12345'}
        created=client.post('/api/v1/admin/businesses',json=payload,headers=headers); assert created.status_code==201,created.text
        bid=created.json()['id']; assert created.json()['plan']=='STARTER'
        assert created.json()['owner_name']=='Phase 20 Owner' and created.json()['owner_email']==unique_email
        with SessionLocal() as db:
            created_owner=db.query(User).filter_by(email=unique_email).first()
            assert created_owner is not None and created_owner.business_id==bid and created_owner.role=='BUSINESS_OWNER'
            fallback_comments=db.query(FallbackReviewComment).filter_by(business_id=bid, enabled=True).all()
            assert len(fallback_comments) == 6
            assert {row.rating for row in fallback_comments} == {4, 5}
        owner_login=client.post('/api/v1/auth/login',json={'email':unique_email,'password':'Phase20@12345'})
        assert owner_login.status_code==200, owner_login.text
        assert owner_login.json()['user']['business_id']==bid
        update=dict(payload); update.update({'name':'Phase 20 Updated','owner_id':created.json()['owner_id'],'status':'INACTIVE'})
        update.pop('owner_full_name',None); update.pop('owner_email',None); update.pop('owner_password',None)
        updated=client.put(f'/api/v1/admin/businesses/{bid}',json=update,headers=headers); assert updated.status_code==200,updated.text
        assert updated.json()['name']=='Phase 20 Updated' and updated.json()['owner_id']==created.json()['owner_id']
        toggled=client.patch(f'/api/v1/admin/businesses/{bid}/status?active=true',headers=headers); assert toggled.status_code==200, toggled.text
        assert toggled.json()['status']=='ACTIVE'
