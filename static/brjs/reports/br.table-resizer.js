(function( br, $, _, undefined ) {
    br.tableResizer = function(viewType) {
//        console.log("adee.macdowell@gmail.comx");
        var calcDataTableHeight = function() {
            return $(window).height()*45/100;
        };
        $(window).resize(function () {
            var oSettings = oTable.fnSettings();
            oSettings.oScroll.sY = calcDataTableHeight();
            oTable.fnDraw();
            });
        var windowHeight = $(window).height();
        var windowWidth = $(window).width();
        var intWindowHeight = parseInt(windowHeight);
        var intWindowWidth = parseInt(windowWidth);
        var sScrollX; //set x-scroll width
        if(viewType=="isSalesAnalysisView"){
            sScrollX = "100%";
//            console.log("issale");
        }
        else if(viewType=="isItemisedView"){
            sScrollX = "1555px";
//            console.log("isItem");
        }
        else{
            sScrollX = "100%";
//            console.log("isNone");
        }
        if(intWindowHeight>993){  //set y-scroll height
            sScrollY = "710px"
        }
        else{
            if(intWindowHeight>923 && intWindowHeight < 994){
                sScrollY = "640px"
            }
            else{
                if(intWindowHeight>641 && intWindowHeight < 924){
                    sScrollY = "360px"
                }
                else{
                    sScrollY = calcDataTableHeight()
                }
            }
        }
        //alert(window.screen.width+"x"+window.screen.height + "BROWSER-height:" + windowHeight + "wid:" + windowWidth);
        var oTable = $('#example').dataTable(
        {
            "sScrollX": '2222px',
            "sScrollX": sScrollX,
            "sScrollXInner": '2222px',
            "sScrollXInner": sScrollX,
            "bScrollCollapse": true,
            "bPaginate": false,
            "bFilter": false,
            "bSort": false,
            "sScrollY": sScrollY

        } );



        new FixedColumns( oTable,
        {
            "sHeightMatch": "none"
        } );


        return true;
    };
}( window.br = window.br || {}, jQuery, _ ));