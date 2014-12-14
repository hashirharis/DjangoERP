from stock.models import Claim, ClaimLine, StoreInventoryItem
from lib.jsonStringify.utility import encodeDecimal

def claimFromJson(data, staff):
    if data.get('id', 0) != 0:
        claim = Claim.objects.get(pk=data.get('id'))
    else:
        claim = Claim()
        claim.createdBy = staff
        claim.store = staff.store
    claim.status = data.get('status')
    claim.type = data.get('type')
    claim.code = Claim.generateDocReference(staff.store)
    claim.comments = data.get('comments')
    claim.save()
    for line in data.get('claimLines', []):
        try:
            dbline = ClaimLine.objects.get(inventoryItem__id=line.get('id'), claim=claim)
        except ClaimLine.DoesNotExist:
            inventoryItem = StoreInventoryItem.objects.get(pk=line.get('id'))
            dbline = ClaimLine(claim=claim, inventoryItem=inventoryItem)
        dbline.description = line.get('description')
        dbline.oldNetPrice = line.get('unitPrice', 0.00)
        dbline.newNetPrice = line.get('newUnitPrice', 0.00)
        dbline.amount = line.get('claimTotal', 0.00)
        dbline.save()
    return claim

def jsonFromClaim(claim):
    return {
        'id': claim.id,
        'status': claim.status,
        'store': claim.store.code,
        'storeid': claim.store.id,
        'type': claim.type,
        'comments': claim.comments,
        'claimLines': [
            {
                'id': x.inventoryItem.id,
                'description': x.description,
                'unitPrice': encodeDecimal(x.oldNetPrice),
                'newUnitPrice': encodeDecimal(x.newNetPrice)
            }
            for x in claim.claimline_set.all()
        ]
    }