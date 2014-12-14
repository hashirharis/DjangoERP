/**
 * Created by Yussuf on 22/11/13.
 */
(function( br, $, _, undefined ) {
	//public
 	br.stockTakeModel = function(model) {
 		if (model==undefined) { //default model instance
            model = {
                id: 0, //other vars
                status: "NEW",
                clearNSBI: true,
                stockTakeLines: [],
                stockTakeLinesIndex: 0
            }
        }
        var stockTakeModel = br.baseModel(model);

        //general total,get,update,delete,add and addFrom(x)
        stockTakeModel.getStockTakeLine = function(line) {
            var filter = {line:line};
            return this.getItem("stockTakeLines",filter);
        };
        stockTakeModel.addStockTakeLineFromForm = function(obj) {
            // this is used to add a product to the array
            //(mainly for the sanitation of the object returned from a modal or anything really)
            var stockTakeLine = {
                "line" : this.stockTakeLinesIndex, //index for non repeat logic
                "productID": parseInt(obj.productID),
                "quantity" : parseInt(obj.quantity),
                "systemQuantity" : parseInt(obj.systemQuantity),
                "nsbiQuantity" : parseInt(obj.nsbiQuantity),
                "description": obj.description
            };
            stockTakeLine.variance = stockTakeLine.quantity - stockTakeLine.systemQuantity;
            this.addStockTakeLine(stockTakeLine);
        };
        stockTakeModel.loadStockTakeLine = function(stockTakeLine) {
            var stockLine = $.extend(true,{},stockTakeLine);
            stockLine.line = this.stockTakeLinesIndex;
            stockLine.variance = stockTakeLine.quantity - stockTakeLine.systemQuantity;
            this.addItem("stockTakeLines",stockLine);
            this.stockTakeLinesIndex++;
        };
        stockTakeModel.addStockTakeLine = function(stockTakeLine) {
            this.addItem("stockTakeLines",stockTakeLine);
            this.stockTakeLinesIndex++;
        };
        stockTakeModel.removeStockTakeLine = function(line) {
            var filter = {line:line};
            this.deleteItem("stockTakeLines",filter);
        };
        stockTakeModel.changeStockTakeLine = function(line,newStockTakeLine) {
            var filter = {line:line};
            this.updateItem("stockTakeLines",filter,newStockTakeLine);
        };
        stockTakeModel.updateStockTakeLine = function(line,newattributes) {
            var filter = {line:line};
            this.updateItemValues("stockTakeLines",filter,newattributes);
        };
        //example updating line information
        stockTakeModel.changeLineQuantity = function(line,quantity) {
            //validation logic goes here
            if (quantity == '' || quantity == null) {
                return;
            }
            if (isNaN(parseInt(quantity))) {
                alert("Invalid Quantity Value Entered");
                return;
            }
            quantity = parseInt(quantity);
            if (quantity>0) {
                var stockTakeLine = this.getStockTakeLine(line);
                var changes = {};
                changes.quantity = quantity;
                changes.variance = quantity - stockTakeLine.systemQuantity;
                this.updateStockTakeLine(line,changes);
            }
            else {
                this.removeStockTakeLine(line);
            }
        };
        //example utility funcs
        stockTakeModel.hasNSBI = function() {
            return _.some(this.stockTakeLines, function(v) {
                return v.nsbiQuantity > 0
            });
        };
        stockTakeModel.saveStockTake = function() {
            this.set("status","SAVED");
            this.saveModel(this.saveURL,"stockTakeData",this.onSave);
        };
        stockTakeModel.processStockTake = function() {
            this.set("status","COMPLETED");
            this.saveModel(this.saveURL,"stockTakeData",this.onSave);
        };
        stockTakeModel.loadStockTake = function(data) {
            var that = this;
            this.set('id',data.id);
            this.set('status',data.status);
            $.each(data.stockTakeLines,function(k,v) {
                that.loadStockTakeLine(v);
            });
        };
        stockTakeModel.onSave = function(msg) {
            window.onbeforeunload = null;
            window.location = msg.open;
        };

        return stockTakeModel;
    };

}( window.br = window.br || {}, jQuery, _ ));