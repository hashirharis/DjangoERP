(function( br, $, _, undefined ) {

    var createEntityModal = '<div class="modal fade" id="add<%= html %>">\
                                 <div class="modal-dialog">\
                                    <div class="modal-content">\
                                        <div class="modal-header">\
                                            <button class="close" data-dismiss="modal">×</button>\
                                            <h3>Add <%= human %></h3>\
                                        </div>\
                                        <div class="modal-body addEntityModalContent">\
                                            <%= form %>\
                                        </div>\
                                        <div class="modal-footer">\
                                            <button id="addEntityConfirmButton" class="btn btn-primary">Add <%= human %></button>\
                                            <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>\
                                        </div>\
                                    </div>\
                                </div>\
                            </div>';
    var updateEntityModal = '<div class="modal fade" id="edit<%= html %>">\
                                <div class="modal-dialog">\
                                    <div class="modal-content">\
                                        <div class="modal-header">\
                                            <button class="close" data-dismiss="modal">×</button>\
                                            <h3 id="editEntityLabel">Edit <%= human %></h3>\
                                        </div>\
                                        <div class="modal-body editEntityModalContent">\
                                        </div>\
                                        <div class="modal-footer">\
                                            <button id="editEntityConfirmButton" class="btn btn-primary">Update <%= human %></button>\
                                            <button class="btn" data-dismiss="modal">Close</button>\
                                        </div>\
                                    </div>\
                                </div>\
                            </div>';
    var viewEntityModal =   '<div class="modal fade" id="view<%= html %>">\
                                <div class="modal-dialog">\
                                    <div class="modal-content">\
                                        <div class="modal-header">\
                                            <button class="close" data-dismiss="modal">×</button>\
                                            <h3 id="view<%= html %>Label">View <%= human %></h3>\
                                        </div>\
                                        <div class="modal-body viewEntityModalContent">\
                                        </div>\
                                        <div class="modal-footer">\
                                            <button class="btn" data-dismiss="modal">Close</button>\
                                        </div>\
                                    </div>\
                                </div>\
                            </div>';

	br.globalVar = 2;
 	br.search = function(model) {
 		var defaults = {
            format: "get",
            entities : {},
            autoSubmit: true,//this is to determine whether the form will be submitted automatically after a parameter change
            ajaxLoader: "",
            searchURL:"",
            csrfToken:""
        };
        var searchModel = _.extend({},defaults,model);

         var createModal = function(entity,action,form) {
             if (!_.has(searchModel.entities,entity)) {
                 return;
             }
             else {
                 var human = searchModel.entities[entity].human;
                 var html = searchModel.entities[entity].html;
             }
             var params = {
                 form: form,
                 html: html,
                 human: human
             };
             var modal = undefined;
             if (action=="create") { modal = $(_.template(createEntityModal,params));}
             else if (action=="update"){ modal = $(_.template(updateEntityModal,params)); }
             else if (action=="view"){ modal = $(_.template(viewEntityModal,params)); }
             $('.content').append(modal);
             return modal;
         };

         var post_to_url = function(params) {
             // The rest of this code assumes you are not using a library.
             // It can be made less wordy if you use one.
             var form = $('<form></form>');
             form.attr("method", searchModel.format);
             form.attr("action", searchModel.searchURL);

             if (searchModel.format == "post"||searchModel.format == "POST") {
                form.append($(searchModel.csrfToken));
             }

             for(var key in params) {
                 if(params.hasOwnProperty(key)) {
                     var hiddenField = $('<input></input>')
                     hiddenField.attr("type", "hidden");
                     hiddenField.attr("name", key);
                     hiddenField.attr("value", params[key]);
                     form.append(hiddenField);
                 }
             }

             $('body').append(form);
             form.submit();
         };

        searchModel.addEntity = function(name,entityObj) {
            /*
                search.addEntity(name,{
                    human: "Class Vendor Bonus",
                    html: "ClassVendorBonus",
                    prepend: "classVendorBonus"
                })
            */
            this.entities[name] = entityObj;
        };

        searchModel.addQuerySet = function(entity,querySetObj){
            /**
                search.addQuerySet("Model",{
                    name:'all',
                    parameters: {
                        q: currentValue
                    }
                });
             */
            if (this.entities[entity].querysets===undefined) {
                this.entities[entity].querysets = [];
            }
            this.entities[entity].querysets.push(querySetObj);
            return this;
        };

        searchModel.addCreate = function(entity,obj) {
            /*
             search.addCreateModal("entity",{
                    button: $(''),//jQuery selector
                    form: "<form></form",//element
                })
             */

            //should have button and form elements
            var modal = createModal(entity,'create',obj.form);

            obj.button.click(function(e){
                modal.modal('show');
            });

            modal.on('shown.bs.modal', function() {
                modal.find('input[type!="hidden"], select').first().focus();
            });

            modal.find('#addEntityConfirmButton').click(function(){
                modal.find('#createEntityForm').submit();
            });

            var processCreateEntityJson = function(data) {
                var createEntityForm = modal.find('#createEntityForm');
                // 'data' is the json object returned from the server
                if(data.errors!=undefined) {
                    jQuery.each(data.errors, function(key,val) {
                        var errorInput = createEntityForm.find("#id_"+key);
                        errorInput.parents('.control-group').addClass('error');
                        errorInput.parents('.controls').append('<span id="error_id_'+key+'" class="help-inline">' + val + '</span>')
                    });
                }
                else {
                    //customer added
                    modal.modal('hide');
                    if (searchModel.autoSubmit) {searchModel.submitPage();}
                }
            };

            modal.find('#createEntityForm').ajaxForm({
                dataType:  'json',
                success:   processCreateEntityJson
            });

            return this;
        };

        searchModel.addUpdate = function(entity,obj) {
            /*
             search.addUpdateModal("entity",{
                button: $(''),//jQuery selector
                url: //update URL to request (this can will have the default id of 0 appended to the end)
                attribute: //attribute for id, defaults to id
             })
             */

            var modal = createModal(entity,'update');
            var modalContent = modal.find('.editEntityModalContent');

            modal.on('shown.bs.modal', function() {
                modal.find('input[type!="hidden"], select').first().focus();
            });

            modal.find('#editEntityConfirmButton').click(function() {
                modal.find('#editEntityForm').submit();
            });

            var processEditEntityJson = function(data) {
                var editEntityForm = modalContent.find('#editEntityForm');
                // 'data' is the json object returned from the server
                if(data.errors!=undefined) {
                    jQuery.each(data.errors, function(key,val) {
                        var errorInput = editEntityForm.find("#id_"+key);
                        errorInput.parents('.control-group').addClass('error');
                        errorInput.parents('.controls').append('<span id="error_id_'+key+'" class="help-inline">' + val + '</span>');
                    });
                }
                else {
                    //customer added
                    modal.modal('hide');
                    if (searchModel.autoSubmit) {searchModel.submitPage();}
                }
            };

            obj.button.click(function(e){
                var attribute = obj.attribute;
                if(attribute==undefined) {
                    attribute = "data-id";
                }
                var id = $(this).attr(attribute);
                var url = obj.url;
                url = url.substring(0,url.length-1) + id;

                var request = $.ajax({
                    url: url,
                    type: "GET",
                    dataType: "html",
                    beforeSend: function(xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", br.getCookie('csrftoken'));
                        modal.modal('show');
                        modalContent.html(this.ajaxLoader);
                    }
                });

                request.done(function(msg) {
                    modalContent.html(msg);
                    modal.find('#editEntityForm').ajaxForm({
                        dataType:  'json',
                        success:   processEditEntityJson
                    });
                });

            });
            return this;
        };

         searchModel.addRead = function(entity,obj) {
             /*
              search.addCreateModal("entity",{
                  button: $(''),//jQuery selector
                  url: //update URL to request (this can will have the default id of 0 appended to the end)
                  attribute: //attribute for id, defaults to id
              })
              */

             var modal =  createModal(entity,'view');
             var modalContent = modal.find('.viewEntityModalContent');

             obj.button.click(function(e){
                 var attribute = obj.attribute;
                 if(attribute==undefined) {
                     attribute = "data-id";
                 }
                 var id = $(this).attr(attribute);
                 var url = obj.url;
                 url = url.substring(0,url.length-1) + id;

                 var request = $.ajax({
                     url: url,
                     type: "GET",
                     dataType: "html",
                     beforeSend: function(xhr, settings) {
                         xhr.setRequestHeader("X-CSRFToken", br.getCookie('csrftoken'));
                         modal.modal('show');
                         modalContent.html(this.ajaxLoader);
                     }
                 });

                 request.done(function(msg) {
                     modalContent.html(msg);
                 });
             });

         };

        searchModel.addDelete = function(entity,obj) {
            /*
             search.addDelete("entity",{
                 deleteButton: $(''),//jQuery selector
                 deleteURL: //update URL to request (this can will have the default id of 0 appended to the end)
                 attribute: //attribute for id, defaults to id
             })
             */

            if (!_.has(this.entities,entity)) {
                return;
            }

            obj.button.click(function(e){
                if(!confirm("Are you sure you want to do this?")){return;}
                var attribute = obj.attribute;
                if(attribute==undefined) {
                    attribute = "data-id";
                }
                var id = $(this).attr(attribute);
                var url = obj.url;
                url = url.substring(0,url.length-1) + id;

                var request = $.ajax({
                    url: url,
                    type: "POST",
                    dataType: "json",
                    beforeSend: function(xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", br.getCookie('csrftoken'));
                    }
                });

                request.done(function(msg) {
                    if(msg.success) {
                        if (searchModel.autoSubmit) {searchModel.submitPage();}
                    }
                    else {
                        alert(msg.error);
                    }
                });
            });
        };

        searchModel.changeParameter = function(entity,queryset,param,newVal) {
            /** search.changeParameter("Model","QuerySet","Start",new Date()); //refresh page if automatic**/
            if (!_.has(this.entities,entity)) {
                return;
            }
            var querySet = _.findWhere(this.entities[entity].querysets,{name:queryset});
            if (_.isUndefined(querySet)) {
                alert("There is no queryset of that name!");
                return;
            }
            if (_.isUndefined(querySet.parameters[param])){
                alert("No Parameters of that name were initialized!");
                return;
            }
            querySet.parameters[param] = newVal;
            if (this.autoSubmit) {this.submitPage();}
        };

        searchModel.getParameter = function(entity,queryset,param) {
             /** search.changeParameter("Model","QuerySet","Start",new Date()); //refresh page if automatic**/
             if (!_.has(this.entities,entity)) {
                 return;
             }
             var querySet = _.findWhere(this.entities[entity].querysets,{name:queryset});
             if (_.isUndefined(querySet)) {
                 alert("There is no queryset of that name!");
                 return;
             }
             if (_.isUndefined(querySet.parameters[param])){
                 alert("No Parameters of that name were initialized!");
                 return;
             }
             return querySet.parameters[param];
        };

        searchModel.submitPage = function() {
            /**
             * this should append the entityname+queryset+paramter name to the post request and then send it.
             */
            var postParams = {};
            _.each(this.entities,function(e){
                var entityPrepend = e.prepend;
                _.each(e.querysets,function(q){
                    var querysetPrepend = q.prepend;
                    $.each(q.parameters,function(ParamKey,ParamValue) {
                        var key = entityPrepend+querysetPrepend+ParamKey;
                        postParams[key] = ParamValue;
                    });
                });
            });

            //console.log(postParams);
            post_to_url(postParams);
        };

        searchModel.addPagination = function(entity,queryset,param,element) {
            /**
             * binds the paging div to the queryset parameter
             */
            element.find('.pagination a').click(function() {
                var link = $(this);
                if(link.closest('li').hasClass('disabled')) { return;}
                var pageNum = link.attr("page");
                searchModel.changeParameter(entity,queryset,param,pageNum);
                this.submitPage();
            });
        };

        return searchModel;
    };

}( window.br = window.br || {}, jQuery, _ ));