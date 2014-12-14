(function( br, $, _, undefined ) {
    var ProfitMarginCalcHTML = '\
    <div class="modal fade" id="ProfitMarginCalculator">\
        <div class="modal-dialog">\
            <div class="modal-content">\
                <div class="modal-header">\
                    <button class="close" data-dismiss="modal">×</button>\
                    <h3>Price Check</h3>\
                </div>\
                <div class="modal-body">\
                    <table class="table table-bordered">\
                        <tbody>\
                            <tr>\
                                <td><%= salePriceLabel %></td>\
                                <td>\
                                <div class="input-prepend input-append">\
                                    <span class="add-on">$</span>\
                                    <input id="dollars" value="500" class="span1" size="8" type="text">\
                                        <span class="add-on">.</span>\
                                        <input id="cents" value="00" class="span1" size="2" type="text">\
                                </div>\
                                </td>\
                            </tr>\
                            <tr>\
                                <td><%= costPriceLabel %></td>\
                                <td>\
                                    <div class="input-prepend">\
                                        <span class="add-on">$</span>\
                                        <input id="costPrice" class="span2" value="400" type="text">\
                                    </div>\
                                </td>\
                            </tr>\
                            <tr class="success">\
                                <td><%= marginLabel %></td>\
                                <td>\
                                    <div class="input-append">\
                                        <input id="percent" class="span1" size="8" type="text" value="20">\
                                            <span class="add-on">%</span>\
                                        </div>\
                                    </td>\
                            </tr>\
                        </tbody>\
                    </table>\
                </div>\
                <div class="modal-footer">\
                    <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>\
                    <button id="saveChanges" class="btn btn-primary">Save changes</button>\
                </div>\
            </div>\
        </div>\
    </div>';

    var MarginCalculatorDefaults = {
        costPriceLabel: "Net Price",
        costPrice:0,
        salePriceLabel: "Sale Price",
        salePrice:0,
        marginLabel: "Profit",
        returnValue: 'salePrice', //this can be changed to return cost or margin.
        callback : function(salePrice) {
            console.log(salePrice);
        }
    };

    br.marginCalculator = function(options) {
        options = _.extend({},MarginCalculatorDefaults,options);

        var CalcModalWindow = $(_.template(ProfitMarginCalcHTML,options))
        var CalcCostPriceInput = CalcModalWindow.find('input#costPrice');
        var CalcDollarsInput = CalcModalWindow.find('input#dollars');
        var CalcCentsInput = CalcModalWindow.find('input#cents');
        var CalcProfitInput = CalcModalWindow.find('input#percent');
        var CalcSaveChangesButton = CalcModalWindow.find('button#saveChanges');

        var profit = ((options.salePrice - options.costPrice)/options.costPrice * 100).toFixed(2);
        var dollarsAmount = Math.floor(options.salePrice);
        var centsAmount = Math.floor((options.salePrice - dollarsAmount) * 100);
        var returnFunction = options.callback;

        CalcCostPriceInput.val(options.costPrice);
        CalcDollarsInput.val(dollarsAmount);
        CalcCentsInput.val(pad(centsAmount,2));
        CalcProfitInput.val(profit);

        var closeCalculator = function(e) {
            var returnVal = parseFloat(CalcDollarsInput.val()) + parseFloat(CalcCentsInput.val())/100;
            CalcModalWindow.modal('hide');
            returnFunction(returnVal);
            CalcModalWindow.remove();
        }

        var reCalculatePrice = function(e) {
            var salePrice = parseFloat(CalcDollarsInput.val()) + parseFloat(CalcCentsInput.val())/100;
            var costPrice = parseFloat(CalcCostPriceInput.val());

            var profit = ((salePrice - costPrice)/costPrice * 100).toFixed(2);

            CalcProfitInput.val(profit);
        };

        var reCalculatePercent = function(e) {
            var profit = parseFloat(CalcProfitInput.val());
            var costPrice = parseFloat(CalcCostPriceInput.val());

            var salePrice = profit/100 * costPrice + costPrice;

            var dollarsAmount = Math.floor(salePrice);
            var centsAmount = Math.floor((salePrice - dollarsAmount) * 100);

            CalcDollarsInput.val(dollarsAmount);
            CalcCentsInput.val(pad(centsAmount,2));
        };

        CalcCostPriceInput.on('change', reCalculatePrice);
        CalcDollarsInput.on('change',reCalculatePrice);
        CalcCentsInput.on('change', reCalculatePrice);
        CalcProfitInput.on('change', reCalculatePercent);
        CalcSaveChangesButton.on('click', closeCalculator);

        CalcModalWindow.on('hidden.bs.modal', function () { // when closing the breakdown window show the calculator again.
            CalcModalWindow.remove();
        });

        function pad(num, size) { // for leading zeroes
            var s = num+"";
            while (s.length < size) s = "0" + s;
            return s;
        };

        $('.content').append(CalcModalWindow);
        CalcModalWindow.modal('show');
    }
}( window.br = window.br || {}, jQuery, _ ));

