from django.db.models.signals import post_save
from django.db.models import Q
from core.models import Product, Deal, ClassVendorBonus, ProductTag

def ModelDealChanged(sender, **kwargs):
    deal = kwargs['instance']
    type = sender.__name__
    if type == "ClassVendorBonus":
        tag = ProductTag.objects.get(tag__exact="Vendor Bonus", type__exact="Deal")
        for product in Product.objects.filter(Q(category__parentCategory=deal.type) | Q(category=deal.type) | Q(category__parentCategory__parentCategory=deal.type) | Q(category__parentCategory__parentCategory__parentCategory=deal.type), brand=deal.brand):
            product.updateCurrentSPANNet()
            if deal.active:
                product.tags.add(tag)
            else:
                product.tags.remove(tag)
    else:
        deal.product.updateCurrentSPANNet()
        type = deal.type
        types = {
            'OI': 'Model Discount',
            'MB': 'Model Bonus',
            'PB': 'Percent Bonus',
            'ST': 'Sell Through'
        }
        tag = ProductTag.objects.get(tag__exact=types[type], type__exact="Deal")
        if deal.active:
            deal.product.tags.add(tag)
        else:
            deal.product.tags.remove(tag)

post_save.connect(ModelDealChanged, sender=Deal)
post_save.connect(ModelDealChanged, sender=ClassVendorBonus)