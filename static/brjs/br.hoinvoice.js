//Adding New Functionality to br.base
(function( br, $, _, undefined ) {
    //Public Method
    br.hoInvoiceModel = function(model) { // can optionally accept an existing invoiceModel
        if (model==undefined) { //default model instance
            model = {
                id: 0,
                invoiceLines: [],
                invoiceLinesIndex:1,
                type: 'Purchase of stock',
                distributor: '',
                store:1,
                invoiceNumber : "",
                invoiceDate : undefined,//invoiceDate
                orderReference: "",
                otherInvoiceReference : "",
                hoComments: "",
                storeInformation: "",
                extendedCredit : false,
                freight : 0.00, //freight ex GST
                invTotal : 0.00,    //invoice in GST
                invTotalExGST: 0.00,
                netTotal : 0.00,    //netTotal Ex
                createdDate : '',
                dueDate: undefined,
                GSTTotal: 0.00,     // total tax
                NetCalculationUrl:"",
                viewOnly: false
            }
        }
        var hoInvoiceModel = br.baseModel(model);
        hoInvoiceModel.updateInvoiceTotals = function() {
            var totalInvoiceInc = 0.00;
            var totalInvoiceEx = 0.00;
            var totalGST = 0.00;
            var totalStoreNetEx = 0.00;
            var totalFreightEx = this.freight;
            var totalFreightIn = totalFreightEx*br.GST;

            $.each(this.invoiceLines,function(k,v){
                totalInvoiceInc += v.linePriceInGST;
                totalInvoiceEx += v.linePriceExGST;
                totalGST += v.totalTax;
                totalStoreNetEx += v.lineSpanNet;
            });

            totalInvoiceInc += totalFreightIn;
            totalInvoiceEx += totalFreightEx;
            totalGST += (totalFreightIn-totalFreightEx);
            totalStoreNetEx += totalFreightEx;

            this.set('invTotal',totalInvoiceInc);
            this.set('freight',totalFreightEx);
            this.set('netTotal',totalStoreNetEx);
            this.set('freightGST',(totalFreightIn-totalFreightEx));
            this.set('GSTTotal',totalGST);
            this.set('invTotalExGST',totalInvoiceEx);
        };
        hoInvoiceModel.getInvoiceLine = function(lineid) {
            var filter = {line:lineid};
            return this.getItem("invoiceLines",filter);
        };
        hoInvoiceModel.addProductFromModal = function(productObj) {
            // this is used to add a product to the invoice (mainly for the sanitation of the object returned from the modal)
            var unitPriceExGST = parseFloat(productObj.invActual);
            var linePriceInGST = parseFloat(productObj.invActual)*br.GST;
            var linePriceExGST = parseFloat(productObj.invActual);
            var spanNetExGST = parseFloat(productObj.spanNet);
            var invoiceLine = {
                "line" : this.invoiceLinesIndex,
                "productID" : productObj.id,
                "quantity" : 1,
                "modelNum" : productObj.modelNum,
                "description": productObj.description,
                "unitPriceExGST": unitPriceExGST,
                "linePriceInGST": linePriceInGST,
                "totalTax" : linePriceInGST - linePriceExGST,
                "unitSpanNet" : spanNetExGST, //ExGST
                "lineSpanNet" : spanNetExGST,
                "linePriceExGST" : linePriceExGST
            };
            this.addInvoiceLine(invoiceLine);
        };
        hoInvoiceModel.loadInvoiceLine = function(serverObj) {
            var unitPriceExGST = parseFloat(serverObj.invActual);
            var quantity = parseInt(serverObj.quantity)
            var linePriceInGST = unitPriceExGST*quantity*br.GST;
            var linePriceExGST = unitPriceExGST*quantity;
            var spanNetExGST = parseFloat(serverObj.spanNet);
            var invoiceLine = {
                "line" : this.invoiceLinesIndex,
                "productID" : serverObj.id,
                "quantity" : quantity,
                "modelNum" : serverObj.modelNum,
                "description": serverObj.description,
                "unitPriceExGST": unitPriceExGST,
                "linePriceInGST": linePriceInGST,
                "totalTax" : linePriceInGST - linePriceExGST,
                "unitSpanNet" : spanNetExGST, //ExGST
                "lineSpanNet" : spanNetExGST*quantity,
                "linePriceExGST" : linePriceExGST
            };
            this.addInvoiceLine(invoiceLine);
        };
        hoInvoiceModel.addInvoiceLine = function(salesLine) {
            this.addItem("invoiceLines",salesLine);
            this.invoiceLinesIndex++;
            this.updateInvoiceTotals();
        };
        hoInvoiceModel.removeInvoiceLine = function(line) {
            var filter = {line:line};
            this.deleteItem("invoiceLines",filter);
            this.updateInvoiceTotals();
        };
        hoInvoiceModel.removeAllInvoiceLines = function() {
            var that = this;
            $.each(this.invoiceLines,function(k,v){
                that.removeInvoiceLine(v.line);
            });
        };
        hoInvoiceModel.changeInvoiceLine = function(lineid,newInvoiceLine) {
            var filter = {line:lineid};
            this.updateItem("invoiceLines",filter,newInvoiceLine);
            this.updateInvoiceTotals();
        };
        hoInvoiceModel.updateInvoiceData = function(lineid,newattributes) {
            var filter = {line:lineid};
            this.updateItemValues("invoiceLines",filter,newattributes);
            this.updateInvoiceTotals();
        };
        hoInvoiceModel.changeLineQuantity = function(lineid,quantity) {
            if (quantity == '' || quantity == null) {
                return;
            }
            if (isNaN(parseInt(quantity))) {
                alert("Invalid Quantity Value Entered");
                return;
            }
            quantity = parseInt(quantity);
            if (quantity != 0) {
                var invoiceLine = this.getInvoiceLine(lineid);
                var changes = {};
                changes.quantity = quantity;
                changes.linePriceExGST = quantity * invoiceLine.unitPriceExGST
                changes.linePriceInGST = quantity * invoiceLine.unitPriceExGST * br.GST;
                changes.lineSpanNet = quantity * invoiceLine.unitSpanNet;
                changes.totalTax = changes.linePriceInGST - changes.linePriceExGST;
                this.updateInvoiceData(lineid,changes);
            }
            else {
                this.removeInvoiceLine(lineid);
            }
        };
        hoInvoiceModel.changeLineUnitPrice = function(lineid,unitPrice) {
            if (unitPrice == '' || unitPrice == null) {
                return;
            }
            if (isNaN(parseFloat(unitPrice))) {
                alert("Invalid Value Entered");
                return;
            }
            unitPrice = parseFloat(unitPrice);
            var invoiceLine = this.getInvoiceLine(lineid);
            var quantity = invoiceLine.quantity;
            var changes = {};
            changes.unitPriceExGST = unitPrice;
            changes.linePriceExGST = quantity * unitPrice;
            changes.linePriceInGST = quantity * unitPrice * br.GST;
            changes.totalTax = changes.linePriceInGST - changes.linePriceExGST;
            this.updateInvoiceData(lineid,changes);
        };
        hoInvoiceModel.changeFreight = function(freight) {
            if (freight == '' || freight == null) {
                return;
            }
            if (isNaN(parseFloat(freight))) {
                alert("Invalid Value Entered");
                return;
            }
            freight = parseFloat(freight);
            this.set('freight',freight);
            this.updateInvoiceTotals();
        };
        hoInvoiceModel.completeInvoice = function(url) {
            if(!this.validate()) {return;}
            this.saveModel(url,"invoiceData",this.onSave);
        };
        hoInvoiceModel.validate = function() {
            if (this.invoiceDate==undefined) {
                alert("Please enter a valid date for this invoice!");
                return false;
            }
            if (this.invoiceNumber=="") {
                alert("Please enter a invoice Number for this invoice!")
                return false;
            }
            if (this.orderReference=="") {
                if(!confirm("Are you sure you want to proceed with a blank order reference on this invoice?")){return false;}
            }
            if (this.invoiceLines.length==0) {
                alert("There are no lines on this invoice, please add some lines to this invoice if you wish to save it.");
            }
            return true;
        };
        hoInvoiceModel.onSave = function(msg) {
            window.location = msg.openInvoice;
        };
        hoInvoiceModel.populateFromB2B = function(url) {
            var that = this;
            $.getJSON(url, function(serverModel) {
                that.set('distributor',serverModel.distributor);
                that.set('invoiceNumber',serverModel.invoiceNumber);
                that.set('invoiceDate',new Date(serverModel.invoiceDate));
                that.set('orderReference',serverModel.orderReference);
                that.set('store',serverModel.store);
                $.each(serverModel.invoiceLines,function(k,v) {
                    that.loadInvoiceLine(v);
                });
            });
        };
        hoInvoiceModel.loadInvoice = function(serverModel) {
            var that = this;
            this.set('id',serverModel.id);
            this.set('distributor',serverModel.distributor);
            this.set('type',serverModel.type);
            this.set('store',serverModel.store);
            this.set('invoiceNumber',serverModel.invoiceNumber);
            this.set('invoiceDate',new Date(serverModel.invoiceDate));
            if (serverModel.dueDate!==undefined) {
                this.set('dueDate', new Date(serverModel.dueDate));
            }
            this.set('orderReference',serverModel.orderReference);
            this.set('otherInvoiceReference',serverModel.otherInvoiceReference);
            this.set('hoComments',serverModel.hoComments);
            this.set('storeInformation',serverModel.storeInformation);
            this.set('extendedCredit',serverModel.extendedCredit);
            this.set('freight',parseFloat(serverModel.freight));
            this.set('invTotal',parseFloat(serverModel.invTotal));
            this.set('invTotalExGST',parseFloat(serverModel.invTotalExGST));
            this.set('netTotal',parseFloat(serverModel.netTotal));
            this.set('createdDate',new Date(serverModel.createdDate));

            $.each(serverModel.invoiceLines,function(k,v) {
                that.loadInvoiceLine(v);
            });

        }
        return hoInvoiceModel;
    };
}( window.br = window.br || {}, jQuery, _ ));