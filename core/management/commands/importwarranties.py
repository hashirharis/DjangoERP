#local imports
from core.models import *
from users.models import *
#local utility imports
from importfunc import querysets
#django imports
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Adds all the warranties from the csv dump of the Lumley Warranty list.'
    requires_model_validation = True

    def handle(self, *args, **options):
        warranties = querysets.Warranty().keyMap()
        brand = Brand.objects.get(brand="NARTA")
        store = Store.objects.get(code="HO")
        group = StoreGroup.objects.get(pk=1)
        #create the warranties
        for item in warranties:
            category = ProductCategory.objects.get(parentCategory__name="Extended Warranties", name=item['category'])
            warranty = Warranty()
            warranty.brand = brand
            warranty.category = category
            warranty.costPrice = querysets.Queryset.parse_float_or_zero(item.get('costPrice'))
            warranty.tradePrice = querysets.Queryset.parse_float_or_zero(item.get('costPrice'))
            warranty.spanNet = querysets.Queryset.parse_float_or_zero(item.get('costPrice'))
            warranty.startValue = querysets.Queryset.parse_float_or_zero(item.get('startValue'))
            warranty.endValue = querysets.Queryset.parse_float_or_zero(item.get('endValue'))
            warranty.goPrice = querysets.Queryset.parse_float_or_zero(item.get('goPrice'))
            #item['description'] = self.parse_string_silent(item.get('description'))
            warranty.model = querysets.Queryset.parse_string_silent(item.get('model'))
            #item['manWarranty'] = self.parse_string_silent(item.get('manWarranty'))
            #item['comments'] = self.parse_string_silent(item.get('comments'))
            warranty.isShared = True
            warranty.store = store
            warranty.group = group
            warranty.save()
        #create the warranty category links
        extWarranty_links = querysets.Queryset('Warranty_Categories')
        for link in extWarranty_links:
            category = ProductCategory.objects.all().get(name=link.get('CATEGORY',''), depth=link.get('DEPTH'))
            warrantyCategory = ProductCategory.objects.get(parentCategory__name="Extended Warranties", name=link.get('WARRANTY', ''))
            category.extWarrantyTypes.add(warrantyCategory)