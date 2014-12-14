(function( br, $, _, undefined ) {
	//public
 	br.collationModel = function(month) {
 		if (month==undefined) { //default model instance
            month = {
                //bulletin base
                id: 0, //other vars
                subject: '',
                startDate: undefined,
                endDate: undefined,
                archiveDate: undefined,
                tag: 'Collations',
                toStores: [],
                toGroups: [],
                content: '',
                sendSMS: false,
                sendEmail: false,
                sendSMSReminder: false,
                sendEmailReminder: false,
                //collation
                collationItems: [],
                collationItemsIndex: 0,
                orderMethod: 'Email',
                notes: '',
                deliveryMonths: [],
                deliveryMonthsIndex: 0,
                viewType: 'List',
                //currently selected collation item
                selectedCollationItemPrices: [],
                selectedCollationItemPricesIndex: 0,
                saveURL: ""
            }
        }
        var collationModel = br.baseModel(month);

        collationModel.getCollationItem = function(line) {
            var filter = {line:line};
            return this.getItem("collationItems",filter);
        };
        collationModel.loadCollationItem = function(item) {
            // this is used to add a product to the array
            //(mainly for the sanitation of the object returned from a modal or anything really)
            var collationItem = {
                "line" : this.collationItemsIndex, //index for non repeat logic
                "model": item.model,
                "prices": item.prices,
                "hidden": item.hidden,
                "deleted": item.deleted
            };
            this.addCollationItem(collationItem);
        };
        collationModel.addCollationItemFromModal = function(model) {
            // this is used to add a product to the array
            //(mainly for the sanitation of the object returned from a modal or anything really)
            if (model==null) {
                return
            }
            if (model=='') {
                alert("invalid model number entered");
                return
            }
            var collationItem = {
                "line" : this.collationItemsIndex, //index for non repeat logic
                "model": model,
                "prices": this.selectedCollationItemPrices.slice(),
                "hidden": false,
                "deleted": false
            };
            this.addCollationItem(collationItem);
        };
        collationModel.addCollationItem = function(collationItem) {
            this.addItem("collationItems",collationItem);
            this.collationItemsIndex++;
        };
        collationModel.removeCollationItem = function(line) {
            var filter = {line:line};
            if (this.id==0) { //creating collation
                this.deleteItem("collationItems",filter);
            }
            else { //updating, there may be existing orders so just set it to deleted
                var newattributes = {
                    "deleted": true
                };
                this.updateItemValues("collationItems",filter,newattributes);
            }
        };
        collationModel.hideUnhideCollationItem = function(line) {
            var filter = {line:line};
            var collationItem = this.getCollationItem(line);
            var newattributes = {
                "hidden": !collationItem.hidden
            };
            this.updateItemValues("collationItems",filter,newattributes);
        };
        collationModel.updateCollationItem = function(line,model) {
            var filter = {line:line};
            var newattributes = {
                "model": model,
                "prices": this.selectedCollationItemPrices.slice()
            };
            this.updateItemValues("collationItems",filter,newattributes);
        };
        //general total,get,update,delete,add and addFrom(x)
        collationModel.getDeliveryMonth = function(line) {
            var filter = {line:line};
            return this.getItem("deliveryMonths",filter);
        };
        collationModel.loadDeliveryMonth = function(month) {
            // this is used to add a product to the array
            //(mainly for the sanitation of the object returned from a modal or anything really)
            var deliveryMonth = {
                "line" : this.deliveryMonthsIndex, //index for non repeat logic
                "month": month.month,
                "hidden": month.hidden,
                "deleted": month.deleted
            };
            this.addDeliveryMonth(deliveryMonth);
        };
        collationModel.addDeliveryMonthFromPrompt = function(month) {
            // this is used to add a product to the array
            //(mainly for the sanitation of the object returned from a modal or anything really)
            if (month==null) {
                return
            }
            if (month=='') {
                alert("Invalid month entered");
                return
            }
            var deliveryMonth = {
                "line" : this.deliveryMonthsIndex, //index for non repeat logic
                "month": month,
                "hidden": false,
                "deleted": false
            };
            this.addDeliveryMonth(deliveryMonth);
        };
        collationModel.addDeliveryMonth = function(deliveryMonth) {
            this.addItem("deliveryMonths",deliveryMonth);
            this.deliveryMonthsIndex++;
        };
        collationModel.removeDeliveryMonth = function(line) {
            var filter = {line:line};
            if (this.id==0) { //creating collation
                this.deleteItem("deliveryMonths",filter);
            }
            else { //updating, there may be existing orders so just set it to deleted
                var newattributes = {
                    "deleted": true
                };
                this.updateItemValues("deliveryMonths",filter,newattributes);
            }
        };
        collationModel.changeDeliveryMonth = function(line,newDeliveryMonth) {
            var filter = {line:line};
            this.updateItem("deliveryMonths",filter,newDeliveryMonth);
        };
        collationModel.updateDeliveryMonth = function(line,newattributes) {
            var filter = {line:line};
            this.updateItemValues("deliveryMonths",filter,newattributes);
        };
        collationModel.hideUnhideDeliveryMonth = function(line) {
            var filter = {line:line};
            var deliveryMonth = this.getDeliveryMonth(line);
            var newattributes = {
                "hidden": !deliveryMonth.hidden
            };
            this.updateItemValues("deliveryMonths",filter,newattributes);
        };
        //general total,get,update,delete,add and addFrom(x)
        collationModel.getCollationItemPrice = function(line) {
            var filter = {line:line};
            return this.getItem("selectedCollationItemPrices",filter);
        };
        collationModel.addCollationItemPriceFromPrompt = function(type, value) {
            // this is used to add a product to the array
            //(mainly for the sanitation of the object returned from a modal or anything really)
            if (value == '' || value == null) {
                return;
            }
            var collationItemPrice = {
                "line" : this.selectedCollationItemPricesIndex, //index for non repeat logic
                "priceType": type,
                "value" : value
            };
            this.addCollationItemPrice(collationItemPrice);
        };
        collationModel.addCollationItemPrice = function(collationItemPrice) {
            this.addItem("selectedCollationItemPrices",collationItemPrice);
            this.selectedCollationItemPricesIndex++;
        };
        collationModel.removeCollationItemPrice = function(line) {
            var filter = {line:line};
            this.deleteItem("selectedCollationItemPrices",filter);
        };
        collationModel.removeAllCollationItemPrices = function() {
            var that = this;
            $.each(this.selectedCollationItemPrices,function(k,v){
                that.removeCollationItemPrice(v.line);
            });
        };
        collationModel.completeChangeCollationItemPrices = function(array) {
            var that = this;
            that.removeAllCollationItemPrices();
            $.each(array,function(k,v){
                that.addCollationItemPriceFromPrompt(v.priceType, v.value);
            });
        };
        collationModel.changeCollationItemPrice = function(line,newCollationItemPrice) {
            var filter = {line:line};
            this.updateItem("selectedCollationItemPrices",filter,newCollationItemPrice);
        };
        collationModel.updateCollationItemPrice = function(line,newattributes) {
            var filter = {line:line};
            this.updateItemValues("selectedCollationItemPrices",filter,newattributes);
        };
        //validation and saving
        collationModel.completeCollation = function() {
            if(!this.validate()) {return;}
            this.saveModel(this.saveURL,"collationData",this.onSave);
        };
        collationModel.validate = function() {
            if(this.collationItems.length==0) {
                alert("You need to add at least a single product to this collation.");
                return false;
            }
            if(this.subject.length==0) {
                alert("Subject/Title cannot be blank.");
                return false;
            }
            if(this.content.length==0) {
                alert("Content cannot be blank.");
                return false;
            }
            if(this.startDate.length==0||this.endDate.length==0||this.archiveDate.length==0) {
                alert("Please fill in all the dates.");
                return false;
            }
            if (this.deliveryMonths.length==0) {
                alert("Please add a Delivery Month to the collation.");
                return false;
            }
            if (this.toStores.length==0&&this.toGroups.length==0) {
                alert("Please add at least one recipient");
                return false;
            }
            return true;
        };
        collationModel.loadCollation = function(collationData) {
            var that = this;
            this.set('id',collationData.id);
            this.set('subject',collationData.subject);
            this.set('startDate',collationData.startDate);
            this.set('endDate',collationData.endDate);
            this.set('archiveDate',collationData.archiveDate);
            this.set('tag',collationData.tag);
            this.set('content',collationData.content);
            this.set('orderMethod',collationData.orderMethod);
            this.set('notes',collationData.notes);
            this.set('viewType',collationData.viewType);
            this.set('toGroups', collationData.toGroups);
            this.set('toStores', collationData.toStores);

            $.each(collationData.collationItems,function(k,v) {
                that.loadCollationItem(v);
            });

            console.log(collationData)

            $.each(collationData.deliveryMonths, function(k,v) {
                that.loadDeliveryMonth(v);
            });

            this.set('sendSMS',collationData.sendSMS);
            this.set('sendEmail',collationData.sendEmail);
            this.set('sendSMSReminder',collationData.sendSMSReminder);
            this.set('sendEmailReminder',collationData.sendEmailReminder);
        };
        collationModel.onSave = function(msg) {
            window.onbeforeunload = null;
            window.location = msg.redirect;
        };

        return collationModel;
    };

}( window.br = window.br || {}, jQuery, _ ));