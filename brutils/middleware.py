from users.models import Store, Staff
from brutils.shortcuts import get_or_none

class StoreMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            request.store = get_or_none(Store, user__pk=request.user.id)
            request.staff = get_or_none(Staff, pk=request.session.get('staff_id', 0))