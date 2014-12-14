//Adding New Functionality to br.base
(function( br, $, _, undefined ) {
    var lineTableDefaults = {
        totals: [{title: 'Total Invoice Inc. GST',key :"totalInv",value: 0.00}],
        headers: [{title: "#",key: 'quantity'},{title: "Description",key: 'description'},{title: "Total",key: 'total'}],
        tableClass: "table table-bordered",
        itemClass: "item",
        totalClass: "success",
        emptyText: "Please add entities using option above",
        rowTemplate: _.template('<tr class="item"><% _.each(values, function (v) { %><td><%= v %></td><%  }); %></tr>'),
        identifier: 'line', //used for identification of lines, can be id etc etc
        rowBindingFunction: function(elem) {
            return elem;
        },
        rowUnBindingFunction: function(elem) {
            return elem;
        }
    };
    //Public Method
    br.lineTableWidget = function(options,models) { // can optionally accept an existing invoiceModel
        var lineTable = {
            items: {}, //this is in the format identifer: {model:modelObject,element:rowElement} initialized from models
            tableElement: {},
            initialize: function(options,models) {
                var that= this;
                var endOptions = _.extend({},lineTableDefaults, options);
                $.each(endOptions,function(k,v){
                   that[k] = v;
                });
                _.each(models,function(addModel){
                    var Obj = {}; //only add the keys we need from the collection used to initialize this Widget
                    _.each(that.headers,function(header){
                        var get = header.key;
                        Obj[get] = addModel[get];
                    });
                    if(that.items[addModel[that.identifier]]==undefined) {that.items[addModel[that.identifier]]={};}
                    that.items[addModel[that.identifier]]['model'] = Obj;
                });
                //render the rows
                this.renderAllItemRows();
                this.renderAllTotalRows();
                this.generateTableElement();
                return this;
            },
            addItem: function(addModel) {
                var wasEmpty = this.isEmpty();
                var that = this;
                var Obj = {}; //only add the keys we need from the collection used to initialize this Widget

                if (_.has(that.items,addModel[that.identifier])){ return this; } //don't add duplicates

                _.each(that.headers,function(header){
                    var get = header.key;
                    if (addModel[get]!=undefined) {
                        Obj[get] = addModel[get];
                    }
                    else {
                        Obj[get] = "";
                    }
                });
                if(that.items[addModel[that.identifier]]==undefined) {that.items[addModel[that.identifier]]={};}
                that.items[addModel[that.identifier]]['model'] = Obj;
                var generatedElement = this.renderItemRow(addModel[that.identifier]);
                that.items[addModel[that.identifier]]['element'] = generatedElement;

                if (wasEmpty) {
                    this.tableElement.find('tr.danger').remove();
                    this.tableElement.find('tr.success').first().before(generatedElement);
                }
                else {
                    this.tableElement.find('tr.item').last().after(generatedElement);
                }
            },
            changeItem: function(identifer,newval) {
                var item = this.items[identifer];
                item.model = newval;
                var rowElement = item.element;
                var newRowElement = this.renderItemRow(identifer);
                this.rowUnBindingFunction(rowElement).replaceWith(newRowElement);
                item.element = newRowElement;
            },
            changeTotal: function(totalKey,newVal) {
                var total = _.findWhere(this.totals,{key:totalKey})
                var rowElement = total.element
                var key = _.indexOf(this.totals,total);
                this.totals[key].value = newVal;
                var newRowElement = this.renderTotalRow(key);
                rowElement.replaceWith(newRowElement);
                this.totals[key].element = newRowElement;
            },
            generateTableElement: function() {
                var that = this;
                var tableElement = $('<table class="'+this.tableClass+'"></table>');

                var headElement = $('<thead></thead>');
                var headRowElement = $('<tr></tr>');
                _.each(this.headers,function(v){
                    var headcol = $('<th>'+ v.title + '</th>');
                    headcol.appendTo(headRowElement);
                });
                headRowElement.appendTo(headElement.appendTo(tableElement));
                if(!this.isEmpty()) {
                    $.each(this.items,function(k,v) {
                        v.element.appendTo(tableElement);
                    });
                }
                else {
                    this.renderEmptyRow().appendTo(tableElement);
                }
                $.each(this.totals,function(k,v){
                    v.element.appendTo(tableElement)
                });
                this.tableElement = tableElement;
                return this;
            },
            isEmpty: function() {
                return (_.isEmpty(this.items));
            },
            removeItem: function(identifer) {
                var item = this.items[identifer];
                item.element.remove();
                delete this.items[identifer];
                if(this.isEmpty()) {
                    this.tableElement.find('tr.success').first().before(this.renderEmptyRow());
                }
            },
            renderTotalRow: function(key) {
                var numheaders = this.headers.length;
                var v = this.totals[key];
                var totalRow = $('<tr class="'+this.totalClass+'"></tr>');
                for(var i=0;i<numheaders;i++){
                    var html;
                    if (i==1) { html = $('<td>'+ v.title +'</td>'); } //display total title
                    else if(i==numheaders-1) { html = $('<td>'+ v.value +'</td>'); }
                    else { html = $('<td></td>'); }
                    html.appendTo(totalRow)
                }
                return totalRow;
            },
            renderEmptyRow: function() {
                var numheaders = this.headers.length;
                var emptyRow = $('<tr class="danger"></tr>');
                for(var i=0;i<numheaders;i++){
                    var html;
                    if (i==1) { html = $('<td>'+ this.emptyText +'</td>'); } //display total title
                    else { html = $('<td></td>'); }
                    html.appendTo(emptyRow)
                }
                return emptyRow;
            },
            renderItemRow: function(id) {
                var model = this.items[id].model;
                var element = $(this.rowTemplate({values:model}));
                element.data(this.identifier,id);
                element = this.rowBindingFunction(element);
                return element;
            },
            renderAllItemRows: function() {
                var that = this;
                $.each(this.items,function(k,v) {
                    v.element = that.renderItemRow(k);
                });
                return this;
            },
            renderAllTotalRows: function() {
                var that = this;
                $.each(this.totals,function(k,v) {
                    v.element = that.renderTotalRow(k);
                });
                return this;
            }
        }
        return lineTable.initialize(options,models);
    };
}( window.br = window.br || {}, jQuery, _ ));
//
//var linesTable = br.lineTableWidget({},[
//    {
//        line:1,
//        quantity: 2,
//        description: "Hey there Stupids",
//        total: 13
//    },
//    {
//        line:2,
//        quantity: 2,
//        description: "Hey there Stupids",
//        total: 13
//    },
//    {
//        line:3,
//        quantity: 1,
//        description: "Meow HOOOO",
//        total: 13
//    }
//])