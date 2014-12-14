(function( br, $, _, undefined ) {
    br.select2Refresh_SalesAnalysis = function(
        pageNum, category, brand, startDate, endDate, chkTrueGP, product, store, salesPeople, sortTypes) {
//        pageNum, category, brand, startDate, endDate, sortTypes, chkTrueGP, product, salesPeople) {
        var search = br.search({
            ajaxLoader: "<div class='offset2 col-6' style='text-align:center;margin-top:20px;'> <img src='{{ STATIC_URL }}img/ajax-loader.gif' /> </div>"
        });
        console.log("select2Refresh_SalesAnalysis");
        search.addEntity("Entities",{
            prepend: "",
            html: "Entity",
            human: "Products"
        });
        search.addQuerySet("Entities",{
            name:'All',
            prepend:"",
            parameters: {
                page: pageNum,
                category:category,
                brand: brand,
                startDate: startDate,
                endDate: endDate,
                sortTypes:sortTypes,
                chkTrueGP: chkTrueGP,
                product: product,
                store: store,
                salesPeople: salesPeople
            }
        });
        search.addPagination("Entities","All",'page',$('#resultsDiv'));

        var brands = search.getParameter("Entities","All","brand").split(",");
        $('#searchBrand').select2('val',brands);
        var products = search.getParameter("Entities","All","product").split(",");
        $('#searchBrand2').select2('val',products);




        var salesPeople = search.getParameter("Entities","All","salesPeople").split(",");
        $('#searchsalesPeople').select2('val',salesPeople);



        var categories = search.getParameter("Entities","All","category").split(",");
        $('#searchCategory').select2('val',categories);


        var stores = search.getParameter("Entities","All","store").split(",");
        $('#searchStore').select2('val',stores);


        var sortTypes = search.getParameter("Entities","All","sortTypes").split(",");
        $('#sortTypes').select2('val',sortTypes);




        var startDate = search.getParameter("Entities","All","startDate").split(",");
        $('#ui-datepicker').val(startDate[0]);
        var endDate = search.getParameter("Entities","All","endDate").split(",");
        $('#ui-datepicker-2').val(endDate[0]);


        var chkTrueGP = search.getParameter("Entities","All","chkTrueGP").split(",");
        if (_.contains(chkTrueGP,'trueGP')) {
            $('input[value=trueGP]').iCheck('check');
        }





    };
}( window.br = window.br || {}, jQuery, _ ));