//(function( br, $, _, undefined ) {
//    br.select2refresh_itemisedReport = function(
//        startDate, endDate) {
//        console.log("select2refresh_itemisedReport");
//        var search = br.search({
//            ajaxLoader: "<div class='offset2 col-6' style='text-align:center;margin-top:20px;'> <img src='{{ STATIC_URL }}img/ajax-loader.gif' /> </div>"
//        });
//        search.addEntity("Entities",{
//            prepend: "",
//            html: "Entity",
//            human: "Products"
//        });
//        search.addQuerySet("Entities",{
//            name:'All',
//            prepend:"",
//            parameters: {
//                page: 'none',
//                startDate: startDate,
//                endDate: endDate
////                chkTrueGP: chkTrueGP
//            }
//        });
//        search.addPagination("Entities","All",'page',$('#resultsDiv'));
//        var startDate = search.getParameter("Entities","All","startDate").split(",");
//        $('#ui-datepicker').val(startDate[0]);
//        var endDate = search.getParameter("Entities","All","endDate").split(",");
//        $('#ui-datepicker-2').val(endDate[0]);
////        var chkTrueGP = search.getParameter("Entities","All","chkTrueGP").split(",");
////        if (_.contains(chkTrueGP,'trueGP')) {
////            $('input[value=trueGP]').iCheck('check');
////        }
//    };
//}( window.br = window.br || {}, jQuery, _ ));

(function( br, $, _, undefined ) {
    br.select2refresh_itemisedReport = function() {
        console.log("select2refresh_itemisedReport");
    };
}( window.br = window.br || {}, jQuery, _ ));