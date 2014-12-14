import sys
sys.path.extend(['C:\\Users\\Yussuf\\Documents\\GitHub\\pybr'])

from importfunc.querysets import Model, Category
models = Model()
mappedmodels = Model().djangoMap()
iddcategories = Category().assignAI()
categories = models.unique('CLASSID')
errors = 0

for category in categories:
    categorymodels = models.filter(CLASSID=category)
    initwarrant = []
    varyingModels = []

    for model in categorymodels:
        if model.get('EXTWARTYPE') == "":
            continue
        if len(initwarrant) == 0:
            initwarrant.append(model.get('EXTWARTYPE'))
        else:
            if mappedmodels.get(model=model.get('MODEL')) is not None:
                if model.get('EXTWARTYPE') not in initwarrant:
                    initwarrant.append(model.get('EXTWARTYPE'))
                    varyingModels.append(model.get('MODEL'))
    if len(initwarrant) > 1:
        print "%d varying warranties in category %s \n %s \n %s" % (len(initwarrant), iddcategories.get(CLASSID=model.get('CLASSID')).get('CATEGORY'), str(initwarrant), str(varyingModels))