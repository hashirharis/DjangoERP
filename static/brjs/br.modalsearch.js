(function( br, $, _, undefined ) {
    var GenericModalSearchHTML = '<div class="modal fade" id="<%= id %>">\
                    <div class="modal-dialog">\
                        <div class="modal-content">\
                            <div class="modal-header">\
                                <button class="close" data-dismiss="modal">×</button>\
                                <h3 id="<%= label %>"><%= title %></h3>\
                            </div>\
                            <div class="modal-body">\
                                <div class="row">\
                                    <div class="input-group">\
                                        <input class="genericSearchModalInput form-control" type="text" placeholder="<%= placeholder %>">\
                                        <span class="input-group-btn">\
                                            <button class="btn btn-primary genericSearchModalSearch">Search!</button>\
                                        </span>\
                                    </div>\
                                    <div class="col-12" style="height:20px"></div>\
                                    <div class="genericSearchModalResultDiv">\
                                    </div>\
                                </div>\
                                <div class="modal-footer">\
                                    <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>\
                                </div>\
                            </div>\
                        </div>\
                    </div>';

    var genericModalSearchDefaults = {
        entity:"Entity",
        placeholder: "Enter Search Term Here",
        results: "text",
        postData: {}, //extra data to send
        element: undefined,
        ajaxLoader: "<div class='offset2 col-6' style='text-align:center;margin-top:20px;'> <img src='{{ STATIC_URL }}img/ajax-loader.gif' /> </div>",
        url:"",
        onAfter : function(elem) {
            return elem;
        },
        callback : function(item) {
            console.log(item);
        }
    };

    br.genericModalSearch = function(options) {
        var searchButtonID = 'genericSearchModalSearch';
        var inputID = 'genericSearchModalInput';
        var resultsDiv = 'genericSearchModalResultDiv';

        options = _.extend({},genericModalSearchDefaults,options);
        options['id'] = 'add' + options['entity'] + 'Modal';
        options['label'] = options['id'] + 'Label';
        options['title'] = 'Add ' + options['entity'];
        if (options.element!=undefined) {
            var modalWindow = options.element;
        }
        else {
            var modalWindow = $(_.template(GenericModalSearchHTML,options))
        }

        $('.content').append(modalWindow);

        var searchButton = modalWindow.find('.'+searchButtonID);
        var textBox = modalWindow.find('.'+inputID);
        var resultsDiv = modalWindow.find('.'+resultsDiv);

        searchButton.bind("click",function() {
            ajaxSearchAndReturn(options.url);
        });
        modalWindow.keybind('Enter',function() {
            ajaxSearchAndReturn(options.url);
        });
        modalWindow.on('shown.bs.modal', function() {
            textBox.focus();
        });

        var self = {};

        self.ajaxSearchAndReturn = function() {
            ajaxSearchAndReturn(options.url);
        }

        self.postData = options.postData;

        var ajaxSearchAndReturn = function(url) {
            if (textBox.val().length >1) {
                var ajaxLoader = options.ajaxLoader;
                var q = textBox.val();
                var postData = _.extend({q:q},options.postData);

                var request = $.ajax({
                    url: url,
                    type: "POST",
                    data: postData,
                    dataType: "html",
                    beforeSend: function(xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", br.getCookie('csrftoken'));
                        resultsDiv.html(ajaxLoader);
                        if (options.onAfter!=undefined) {
                            options.onAfter(modalWindow);
                        }
                    }
                });

                request.done(function(msg) {
                    resultsDiv.html( msg );
                    // Bind the events for the add X Entity Button.
                    modalWindow.find('.add'+options.entity).click(function() {
                        var myEntityRow = $(this).closest('tr');
                        var returnEntity = {}
                        $.each(myEntityRow.children('td'), function(k,v){
                            var td = $(v);
                            if (options.format=="text") {
                                var returnVal = td.text();
                            }
                            else{
                                var returnVal = td.html();
                            }
                            if(td.attr("class")==undefined) {
                                return;
                            }
                            else if(td.hasClass("hidden")) {
                                var key = ""
                                $.each(td.attr("class").split(" "),function() { //get first class that isn't named hidden
                                    if (this != "hidden") {key = this;return false;}
                                });
                                if (key!="") {
                                    returnEntity[key] = returnVal
                                }
                            }
                            else {
                                returnEntity[td.attr("class")] = returnVal;
                            }
                        });
                        $.each(myEntityRow.data(),function(k,v) {
                            returnEntity[k] = v;
                        });
                        modalWindow.modal("hide");
                        options.callback(returnEntity);
                    });
                });
                request.fail(function(jqXHR, textStatus) {
                    alert( "Request failed: " + textStatus );
                });
            }
        };

        self.element = $(modalWindow);

        return self;
    }
}( window.br = window.br || {}, jQuery, _ ));

