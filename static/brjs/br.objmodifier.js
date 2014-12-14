(function( br, $, _, undefined ) {
    var ObjModifierHTML = '\
    <div class="modal fade" id="changeAttribute" data-backdrop="false" data-keyboard="false">\
        <div class="modal-dialog">\
            <div class="modal-content">\
                <div class="modal-header">\
                    <h3><%= title %></h3>\
                </div>\
                <div class="modal-body">\
                    <table class="table table-bordered">\
                        <tbody>\
                        <% _.each(values, function(value){ %>\
                            <tr>\
                                <td><%= value.human %></td>\
                                <td>\
                                    <input name="<%= value.actual %>" value="<%= value.defaultVal %>" <% if (!value.editable) { %>disabled <% } %>class="values" size="<% if(_.has(value, "size")) { print(value.size); } %>" type="text">\
                                    <% if(_.has(value, "tip")) { %>\
                                        <br>\
                                        <small style="color:red;"><%= value.tip %></small>\
                                    <% } %>\
                                </td>\
                            </tr>\
                        <% }); %>\
                        </tbody>\
                    </table>\
                </div>\
                <div class="modal-footer">\
                    <button id="saveChanges" class="btn btn-primary">Save changes</button>\
                </div>\
            </div>\
        </div>\
    </div>';

    var ObjModifierDefaults = {
        object: {},
        values: [], //array of values to modify
        title: "Please enter some values",
        callback : function(newObj) {
            console.log(newObj);
        }
    };

    br.objModifier = function(options) {
        options = _.extend({},ObjModifierDefaults,options);

        var ObjModModal = $(_.template(ObjModifierHTML, options))
        var ValueInputs = ObjModModal.find('.values');
        var SaveChangesButton = ObjModModal.find('button#saveChanges');

        var returnFunction = options.callback;

        var closeModifier = function(e) {
            var returnVal = {}
            $.each(ValueInputs, function(k,v) {
                var attrName = $(v).attr('name');
                var attrValue = $(v).val();
                returnVal[attrName] = attrValue;
            });
            returnVal = _.extend({},options.object,returnVal);
            ObjModModal.modal('hide');
            returnFunction(returnVal);
        }

        ObjModModal.on('hidden.bs.modal',function(e) {
            ObjModModal.remove();
        });

        SaveChangesButton.on('click', closeModifier);
        ObjModModal.keybind('Enter',closeModifier);

        ObjModModal.on('shown.bs.modal', function() {
            ValueInputs.get(0).focus();
        });

        $('.content').append(ObjModModal);
        ObjModModal.modal('show');
    }
}( window.br = window.br || {}, jQuery, _ ));

