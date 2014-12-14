from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from functools import wraps

def access_required(module):
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            if request.staff is None:
                return HttpResponseRedirect(reverse('core:home'))
            staff = request.staff
            if module == 'admin':
                if staff.privelegeLevel >= 3:
                    return func(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect(reverse('core:home'))
            elif module == 'stock':
                if staff.privelegeLevel >= 2:
                    return func(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect(reverse('core:home'))
            elif module == 'sale':
                if staff.privelegeLevel >= 1:
                    return func(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect(reverse('core:home'))
        return wraps(func)(inner_decorator)
    return decorator