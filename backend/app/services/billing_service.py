from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy import select, func
from backend.app.models.generated_review import GeneratedPositiveReview
from sqlalchemy.orm import Session
from backend.app.models.business import Business
from backend.app.models.subscription import Subscription, BillingPayment
from backend.app.schemas.billing import PLANS

class BillingService:
    @staticmethod
    def subscription(db: Session, business_id: int) -> Subscription:
        sub = db.scalar(select(Subscription).where(Subscription.business_id == business_id))
        if sub is None:
            now=datetime.now(timezone.utc).replace(tzinfo=None)
            sub=Subscription(business_id=business_id, plan='STARTER', status='TRIALING', provider='MOCK', trial_ends_at=now+timedelta(days=14), current_period_start=now, current_period_end=now+timedelta(days=14))
            db.add(sub); db.commit(); db.refresh(sub)
        return sub
    @staticmethod
    def within_usage_limit(db: Session, business_id: int) -> bool:
        sub=BillingService.subscription(db,business_id)
        start=datetime.now(timezone.utc).replace(day=1,hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
        used=int(db.scalar(select(func.count(GeneratedPositiveReview.id)).where(GeneratedPositiveReview.business_id==business_id, GeneratedPositiveReview.created_at>=start)) or 0)
        return used < PLANS.get(sub.plan, PLANS['STARTER'])['monthly_review_limit']

    @staticmethod
    def checkout(db: Session, business_id: int, plan: str):
        if plan not in PLANS: raise ValueError('Invalid plan')
        amount=PLANS[plan]['price_paise']; receipt=f'RA-{uuid.uuid4().hex[:16].upper()}'
        payment=BillingPayment(business_id=business_id,plan=plan,amount_paise=amount,currency='INR',status='CREATED',provider='MOCK',provider_payment_id=None,receipt_reference=receipt)
        db.add(payment); db.commit(); db.refresh(payment)
        return payment, f'mock_order_{payment.id}_{uuid.uuid4().hex[:8]}'
    @staticmethod
    def confirm(db: Session, payment_id: int, success: bool):
        payment=db.get(BillingPayment,payment_id)
        if not payment: raise ValueError('Payment not found')
        if payment.status not in {'CREATED','FAILED'}: return payment
        payment.status='PAID' if success else 'FAILED'
        if success:
            sub=BillingService.subscription(db,payment.business_id); now=datetime.now(timezone.utc).replace(tzinfo=None)
            sub.plan=payment.plan; sub.status='ACTIVE'; sub.current_period_start=now; sub.current_period_end=now+timedelta(days=30); sub.cancel_at_period_end=False
            payment.provider_payment_id=f'mock_payment_{payment.id}'
        db.commit(); db.refresh(payment); return payment
