(function( br, $, _, undefined ) {

   	br.orderModel = function(jsonStores,model) {
        var extend = {
            id: 0, //other vars
            status: "NEW",
            type: "Order from Supplier",
            purchaser: 1,
            currentStore: 0,
            currentStoreCode: "",
            currentStaffCode: "",
            currentStaffOrder: 0, // how many orders the staff member has placed incremented by one (used for order num generation)
            orderingStore: undefined, //store we are ordering behalf of, this will be undefined if store cannot order on behalf of anyone.
            openToBuy: 0, //open to buy limit for store.
            orderLines: [],
            orderLinesIndex: 1,
            orderReference: "",
            packingSlipNumber: "",
            invoice: undefined, // {} of invoice object
            invoiceID: 0,
            comment: "",
            totalInvoiceExGST: 0,
            totalGST:0,
            totalInvoiceInGST:0,
            storeNetInGST:0,
            storeNetExGST:0,
            supplierID:0,
            //et specific
            supplierHasET: false,
            is_et: false,
            et : undefined, // if this model is et then this will hold the variables.
            etInstructions:[],
            etInstructionsIndex: 0
        };
        extend = _.extend(extend,model);
        var orderModel = br.baseModel(extend);
        var jsonStores = jsonStores;

        orderModel.updateTotals = function() {
            //totalvariables
            var totalInvoiceExGST = 0;
            var totalGST = 0;
            var totalInvoiceInGST = 0;
            var storeNetInGST = 0;

            $.each(this.orderLines, function(k,v) {
                //calculations
                storeNetInGST += v.lineNetIncGST;
                totalInvoiceExGST += v.invoiceExGST * v.quantity;
                totalInvoiceInGST += v.invoiceIncGST * v.quantity;
            });
            totalGST = totalInvoiceInGST - totalInvoiceExGST;

            //set totals on model
            this.set('totalInvoiceExGST',totalInvoiceExGST);
            this.set("totalGST",totalGST);
            this.set("totalInvoiceInGST",totalInvoiceInGST);
            this.set("storeNetExGST",storeNetInGST/1.1);
            this.set("storeNetInGST",storeNetInGST);
        };
        orderModel.getOrderLine = function(line) {
            var filter = {line:line};
            return this.getItem("orderLines",filter);
        };
        orderModel.addOrderLineFromModal = function(modalObj) {
            // this is used to add a product to the array
            //(mainly for the sanitation of the object returned from a modal or anything really)
            var supplierObj = {
                "id" : parseInt(modalObj.supplierID),
                "hasET" : (modalObj.supplierHasET=="True")
            };
            this.setSupplier(supplierObj);
            //add it.
            var invoiceIncGST = (parseFloat(modalObj.offInvoicePrice)*br.GST);
            var orderLine = {
                "line" : this.orderLinesIndex, //index for non repeat logic
                "productID" : modalObj.id,
                "EAN" : modalObj.EAN,
                "modelNum" : modalObj.modelNum,
                "quantity" : 1,
                "description" : modalObj.description,
                "originalInvoiceExGST" : parseFloat(modalObj.offInvoicePrice),
                "invoiceExGST": parseFloat(modalObj.offInvoicePrice),
                "invoiceIncGST": invoiceIncGST,
                "unitNetIncGST": parseFloat(modalObj.SpanNetPlusGST),
                "lineNetIncGST": parseFloat(modalObj.SpanNetPlusGST)
            };
            this.addOrderLine(orderLine);
        };
       orderModel.addOrderLineFromServer = function(serverObj) {
           // this is used to add a product to the array
           //(mainly for the sanitation of the object returned from a modal or anything really)
           var invoiceIncGST = (parseFloat(serverObj.invoicePrice)*br.GST);
           var orderLine = {
               "line" : this.orderLinesIndex, //index for non repeat logic
               "productID" : serverObj.id,
               "EAN" : serverObj.EAN,
               "modelNum" : serverObj.modelNum,
               "quantity" : serverObj.quantity,
               "description" : serverObj.description,
               "originalInvoiceExGST" : parseFloat(serverObj.invoiceOriginal),
               "invoiceExGST": parseFloat(serverObj.invoicePrice),
               "invoiceIncGST": invoiceIncGST,
               "unitNetIncGST": parseFloat(serverObj.netPrice),
               "lineNetIncGST": parseFloat(serverObj.lineNet)
           };
           this.addOrderLine(orderLine);
       };
        orderModel.addOrderLine = function(orderLine) {
            this.addItem("orderLines",orderLine);
            this.orderLinesIndex++;
            this.updateTotals();
        };
        orderModel.removeOrderLine = function(line) {
            var filter = {line:line};
            this.deleteItem("orderLines",filter);
            this.updateTotals();
        };
        orderModel.removeAllOrderLines = function() {
            var that = this;
            $.each(this.orderLines,function(k,v){
                that.removeOrderLine(v.line);
            });
        };
        orderModel.changeOrderLine = function(line,newOrderLine) {
            var filter = {line:line};
            this.updateItem("orderLines",filter,newOrderLine);
            this.updateTotals();
        };
        orderModel.updateOrderLine = function(line,newattributes) {
            var filter = {line:line};
            this.updateItemValues("orderLines",filter,newattributes);
            this.updateTotals();
        };
        orderModel.changeLineQuantity = function(line,quantity) {
            if (quantity == '' || quantity == null) {
                return;
            }
            if (isNaN(parseInt(quantity))) {
                alert("Invalid Quantity Value Entered");
                return;
            }
            quantity = parseInt(quantity);
            if (quantity == 0) {
                this.removeOrderLine(line);
                return;
            }
            var orderLine = this.getOrderLine(line);
            var unitPrice = orderLine.unitNetIncGST;
            var changes = {};
            changes.lineNetIncGST = unitPrice*quantity;
            changes.quantity = quantity;
            this.updateOrderLine(line,changes);
        };
        orderModel.changeLineInvoicePrice = function(line,newprice,url) {
            if (newprice == '' || newprice == null) {
                return;
            }
            if (isNaN(parseFloat(newprice))) {
                alert("Invalid Value Entered!");
                return;
            }
            var that = this;
            var orderLine = this.getOrderLine(line);

            var request = $.ajax({
                url: url,
                type: "POST",
                data: {id : orderLine.productID, invoicePrice : newprice },
                dataType: "json",
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", br.getCookie('csrftoken'));
                }
            });

            request.done(function(msg) {
                var quantity = orderLine.quantity;
                var unitPrice = parseFloat(msg.result);
                var invoicePrice = parseFloat(newprice);
                var changes = {};
                changes.invoiceExGST = invoicePrice;
                changes.invoiceIncGST = invoicePrice * br.GST;
                changes.unitNetIncGST = unitPrice;
                changes.lineNetIncGST = unitPrice*quantity;
                that.updateOrderLine(line,changes);
            });
        };
       //misc methods:
       orderModel.setSupplier = function(supplierObj) {
           if(!this.supplierID==0 && !_.isUndefined(this.supplierID)){
               if(supplierObj.id!=this.supplierID) {
                   if(confirm("This product is a different supplier to the other product(s) on this order, do you wish to remove the other products?")){
                       this.removeAllOrderLines();
                   }else{
                       return;
                   }
               }
           }
           this.set("supplierID",supplierObj.id);
           this.set("supplierHasET",supplierObj.hasET);
       };
       orderModel.regenerateOrderReference = function() {
           if (this.orderReference.length) {
               if(!confirm("Do you want to regenerate the order reference ?")) {return;}
           }
           var that = this;
           var store_code = this.currentStoreCode;
           if (!_.isNaN(this.orderingStore)) { // can order on another stores behalf.
               var behalfOf = '';
               $.each(jsonStores,function(k,v) {
                   if (v.id == that.orderingStore){
                       behalfOf = v.code;
                       return false;
                   }
               });
               if (behalfOf == store_code) {
                   store_code = behalfOf;
               }
               else {
                   store_code = store_code + "-" + behalfOf
               }
           }
           var orderRef = store_code + "-" + this.currentStaffCode + "-" + this.currentStaffOrder;
           this.set("orderReference",orderRef);
       };
       //action to/from server methods
       orderModel.saveToServer = function(url,save) {
           console.log(this);
           if(this.et==undefined&&!save&&this.ElectronicTradingConfirm()) {
               //et order ?
               return; //if the user wants this to be an electronic order then fill out additional information before proceeding.
           }
           if(this.et!=undefined&&this.is_et) {
               // this is an et order so do et checks.
               var invalid = false;
               _.some(this.orderLines, function(v) {
                   //if any of the lines have model numbers equal to the EAN then there will be an issue with the order
                   if(v.modelNum==v.EAN) {
                        invalid = true;
                   };
               });
                if(invalid) {return;}
           }
           if(save==undefined&&!confirm("Are you sure you want to place this order (this is not reversible) ?")) {
              return;
           }
           if(!this.validateSaveToServer()) { return;};
           this.saveModel(url,"orderData",this.onSave);
       };
       orderModel.validateSaveToServer = function() {
            if (this.orderLines.length==0) {
                alert("Add Items to the order!");
                return false;
            }
            if(this.orderReference.length==0) {
                alert("Please enter an order reference for this order!");
                return false;
            }
           if(this.storeNetExGST>this.openToBuy) {
                alert("You are not able to place this order as you are over your openToBuy amount. Please contact Head Office.");
               return false;
           }
            return true;
       };
       orderModel.onSave = function(msg) {
            window.location = msg.openOrder;
       };
       orderModel.loadOrderFromServer = function(serverModel) {
            var that = this;
            this.set("id",parseInt(serverModel.id));
            this.set("supplierID",parseInt(serverModel.supplier));
            this.set("supplierHasET",serverModel.supplierHasET);
            this.set("orderReference",serverModel.orderReference);
            this.set("status",serverModel.status);
            if (parseInt(serverModel.store)!=this.currentStore) {
                this.set("orderingStore",parseInt(serverModel.store));
            }
            this.set("comment",serverModel.note);
            this.set("packingSlipNumber",serverModel.packingSlipNumber);
            this.set("type",serverModel.type);
            this.set("is_et",serverModel.et);
            this.set("purchaser",serverModel.purchaser);
        	$.each(serverModel.orderLines,function(k,v) {
       	        that.addOrderLineFromServer(v);
        	});
           //TODO:set invoice if attached
       };
       //ET functions
       orderModel.ElectronicTradingConfirm = function() {
           if(this.supplierHasET) {
               if(confirm("Do you want to send this order via Electronic Trading?")) {
                   this.set("is_et",true);
                   return true;
               }
           }
           return false;
       };
       orderModel.setAndSaveElectronicOrder = function(electronicOrder,url) {
           //validate et variables
           this.set("et",electronicOrder);
           this.saveToServer(url);
       };
       orderModel.getETInstruction = function(line) {
           var filter = {line:line};
           return this.getItem("etInstructions",filter);
       };
       orderModel.addETInstructionFromModal = function(modalObj) {
           //validate
           if (modalObj.line1.length<=0) {
               alert("Enter or select at least one line on line 1!");
               return false;
           }
           var etInstruction = {
               "line" : this.etInstructionsIndex, //index for non repeat logic
               "type" : modalObj.type,
               "line1" : modalObj.line1,
               "line2" : modalObj.line2,
               "line3" : modalObj.line3,
               "line4" : modalObj.line4,
               "line5" : modalObj.line5
           };
           this.addETInstruction(etInstruction);
           return true;
       };
       orderModel.addETInstruction = function(etInstruction) {
           this.addItem("etInstructions",etInstruction);
           this.etInstructionsIndex++;
       };
       orderModel.removeETInstruction = function(line) {
           var filter = {line:line};
           this.deleteItem("etInstructions",filter);
       };
       orderModel.changeETInstruction = function(line,newETInstruction) {
           var filter = {line:line};
           this.updateItem("etInstructions",filter,newETInstruction);
       };
       orderModel.updateETInstruction = function(line,newattributes) {
           var filter = {line:line};
           this.updateItemValues("etInstructions",filter,newattributes);
       };
        return orderModel;
    };

}( window.br = window.br || {}, jQuery, _ ));