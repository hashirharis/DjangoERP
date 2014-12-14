from django.db import models
from django.db.models.query import QuerySet
from django.db.models import Q

class GenericObjectManager(models.Manager):
    def get_query_set(self):
        return self.model.queryset(self.model)

#This is used my the Store Level Object Model to filter models based on their ownerships. Models can be products, Brands, Tags etc. Really anything that inherits from the StoreLevelObject model
class StoreLevelObjectQueryset(QuerySet):
    def filterReadAll(self, store):
        return self.filter(Q(group=store.group) | Q(group__parent=store.group), isShared=True) | self.filter(store=store, group=store.group, isShared=False)

    def filterReadLocal(self, store):
        return self.filter(store=store, group=store.group, isShared=False)

    def filterReadGlobal(self, store):
        return self.filter(Q(group=store.group) | Q(group__parent=store.group), isShared=True)

    def filterUpdateAll(self, store):
        return self.filter(Q(group=store.group) | Q(group__parent=store.group), isShared=True, store=store) | self.filter(store=store, group=store.group, isShared=False)