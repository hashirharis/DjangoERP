(function( br, $, _, undefined ) {
    //Private Property
    var LoginModalHTML =
        '<div class="modal fade" id="LoginBoxModal">\
            <div class="modal-dialog">\
                <div class="modal-content">\
                    <div class="modal-header">\
                        <button class="close" data-dismiss="modal">×</button>\
                        <h3>Login</h3>\
                    </div>\
                    <div class="modal-body">\
                        <div class="row">\
                            <form class="form-horizontal">\
                                <label class="control-label" for="LoginUsername">User</label>\
                                <div class="controls">\
                                    <input type="text" id="LoginUsername" placeholder="User">\
                                </div>\
                                <label class="control-label" for="LoginPassword">Password</label>\
                                    <div class="controls">\
                                        <input type="password" id="LoginPassword" placeholder="Password">\
                                    </div>\
                            </form>\
                        </div>\
                    </div>\
                    <div class="modal-footer">\
                        <button class="btn btn-success" id="LoginConfirm">Login</button>\
                        <button class="btn" data-dismiss="modal">Close</button>\
                    </div>\
                </div>\
            </div>\
        </div>';

    br.initLoginPrompt = function(staff) {
        var that = this;
        var modalWindow = $(LoginModalHTML);
        $('body').append(modalWindow);

        modalWindow.on('shown.bs.modal', function() {
            modalWindow.find('#LoginUsername').focus();
        });

        modalWindow.on('hide.bs.modal', function(e) {
            console.log("unbinding");
            modalWindow.find('#LoginConfirm').unbind('click');
            modalWindow.keyunbind('Enter');
            modalWindow.find('#LoginUsername').val("");
            modalWindow.find('#LoginPassword').val("")
        });

        var privelegeLevelNeeded = function(module) {
            var requiredPrivelege = 1;
            if (module=='Sale') {
                requiredPrivelege = 1;
            }
            else if(module=='PriceBook'||module=='Stock') {
                requiredPrivelege = 2;
            }
            else if(module=='Admin') {
                requiredPrivelege = 3;
            }
            else {
                requiredPrivelege = 6;
            }
            return requiredPrivelege;
        }

        this.prompt = function(module, callback) {
            var requiredPrivelege = privelegeLevelNeeded(module);
            modalWindow.modal('show');
            var login = function(e) {
                var name = modalWindow.find('#LoginUsername').val();
                var password = modalWindow.find('#LoginPassword').val();
                var user = _.findWhere(staff, {name:name,password:password});
                modalWindow.modal('hide');
                if (user==undefined) {
                    callback(false);
                    return
                }
                if(user.privelegeLevel>=requiredPrivelege) {
                    callback(true, user);
                } else {
                    modalWindow.modal('hide');
                    callback(false, user);
                }
            }
            modalWindow.find('#LoginConfirm').bind('click',login);
            modalWindow.keybind('Enter', login);
        }
        return this;
    };

}( window.br = window.br || {}, jQuery, _ ));