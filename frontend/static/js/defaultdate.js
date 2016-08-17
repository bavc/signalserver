var today = new Date();
var dd = today.getDate();
var mm = today.getMonth()+1; //January is 0!
var yyyy = today.getFullYear();
var tomorrow = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
var td = tomorrow.getDate();
var tm = tomorrow.getMonth()+1;

    if(dd<10) {
        dd='0'+dd;
    }
    if(td<10) {
        td='0'+td;
    }
    if(mm<10) {
        mm='0'+ mm;
    }
    if(tm<10) {
        tm='0'+ tm;
    }


    endday = yyyy+'/'+tm+'/'+td;
    endday = endday + " 00:00";
    lastyear = (yyyy - 1) + '/' + mm + '/' + dd + " 00:00";



    jQuery(function(){
    jQuery('#datetimepicker').datetimepicker();
    jQuery('#datetimepicker').datetimepicker({value:lastyear});
    jQuery('#datetimepicker2').datetimepicker();
    jQuery('#datetimepicker2').datetimepicker({value:endday});
    });