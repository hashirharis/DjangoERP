//Adding New Functionality to br.base
(function( br, $, _, undefined ) {
    //Public Method
    br.walkInCustomerID = 0;
    br.creditPaymentID = 14;
    br.accountParentID = 9;

    br.saleModel = function(model) { // can optionally accept an existing invoiceModel
        if (model==undefined) { //default model instance
            model = {
                id: 0,
                status:"NEW",
                salesLines: [],
                salesTotalInGST: 0,
                salesTotalExGST: 0,
                salesTotalGST: 0,
                isRefund: false,
                paymentLines: [],
                paymentsTotal: 0,
                paymentsGrouping:1,
                paymentLineIndex: 0,
                printingAvailable: false,
                totalOwing: 0,
                releasedTotal: 0,
                toReleaseTotal: 0,
                storeNote:"",
                saleNote:"",
                saleLineIndex:1,
                customerID:0, //walkin customer
                customer:undefined,
                deliveryAddress: "",
                invoiceLines: [],
                invoiceLineIndex: 0,
                newInvoiceLines: [],
                saveURL: ""
            }
        }
        var saleModel = br.baseModel(model);
        //salesLinesRelated
        saleModel.updateSalesTotals = function() {
            var total = 0;
            var taxTotal = 0;
            var subTotal = 0;
            var releasedTotal = 0;
            var toReleaseTotal = 0;

            $.each(this.salesLines, function(k,v) {
                total += v.totalPrice;
                releasedTotal += v.unitPrice * (v.released+ v.toRelease);
                toReleaseTotal += v.unitPrice * v.toRelease;
                subTotal += (v.totalPrice / br.GST);
            });
            taxTotal = total - subTotal;

            this.set('releasedTotal', releasedTotal)
            this.set('toReleaseTotal', toReleaseTotal)
            this.set('salesTotalExGST',subTotal);
            this.set('salesTotalGST',taxTotal);
            this.set('salesTotalInGST',total);
            this.updateOwing();
        };
        saleModel.getSalesLine = function(lineid) {
            var filter = {line:lineid};
            return this.getItem("salesLines",filter);
        };
        saleModel.addProductFromModal = function(productObj) {
            // this is used to add a product to the sale
            var salesLine = {
                line: this.saleLineIndex,
                productID: productObj.id,
                isWarranty: parseInt(productObj.isWarranty),
                warrantyRef: productObj.warrantyRef,
                modelNum: productObj.modelNum,
                description: productObj.description,
                unitCostPrice: parseFloat(productObj.SpanNetPlusGST),
                lineCostPrice: parseFloat(productObj.SpanNetPlusGST),
                availableStock: parseInt(productObj.availableStock),
                quantity: 1,
                released: 0,
                toRelease: 0,
                barcodes: '',
                unitPrice: parseFloat(productObj.goPrice),
                totalPrice: parseFloat(productObj.goPrice)
            };
            this.addSalesLine(salesLine);
            return salesLine;
        };
        saleModel.loadSalesLine = function(salesLineObj) {
            var salesLine = $.extend(true,{},salesLineObj);
            salesLine.unitCostPrice = parseFloat(salesLine.unitCostPrice);
            salesLine.lineCostPrice = parseFloat(salesLine.lineCostPrice);
            salesLine.unitPrice =  parseFloat(salesLine.unitPrice);
            salesLine.totalPrice = parseFloat(salesLine.totalPrice);
            salesLine.toRelease = 0;
            salesLine.barcodes = '';
            this.addSalesLine(salesLine);
        };
        saleModel.addSalesLine = function(salesLine) {
            this.addItem("salesLines",salesLine);
            this.saleLineIndex++;
            this.updateSalesTotals();
        };
        saleModel.removeSalesLine = function(line) {
            var filter = {line:line};
            this.deleteItem("salesLines",filter);
            this.updateSalesTotals();
        };
        saleModel.changeSalesLine = function(lineid,newSalesLine) {
            var filter = {line:lineid};
            this.updateItem("salesLines",filter,newSalesLine);
            this.updateSalesTotals();
        };
        saleModel.updateSaleData = function(lineid,newattributes) {
            var filter = {line:lineid};
            this.updateItemValues("salesLines",filter,newattributes);
            this.updateSalesTotals();
        };
        saleModel.negateSalesLine = function(lineid) {
            var saleLine = this.getSalesLine(lineid);
            if (saleLine.released!=0) {
                alert("You cannot delete a line which has been released!");
                return;
            }
            this.removeSalesLine(lineid);
        };
        saleModel.changeLineQuantity = function(lineid,quantity) {
            if (quantity == '' || quantity == null) {
                return;
            }
            if (isNaN(parseInt(quantity))) {
                alert("Invalid Quantity Value Entered");
                return;
            }
            quantity = parseInt(quantity);
            var saleLine = this.getSalesLine(lineid);
            if (saleLine.released!=0) {
                if (saleModel.isRefund&&quantity>saleLine.released) {
                    alert("Please enter a quantity that is less than the released amount");
                    return;
                }
                if (!saleModel.isRefund&&quantity<saleLine.released) {
                    alert("Please enter a quantity that is greater than the released amount");
                    return;
                }
            }
            if (quantity == 0) {
                this.removeSalesLine(lineid);
                return;
            }
            if (quantity < 0) {
                this.set("isRefund",true);
            }else {
                this.set("isRefund",false);
            }
            var changes = {};
            changes.quantity = quantity;
            changes.totalPrice = quantity * saleLine.unitPrice;
            this.updateSaleData(lineid,changes);
        };
        saleModel.changeLineBarcodes = function(lineid, barcodes) {
            var changes = {};
            changes.barcodes = barcodes;
            this.updateSaleData(lineid,changes);
        };
        saleModel.changeLineReleased = function(lineid, newVal) {
            if (newVal == '' || newVal == null) {
                return false;
            }
            if (isNaN(parseInt(newVal))) {
                alert("Invalid Released Value Entered");
                return false;
            }
            newVal = parseInt(newVal);
            var saleLine = this.getSalesLine(lineid);
            if (!saleModel.isRefund) {
                if(newVal>saleLine.quantity-saleLine.released) {
                    alert("This value is greater than the remaining balance of products!");
                    return false;
                }
                if (newVal*saleLine.unitPrice>this.paymentsTotal-this.releasedTotal+(saleLine.unitPrice*saleLine.toRelease)){ //exclude current toRelease value from calc
                    alert("Please process a payment equivalent to the value of the products being released first!")
                    return false;
                }
            }
            else {
                if(newVal<saleLine.quantity-saleLine.released) {
                    alert("This value is greater than the remaining balance of products!");
                    return false;
                }
                if (newVal*saleLine.unitPrice<this.paymentsTotal-this.releasedTotal+(saleLine.unitPrice*saleLine.toRelease)){ //exclude current toRelease value from calc
                    alert("Please process a payment equivalent to the value of the products being released first!")
                    return false;
                }
            }

            //create a invoice and invoice lines
            var changes = {};
            changes.toRelease = newVal;
            this.updateSaleData(lineid,changes);
            return true;
        };
        saleModel.changeLineUnitPrice = function(lineid,unitPrice) {
            if (unitPrice == '' || unitPrice == null) {
                return;
            }
            if (isNaN(parseFloat(unitPrice))) {
                alert("Invalid Unit Price Value Entered!");
                return;
            }
            unitPrice = parseFloat(unitPrice);
            var saleLine = this.getSalesLine(lineid);
            var changes = {};
            changes.unitPrice = unitPrice;
            changes.totalPrice = saleLine.quantity * unitPrice;
            this.updateSaleData(lineid,changes);
        };
        saleModel.changeLineTotalPrice = function(lineid,totalPrice) {
            var saleLine = this.getSalesLine(lineid);
            var changes = {};
            changes.totalPrice = totalPrice
            changes.unitPrice = (totalPrice/saleLine.quantity);
            this.updateSaleData(lineid,changes);
        };
        saleModel.changeLineWarrantyRef = function(lineid,warrantyRef) {
            var changes = {};
            changes.warrantyRef = warrantyRef;
            this.updateSaleData(lineid,changes);
        };
        //interface elements i.e changing quantity changing total price should go on the page itself. this is only for logic
        //end of salesLinesRelated
        //Customer Related
        saleModel.addCustomerFromModal = function(obj) {
            var customer = {
                id: obj.id,
                name: obj.name,
                firstContact: obj.firstContact,
                htmlAddress: obj.htmlAddress,
                creditLimit: obj.creditLimit
            }
            saleModel.setCustomer(obj);
        };
        saleModel.setCustomer = function(customerIDOrObj) {
            if (_.isObject(customerIDOrObj)) { //customer object
                this.set('customer',customerIDOrObj);
                this.set('customerID',customerIDOrObj.id);
                this.set("deliveryAddress",customerIDOrObj.htmlAddress);
            }
            else if (_.isNumber(customerIDOrObj)) { //id
                if (customerIDOrObj ==4) { return; }
                this.set('customerID',customerIDOrObj);
            }
        };
        //end of customer related
        saleModel.addPaymentFromModal = function(paymentObj) {
            var payment = paymentObj;
            payment.group = this.paymentsGrouping;
            payment.line = this.paymentLineIndex;
            this.addPayment(payment);
        };
        saleModel.loadPayment = function(paymentObj) {
            var payment = paymentObj;
            payment.paymentDate = new Date(payment.paymentDate);
            payment.dateToString = payment.paymentDate.toLocaleString();
            payment.amount = parseFloat(payment.amount);
            payment.line = this.paymentLineIndex;
            this.addPayment(payment);
        };
        saleModel.addPayment = function(payment) {
            if (payment.amount ==0||payment.amount==undefined||isNaN(payment.amount)) {
                alert("Please enter a valid payment amount");
                return
            }
            this.paymentLineIndex++;
            this.addItem("paymentLines",payment);
            this.updatePaymentTotals();
        };
        saleModel.removePayment = function(line) {
            var filter = {line:line};
            this.deleteItem("paymentLines",filter);
            this.updatePaymentTotals();
        };
        saleModel.updatePaymentTotals = function() {
            var total = 0;
            $.each(this.paymentLines, function(k,v) {
                total += v.amount;
            });
            this.set('paymentsTotal',total);
            this.updateOwing();
        };
        saleModel.updateOwing = function() {
            var total = this.salesTotalInGST - this.paymentsTotal;
            this.set('totalOwing', total);
        };
        //invoice functions
        saleModel.loadInvoice = function(invoiceObj) {
            var invoice = invoiceObj;
            invoice.created = new Date(invoice.created);
            invoice.createdToString = invoice.created.toLocaleString();
            invoice.total = parseFloat(invoice.total);
            invoice.line = this.invoiceLineIndex;
            this.addItem("invoiceLines",invoice);
            this.invoiceLineIndex++;
        };
        saleModel.generateTaxInvoices = function() {
            //update salesline release quantity
            $.each(saleModel.salesLines, function(k,v) {
                if (v.toRelease) {
                    var invLine = {
                        quantity: v.toRelease,
                        unitPrice: v.unitPrice,
                        totalPrice: v.unitPrice* v.toRelease,
                        line: v.line
                    };
                    saleModel.newInvoiceLines.push(invLine);
                    //saleModel.updateSaleData(v.line,{released: v.released, toRelease: v.toRelease});
                }
            });
        };
        //saving and validation methods
        saleModel.completeSale = function() {
            //round the total owing amount because javascript may not pick it up
            if (this.totalOwing.round(2)==0.00&&this.salesTotalInGST==this.releasedTotal) { //sale - completed status
                this.set('status','COMPLETED');
            }
            else {
                this.set("status","PENDING");
            }
            if(!this.validate()) {return;}
            this.generateTaxInvoices();
            this.saveModel(this.saveURL,"salesData",this.onSave);
        };
        saleModel.saveAsQuote = function() {
            //SAVED, COMPLETE, ON-ACCOUNT, LAYBY
            this.set('status','QUOTE');
            if(!this.validateQuote()){return;}
            this.saveModel(this.saveURL,"salesData",this.onSave);
        };
        saleModel.validate = function() {
            if(this.salesLines.length==0) {
                alert("You need to add at least a single product to this sale in order to be able to save it.");
                return false;
            }
            if(this.customerID==0||this.customerID==br.walkInCustomerID) {
                alert("This sale must have a valid customer attached!")
                return false;
            }
            return true;
        };
        saleModel.validateQuote = function() {
            if(this.customerID==br.walkInCustomerID) {
                alert("You need to assign this quote to a customer to be able to continue.");
                return false;
            }
            if(this.salesLines.length==0) {
                alert("You need to add at least a single product to this Quote in order to be able to save it.");
                return false;
            }
            return true;
        };
        saleModel.loadSale = function(salesData) {
            var that = this;
            this.set('id',salesData.id);
            this.set('status',salesData.status);
            this.set('paymentsGrouping',salesData.paymentsGrouping);
            this.set('printingAvailable',(salesData.paymentsGrouping>1));
            this.set('storeNote',salesData.storeNote);
            this.set('saleNote',salesData.saleNote);
            this.set('isRefund', _.some(salesData.salesLines, function(v) { return v.quantity<0;}));
            this.setCustomer(salesData.customer);
            $.each(salesData.salesLines,function(k,v) {
                that.loadSalesLine(v);
            });
            $.each(salesData.paymentLines, function(k,v) {
                that.loadPayment(v);
            });
            $.each(salesData.invoiceLines, function(k,v) {
                that.loadInvoice(v);
            });
        };
        saleModel.onSave = function(msg) {
            window.onbeforeunload = null;
            window.location = msg.openSale;
        };
        return saleModel;
    };
}( window.br = window.br || {}, jQuery, _ ));