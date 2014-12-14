from django.core.urlresolvers import reverse
from lib.queries import get_query
from django.core.paginator import Paginator, EmptyPage

def getGenericCrudURLS(entity, c=False, r=False, u=False, d=False, args=(1,), prepend="core:",):
    returnDict = {}
    if c:
        returnDict['createURL'] = reverse("%screate%s" % (prepend, entity))
    if r:
        returnDict['viewURL'] = reverse("%sview%s" % (prepend, entity), args=args)
    if u:
        returnDict['updateURL'] = reverse("%supdate%s" % (prepend, entity), args=args)
    if d:
        returnDict['deleteURL'] = reverse("%sdelete%s" % (prepend, entity), args=args)
    return returnDict

def filterGenericSearchQuery(entities, fieldsToSearch, POST):
    p=1
    q=''

    if ('q' in POST) and (len(POST['q'].strip())>0):
        q = POST['q']
        #regular product fields search
        entry_query = get_query(q, fieldsToSearch)
        entities = entities.filter(entry_query)

    entities = entities.order_by('-id')[:300]

    paginator = Paginator(entities, 30)
    if ('page' in POST)  and (len(POST['page'].strip())>0):
        p = int(POST['page'])

    try:
        entities = paginator.page(p)
    except EmptyPage:
        entities = paginator.page(paginator.num_pages)

    return {
        'entities': entities,
        'p':p,
        'q':q,
    }