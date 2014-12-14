from django.core.management.base import BaseCommand
from users.models import Store, Staff
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates Users for the all the stores with username as store name and password as code + 123'
    requires_model_validation = True

    def handle(self, *args, **options):
        stores = Store.objects.all()
        #create store users
        for store in stores:
            user = User.objects.create_user(username=store.code, password=store.code+"123")
            store.user = user
            store.save()
            managerMember = Staff(
                store=store,
                name='%s manager' % store.code,
                initials=store.code[:4],
                username=store.code,
                password=store.code+'123',
                privelegeLevel=3
            )
            managerMember.save()