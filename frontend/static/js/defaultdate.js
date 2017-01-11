window.onload = function() {
    var today = new Date();
    var dd = today.getDate()+1; // I want ending of file search is tomorrow
    var mm = today.getMonth()+1; //January is 0!
    var yyyy = today.getFullYear();
    var lastyear = new Date(yyyy, mm - 1, dd);
    lastyear.setMonth(lastyear.getMonth() - 1);
    var lm = lastyear.getMonth() + 1;
    var ly = lastyear.getFullYear();

    if(dd<10) {
        dd='0'+dd;
    }

    if(mm < 10) {
        mm = '0'+ mm;
    }

    if (lm < 10) {
        lm = '0' + lm;
    }


    today = yyyy+'/'+mm+'/'+dd;
    today = today + " 00:00";
    lastyear = ly + '/' + lm + '/' + dd+ " 00:00";



    jQuery(function(){
        jQuery('#datetimepicker').datetimepicker();
        jQuery('#datetimepicker').datetimepicker({value:lastyear});
        jQuery('#datetimepicker2').datetimepicker();
        jQuery('#datetimepicker2').datetimepicker({value:today});
    });
}