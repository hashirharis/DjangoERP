/**
 * Created by Yussuf on 22/11/13.
 */
(function( br, $, _, undefined ) {
	//public
 	br.claimModel = function(model) {
 		if (model==undefined) { //default model instance
            model = {
                id: 0, //other vars
                status: "NEW",
                store: '', //if head office is requesting this will be filled out.
                storeid: 0,
                type: "PP", //price protection, incorrectly charged invoice supplier/head office.
                comments: "",
                //do we need the reference to the invoice ?
                claimLines: [],
                claimLinesIndex: 0,
                claimTotal: 0
            }
        }
        var claimModel = br.baseModel(model);

        //general total,get,update,delete,add and addFrom(x)
        claimModel.updateTotals = function() {
            var claimTotal = 0;

            $.each(this.claimLines, function(k,v) {
                claimTotal += v.claimTotal;
            });

            this.set('claimTotal',claimTotal);
        };
        claimModel.getClaimLine = function(line) {
            var filter = {line:line};
            return this.getItem("claimLines",filter);
        };
        claimModel.addClaimLineFromModal = function(modalObj) {
            // this is used to add a product to the array
            //(mainly for the sanitation of the object returned from a modal or anything really)
            var claimLine = {
                "line" : this.claimLinesIndex, //index for non repeat logic
                "id": modalObj.id,
                "description": modalObj.description,
                "unitPrice" : parseFloat(modalObj.unitPrice),
                "newUnitPrice": parseFloat(modalObj.unitPrice),
                "claimTotal": 0.00
            };
            this.addClaimLine(claimLine);
        };
        claimModel.loadClaimLine = function(obj) {
            var claimLine = {
                "line" : this.claimLinesIndex, //index for non repeat logic
                "id": obj.id,
                "description": obj.description,
                "unitPrice" : parseFloat(obj.unitPrice),
                "newUnitPrice": parseFloat(obj.newUnitPrice),
                "claimTotal": parseFloat(obj.unitPrice) - parseFloat(obj.newUnitPrice)
            };
            this.addClaimLine(claimLine);
        };
        claimModel.addClaimLine = function(claimLine) {
            this.addItem("claimLines",claimLine);
            this.claimLinesIndex++;
            this.updateTotals();
        };
        claimModel.removeClaimLine = function(line) {
            var filter = {line:line};
            this.deleteItem("claimLines",filter);
            this.updateTotals();
        };
        claimModel.changeClaimLine = function(line,newClaimLine) {
            var filter = {line:line};
            this.updateItem("claimLines",filter,newClaimLine);
            this.updateTotals();
        };
        claimModel.updateClaimLine = function(line,newattributes) {
            var filter = {line:line};
            this.updateItemValues("claimLines",filter,newattributes);
            this.updateTotals();
        };
        //example updating line information
        claimModel.changeLineUnitPrice = function(lineid,unitPrice) {
            if (unitPrice == '' || unitPrice == null) {
                return;
            }
            if (isNaN(parseFloat(unitPrice))) {
                alert("Invalid Unit Price Value Entered!");
                return;
            }
            unitPrice = parseFloat(unitPrice);
            var claimLine = this.getClaimLine(lineid);
            var changes = {};
            changes.newUnitPrice = unitPrice;
            changes.claimTotal = claimLine.unitPrice - changes.newUnitPrice;
            this.updateClaimLine(lineid,changes);
        };
        //example utility funcs
        claimModel.hasNSBI = function() {
            return _.some(this.claimLines, function(v) {
                return v.nsbiQuantity > 0
            });
        };
        claimModel.getIDs = function() {
            return _.map(this.claimLines, function(v) {
                return v.id;
            });
        }
        claimModel.saveClaim = function() {
            this.set("status","SAVED");
            this.saveModel(this.saveURL,"claimData",this.onSave);
        };
        claimModel.processClaim = function() {
            this.set("status","PENDING");
            this.saveModel(this.saveURL,"claimData",this.onSave);
        };
        claimModel.completeClaim = function() {
            this.set("status","COMPLETED");
            this.saveModel(this.saveURL,"claimData",this.onSave);
        };
        claimModel.loadClaim = function(data) {
            var that = this;
            this.set('id',data.id);
            this.set('type', data.type);
            this.set('status',data.status);
            $.each(data.claimLines,function(k,v) {
                that.loadClaimLine(v);
            });
        };
        claimModel.onSave = function(msg) {
            window.onbeforeunload = null;
            window.location = msg.open;
        };
        return claimModel;
    };

}( window.br = window.br || {}, jQuery, _ ));