//Adding New Functionality to br.base
(function( br, $, _ ) {
    br.reconModel = function(model) {
    	if (model==undefined) { //default model instance
            model = {
                id: 0, //other vars
                status: "NEW",
                total: 0,
                distributor: 1,
                endDate: '',
                statementTotal: 0,
                selectedTotal:0,
                reconLines: [],
                reconLinesIndex: 1,
                saveURL: ''
            }
        }

        var reconModel = br.baseModel(model);

        reconModel.getReconLine = function(line) {
            var filter = {line:line};
            return this.getItem("reconLines", filter);
        };
        reconModel.addReconLineFromServer = function(item) {
            //sanitize some values
            var parsedObj = {
                debit: parseFloat(item.debit),
                credit: parseFloat(item.credit)
            };
            var newline = $.extend(true,item,parsedObj);
            this.addReconLine(newline);
        };
        reconModel.addReconLine = function(item) {
            var newline = $.extend(true,{line: this.reconLinesIndex, selected: false},item);
            this.addItem("reconLines", newline);
            this.reconLinesIndex++;
        };
        reconModel.removeReconLine = function(line) {
            var filter = {line:line};
            this.deleteItem("reconLines",filter);
        };
        reconModel.removeAllReconLines = function() {
            var that = this;
            for(var i = reconModel.reconLines.length-1; i>=0; i--) {
                that.removeReconLine(reconModel.reconLines[i].line);
            }
        };
        //updates entire line
        reconModel.changeReconLine = function(line, newline) {
            var filter = {line:line};
            this.updateItem("reconLines", filter, newline);
        };
        //update certain values
        reconModel.updateReconLine = function(line, newattributes) {
            var filter = {line:line};
            this.updateItemValues("reconLines", filter, newattributes);
        };
        reconModel.selectReconLine = function(line, selected) {
            var filter = {line:line};
            this.updateItemValues("reconLines", filter, {selected: selected});
        };
        reconModel.commentReconLine = function(line, text) {
            var filter = {line:line};
            this.updateItemValues("reconLines", filter, {comment: text});
        };
        reconModel.getSelectedTotals = function() {
            this.set('selectedTotal',_.reduce(this.reconLines, function(runningTotal, val) {
                if(!val.selected) {
                    return runningTotal;
                }
                if(val.credit>0) {
                    return runningTotal + val.credit;
                } else if(val.debit>0) {
                    return runningTotal - val.debit;
                }
            }, 0));
        }

        reconModel.validate = function() {
            if(this.reconLines.length<=0) {
                alert("There are no recon lines in this reconciliation, save failed.")
                return false
            }
            else if (this.selectedTotal === 0) {
                alert("No Recon Lines have been selected, save failed.")
                return false
            }
            else if(this.selectedTotal!==this.statementTotal) {
                if(!confirm("The Statement and selected Lines do not match, do you wish to proceed anyway ?")) {
                    return false;
                }
            }
            return true;
        }
        reconModel.saveReconModel = function() {
            if(this.validate()) {
                this.set("status", "COMPLETED");
                this.saveModel(this.saveURL,"reconData",this.onSave);
            }
        };
        reconModel.onSave = function(msg) {
            window.onbeforeunload = null;
            window.location = msg.open; //redirect to another location
        };

        return reconModel;
    };

}( window.br = window.br || {}, jQuery, _ ));