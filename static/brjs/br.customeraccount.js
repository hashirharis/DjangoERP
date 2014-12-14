(function( br, $, _, undefined ) {
    br.accountParentID = 9;
    br.creditPaymentID = 14;

 	br.customerAccount = function(model) {
 		if (model==undefined) { //default model instance
            model = {
                id: 0, //other vars
                total: 0,
                totalOwing: 0,
                ledgerEntries: [],
                ledgerEntriesIndex: 0,
                paymentLines: [],
                paymentsTotal: 0,
                paymentsGrouping:1,
                paymentLineIndex: 0
            }
        }
        var customerAccount = br.baseModel(model);
        //general total,get,update,delete,add and addFrom(x)
        customerAccount.updateTotal = function(total) {
            this.set('total', total);
            this.updateOwing();
        }
        customerAccount.addLedgerEntries = function(paidForArray) {
            if(this.ledgerEntries.length) {
                this.ledgerEntries = [];
                this.ledgerEntriesIndex = 0;
            }
            var that = this;
            $.each(paidForArray, function() {
                var toAdd = this;
                toAdd.line = that.ledgerEntriesIndex;
                that.addItem("ledgerEntries",toAdd);
                that.ledgerEntriesIndex++;
            });
        }
        customerAccount.addPaymentFromModal = function(paymentObj) {
            var payment = paymentObj;
            payment.group = this.paymentsGrouping;
            payment.line = this.paymentLineIndex;
            this.addPayment(payment);
        };
        customerAccount.loadPayment = function(paymentObj) {
            var payment = paymentObj;
            payment.paymentDate = new Date(payment.paymentDate);
            payment.dateToString = payment.paymentDate.toLocaleString();
            payment.amount = parseFloat(payment.amount);
            payment.line = this.paymentLineIndex;
            this.addPayment(payment);
        };
        customerAccount.addPayment = function(payment) {
            if (payment.amount ==0||payment.amount==undefined||isNaN(payment.amount)) {
                alert("Please enter a valid payment amount");
                return
            }
            this.paymentLineIndex++;
            this.addItem("paymentLines",payment);
            this.updatePaymentTotals();
        };
        customerAccount.removePayment = function(line) {
            var filter = {line:line};
            this.deleteItem("paymentLines",filter);
            this.updatePaymentTotals();
        };
        customerAccount.removeAllPayments = function() {
            var that = this;
            $.each(this.paymentLines, function(k,v) {
                var line = v.line;
                that.removePayment(line)
            });
        }
        customerAccount.updatePaymentTotals = function() {
            var total = 0;
            $.each(this.paymentLines, function(k,v) {
                total += v.amount;
            });
            this.set('paymentsTotal',total);
            this.updateOwing();
        };
        customerAccount.updateOwing = function() {
            var total = this.total - this.paymentsTotal;
            this.set('totalOwing', total);
        };
        customerAccount.validate = function() {
            if (this.totalOwing==0) {
                return true;
            }
            return false;
        };
        customerAccount.savePayments = function(url) {
            if(!this.validate()) {
                alert("The payments : $" + this.paymentsTotal + " do not match the total : $" + this.total)
                return;
            }
            this.saveModel(url,"accountPayments",this.onSave);
        };
        customerAccount.onSave = function(msg) {
            if(msg.error==undefined) {
                window.location.reload();
            }
            else {
                alert(msg.error);
            }
        };
        return customerAccount;
    };

}( window.br = window.br || {}, jQuery, _ ));