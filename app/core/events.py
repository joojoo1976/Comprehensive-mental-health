import logging
from sqlalchemy import event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.attributes import get_history

from app import crud
from app.core.cache import cache_service
from app.models.user import User as UserModel
from app.models.auth import Role as RoleModel

logger = logging.getLogger(__name__)

def setup_cache_invalidation_listeners(SessionLocal: sessionmaker):
    """
    إعداد مستمعي الأحداث لإبطال ذاكرة التخزين المؤقت للمستخدم تلقائيًا.
    """

    @event.listens_for(SessionLocal, "after_commit")
    def receive_after_commit(session: Session):
        """
        يتم استدعاء هذا المستمع بعد كل عملية commit ناجحة على الجلسة.
        """
        user_ids_to_invalidate = set()

        # التكرار على الكائنات التي تم تعديلها في الجلسة
        for obj in session.dirty:
            # الحالة 1: تم تغيير دور المستخدم مباشرة (user.role_id)
            if isinstance(obj, UserModel):
                history = get_history(obj, 'role_id')
                # إذا كان هناك قيمة قديمة وقيمة جديدة وهما مختلفتان
                if history.has_changes():
                    logger.debug(f"User role changed for user ID {obj.id}. Invalidating cache.")
                    user_ids_to_invalidate.add(obj.id)

            # الحالة 2: تم تغيير صلاحيات دور معين (role.permissions)
            if isinstance(obj, RoleModel):
                history = get_history(obj, 'permissions')
                if history.has_changes():
                    logger.debug(f"Permissions changed for role '{obj.name}' (ID: {obj.id}). Finding affected users.")
                    # نحتاج إلى العثور على جميع المستخدمين الذين لديهم هذا الدور وإبطال ذاكرتهم المؤقتة
                    # ملاحظة: هذا يتطلب استعلامًا إضافيًا، لكنه ضروري ويحدث فقط عند تغيير الأدوار.
                    # نستخدم جلسة جديدة هنا لأن الجلسة الحالية قد تم إغلاقها بعد الـ commit.
                    from app.core.database import SessionLocal as NewSession
                    with NewSession() as db_for_query:
                        users_with_role = crud.user.get_multi_by_role(db_for_query, role_id=obj.id)
                        for user in users_with_role:
                            user_ids_to_invalidate.add(user.id)

        if user_ids_to_invalidate:
            logger.info(f"Invalidating cache for user IDs: {user_ids_to_invalidate}")
            for user_id in user_ids_to_invalidate:
                cache_service.invalidate_user(user_id)

    logger.info("SQLAlchemy event listeners for cache invalidation have been set up.")