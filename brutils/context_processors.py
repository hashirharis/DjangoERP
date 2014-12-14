from users.models import Store, Staff
import json

def storevars(request):
    if request.user.is_authenticated():
        store = request.store
        staff = Staff.objects.get(pk=request.session['staff_id']) if request.session.get('staff_id') else None
        return {
            'store': store,
            'staffPerms': json.dumps([{
                'name': x.username,
                'password': x.password,
                'privelegeLevel': x.privelegeLevel,
            } for x in Staff.objects.filter(store=store)]),
            'storeSettings': store.user.profile,
            'staffMember': staff
        }
    return {}