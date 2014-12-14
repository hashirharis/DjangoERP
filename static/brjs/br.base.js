(function( br, $, _, undefined ) {
    //Private Property
    var bindingModel = {
        bindings : {},
        bindEvents: function(eventsObj) {
            var that = this;
            _.each(eventsObj,function(v) {
                $.each(v,function(callbackevent,callbackfunction) {
                    that.bindEvent(k, callbackevent, callbackfunction);
                });
            });
            return this;
        },
        bindEvent: function(attribute,event,callback) {
            if (this.bindings[attribute]==undefined) { this.bindings[attribute] = {}; }
            if (this.bindings[attribute][event]==undefined) { this.bindings[attribute][event] = []; }
            this.bindings[attribute][event].push(callback);
            return this;
        },
        fireEvent: function(attribute,event,params) {
            var that = this;
            if (this.bindings[attribute]!=undefined&&this.bindings[attribute][event]!=undefined) {
                _.each(this.bindings[attribute][event],function(v) {
                    if(params===undefined) { v(that[attribute]); }
                    else { v(params); }
                });
            }
            return this;
        },
        bindCollectionToTable: function(tableView,collectionName) {
            this.bindEvent(collectionName,"added",function(item) {
                tableView.addItem(item);
            });
            this.bindEvent(collectionName,"deleted",function(item) {
                tableView.removeItem(item[tableView.identifier]);
            });
            this.bindEvent(collectionName,"changed",function(item) {
                tableView.changeItem(item[tableView.identifier],item);
            });
        },
        bindAttributeToControl: function(element,attribute,select2) {
            var select2 = typeof select2 !== 'undefined' ? select2 : false;
            var that = this;
            this.bindEvent(attribute,"updated",function(newVal) {
                if (select2) { //non select2 control
                    element.select2("val",newVal);
                }
                else {
                    element.val(newVal);
                }
            });
        },
        bindControlToAttribute: function(element,attribute,select2) {
            var select2 = typeof select2 !== 'undefined' ? select2 : false;
            var that = this;
            if (select2) { //non select2 control
                element.on("change",function(e) {
                    that.set(attribute,e.val);
                });
            }   else {
                element.change(function() {
                    that.set(attribute,element.val());
                });
            }
        },
        completeControlBind: function(element,attribute,select2) {
            var select2 = typeof select2 !== 'undefined' ? select2 : false;
            var that = this;
            if (select2) { //non select2 control
                element.on("change",function(e) {
                    that.set(attribute,e.val);
                });
            }
            else {
                element.change(function() {
                    that.set(attribute,element.val());
                });
            }
            this.bindEvent(attribute,"update",function(newVal) {
                if (select2) { //non select2 control
                    element.select2("val",newVal);
                }
                else {
                    element.val(newVal);
                }
            });
        },
        completeDateControlBind: function(element,attribute) {
            var that = this;
            element.change(function() {
                var date = new Date($(this).val());
                if (_.isNaN(date)){
                    alert("Please enter a valid date!");
                    return;
                }
                that.set(attribute,date.toISOString());
            });
            this.bindEvent(attribute,"update",function(val){
                var date = new Date(val);
                element.val(date);
            });
        },
        completeDatePickerControlBind: function(element,attribute) {
            var that = this;
            element.datepicker({
                dateFormat: 'dd/mm/yy',
                onSelect: function(dateText) {
                    var date = element.datepicker('getDate');
                    that.set(attribute, date.toISOString(), true);
                }
            });
            this.bindEvent(attribute,"update",function(val) {
                element.datepicker("setDate", new Date(val));
            });
        }
    };

    //Public Properties
    br.GST = 1.10;

    //Public Method
    br.baseModel = function(model) {
        var baseModel = {
            initialize: function(model) {
                var that = this;
                $.each(model,function(k,v) {
                    that.set(k,v);
                });
                return this;
            },
            set: function(key,value,suppress) {
                var suppress = typeof suppress !== 'undefined' ? suppress : false;
                if (_.has(this,key)) {
                    var oldVal = this[key];
                    this[key] = value;
                    if (oldVal != value && !suppress) {
                        this.fireEvent(key,"update");
                        this.fireEvent('all','update',true)
                    }
                }
                else {
                    this[key] = value;
                    if(!suppress) {
                        this.fireEvent(key,"create");
                    }
                }
                return this;
            },
            remove: function(key) {
                if (_.has(this,key)) {
                    delete this[key];
                    this.fireEvent(key,"delete")
                }
                return this;
            },
            //collection methods
            addItem: function(collectionName,obj) {
                this[collectionName].push(obj);
                this.fireEvent(collectionName,"added",obj);
                return this;
            },
            deleteItem: function(collectionName,keyOrFilters) {
                var key = this.keyFromKeyOrFilter(collectionName,keyOrFilters);
                var obj = this[collectionName][key];
                this[collectionName].splice(key,1);
                this.fireEvent(collectionName,"deleted",obj);
                return this;
            },
            updateItem: function(collectionName,keyOrFilter,obj) {
                var key = this.keyFromKeyOrFilter(collectionName,keyOrFilter);
                var oldObj = this[collectionName][key];
                if (!_.isEqual(oldObj, obj)) {
                    this[collectionName][key] = obj;
                    this.fireEvent(collectionName,"changed",obj);
                }
                return this;
            },
            getItem: function(collectionName,keyOrFilter) {
                var key = this.keyFromKeyOrFilter(collectionName,keyOrFilter);
                return this[collectionName][key];
            },
            updateItemValues: function(collectionName,keyOrFilter,keyVals,suppress) {
                var suppress = typeof suppress !== 'undefined' ? suppress : false;
                var key = this.keyFromKeyOrFilter(collectionName,keyOrFilter);
                var obj = this[collectionName][key];

                if(obj!==undefined) {
                    $.each(keyVals,function(k,v) {
                        obj[k] = v;
                    });
                    if(!suppress) {this.fireEvent(collectionName,"changed",obj);}
                }
                return this;
            },
            keyFromKeyOrFilter: function(collectionName,keyOrFilter) {
                if (_.isObject(keyOrFilter)) { //filters
                    var obj = _.findWhere(this[collectionName], keyOrFilter);
                    return _.indexOf(this[collectionName], obj);
                }
                else if (_.isNumber(keyOrFilter)) { //key
                    return keyOrFilter;
                }
            },
            saveModel: function(url,EntityName,callback) {
                var data = {};
                var toSend = $.extend(true,{},this);
                delete toSend['bindings'];
                data[EntityName] = JSON.stringify(toSend);
                var request = $.ajax({
                    url: url,
                    type: "POST",
                    data: data,
                    dataType: "json",
                    beforeSend: function(xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", br.getCookie('csrftoken'));
                    }
                });

                request.done(function(msg) {
                    console.log(callback);
                    if(callback!==undefined) {callback(msg);}
                    else{console.log("saved model.. " + EntityName);}
                });
            }
        };
        baseModel = _.extend({},baseModel,bindingModel);
        baseModel.initialize(model);
        return baseModel
    };

    br.viewNetBreakDown = function(id,url,ajaxLoader,modalWindow) {
        var BreakDownModalWindow = modalWindow;
        var BreakDownResultsDiv = modalWindow.find('#netBreakDownContent');

        var request = $.ajax({
            url: url,
            type: "POST",
            data: {id : id},
            dataType: "html",
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", br.getCookie('csrftoken'));
                BreakDownModalWindow.modal('show');
                BreakDownResultsDiv.html(ajaxLoader);
            }
        });

        request.done(function(msg) {
            BreakDownResultsDiv.html( msg );
        });
    };

    br.dateInputBinding = function(element) {
        var that = this;
        var initial = element.val();
        element.attr("placeholder","mm/dd/yyyy");
        element.change(function(e) {
            var date = new Date($(this).val());
            if (isNaN(date)){
                alert("Please enter a valid date!");
                element.val(initial);
            }
            else {
                initial = element.val();
            }
        });
    };

    /** we will use this everytime we are multiplying or dividing to get a proper rounded value to work with. **/
    Number.prototype.round = function(p) {
      p = p || 10;
      return parseFloat( this.toFixed(p) );
    };
}( window.br = window.br || {}, jQuery, _ ));