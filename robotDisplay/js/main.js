//to run this use 
// python3 -m pynetworktables2js --team 7468

var defaultOnce = true;

function onRobotConnection(connected) {
    $('#robotstate').text(connected ? "Connected!" : "Disconnected");
    $('#robotAddress').text(connected ? NetworkTables.getRobotAddress() : "disconnected");
    if(connected && defaultOnce){
        $( "#load-defaults" ).click();
        defaultOnce = false;
    }
   
}

$(document).ready(function(){
    NetworkTables.addRobotConnectionListener(onRobotConnection, true);
        
    attachRobotConnectionIndicator('#robotIndicator');
      
    // attaches the select element to a SendableChooser object
    attachSelectToSendableChooser("#autonomous", "Autonomous Mode");


    NetworkTables.addGlobalListener(function(key, value, isNew){
    // do something with the values as they change
        //console.log(key)
        if(key=="/SmartDashboard/Mytest"){
            console.log('we see it!')
            console.log(value)
        }else if(key=="/limelight/tx"){
            $("#limeTX").text(value.toFixed(2))
        }else if(key=="/limelight/ty"){
            $("#limeTY").text(value.toFixed(2))
        }

        else{
            console.log(key+"  "+value)
        }
    }, true);


    $( "#load-defaults" ).button();
    $( "#load-defaults" ).click(function( event ) {
        console.log('loading defaults');

        $( "#xScale-slider" ).slider('value', 0);
        $( "#yScale-slider" ).slider('value', 0);
        $( "#spinScale-slider" ).slider('value',0);
        $( "#trim-slider" ).slider('value',-.005);
        $( "#climb-slider" ).slider('value',0);

        $( "#intake-slider" ).slider('value',0);
        $( "#indexer-slider" ).slider('value',0);
        $( "#shooter-slider" ).slider('value',0);

        $( "#visionP-slider" ).slider('value',0.05);

        
        $("#intake-off").prop("checked",true).change();
        $("#indexer-off").prop("checked",true).change();
        $("#shooter-off").prop("checked",true).change();


    });

    $( "#drive-beginner" ).button();
    $( "#drive-beginner" ).click(function( event ) {
        console.log('loading defaults');
        $( "#xScale-slider" ).slider('value',.5);
        $( "#yScale-slider" ).slider('value',.2);
        $( "#spinScale-slider" ).slider('value',.2);
    });

    $( "#drive-advanced" ).button();
    $( "#drive-advanced" ).click(function( event ) {
        console.log('loading defaults');
        $( "#xScale-slider" ).slider('value',.5);
        $( "#yScale-slider" ).slider('value',.4);
        $( "#spinScale-slider" ).slider('value',.25);
    });


    $( "#drive-control" ).controlgroup();
    $( "#balls-control" ).controlgroup();
    $( "#vision-control" ).controlgroup();



    $( "#xScale-slider" ).slider({
        min: 0,
        max: 1,
        step: .05,
        value: 0,
        change: function( event, ui ) {
            console.log('see xslider: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/xScale",ui.value)
            $("#xScaleReal").text(parseInt(100*ui.value)+"%")
        }
    });
    $( "#yScale-slider" ).slider({
        min: 0,
        max: 1,
        step: .05,
        value: 0,
        change: function( event, ui ) {
            console.log('see yslider: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/yScale",ui.value)
            $("#yScaleReal").text(parseInt(100*ui.value)+"%")
        }
    });
    $( "#spinScale-slider" ).slider({
        min: 0,
        max: 1,
        step: .05,
        value: 0,
        change: function( event, ui ) {
            console.log('see yslider: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/spinScale",ui.value)
            $("#spinScaleReal").text(parseInt(100*ui.value)+"%")
        }
    });
    $( "#climb-slider" ).slider({
        min: 0,
        max: 1,
        step: .05,
        value: 0,
        change: function( event, ui ) {
            console.log('see climb: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/climbScale",ui.value)
            $("#climbReal").text(parseInt(100*ui.value)+"%")
        }
    });

    $( "#trim-slider" ).slider({
        min: -.015,
        max: .015,
        step: .001,
        value: -.005,
        change: function( event, ui ) {
            console.log('see trimslider: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/steeringTrim",ui.value)
            $("#trimReal").text(ui.value)
        }
    });

    $( "#indexer-slider" ).slider({
        min: 0,
        max: 1,
        step: .05,
        value: 0,
        change: function( event, ui ) {
            console.log('see indexer: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/indexerSpeed",ui.value)
            $("#indexerReal").text(parseInt(100*ui.value)+"%")
        }
    });

    $( "#intake-slider" ).slider({
        min: 0,
        max: 1,
        step: .05,
        value: 0,
        change: function( event, ui ) {
            console.log('see intake: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/intakeSpeed",ui.value)
            $("#intakeReal").text(parseInt(100*ui.value)+"%")
        }
    });
    $( "#shooter-slider" ).slider({
        min: 0,
        max: 1,
        step: .01,
        value: 0,
        change: function( event, ui ) {
            console.log('see shooter: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/shooterSpeed",ui.value)
            $("#shooterReal").text(parseInt(100*ui.value)+"%")
        }
    });

    $( "#visionP-slider" ).slider({
        min: .02,
        max: .1,
        step: .005,
        value: .05,
        change: function( event, ui ) {
            console.log('see visionP: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/visionP",ui.value)
            $("#visionPReal").text(ui.value)
        }
    });



    $( "#intake-radioset" ).buttonset();
    $( "#indexer-radioset" ).buttonset();
    $( "#shooter-radioset" ).buttonset();
    $( "#climb-radioset" ).buttonset();


    $('#intake-radioset input').on('change', function() {
       var temp = $('input:checked', '#intake-radioset').attr('id');
       NetworkTables.putValue("/SmartDashboard/intakeState",temp.split('-')[1])
       console.log("sending "+ temp.split('-')[1])
    });

    $('#indexer-radioset input').on('change', function() {
       var temp = $('input:checked', '#indexer-radioset').attr('id');
       NetworkTables.putValue("/SmartDashboard/indexerState",temp.split('-')[1])
    });

    $('#shooter-radioset input').on('change', function() {
       var temp = $('input:checked', '#shooter-radioset').attr('id');
       NetworkTables.putValue("/SmartDashboard/shooterState",temp.split('-')[1])
    });

    $('#climb-radioset input').on('change', function() {
       var temp = $('input:checked', '#climb-radioset').attr('id');
       NetworkTables.putValue("/SmartDashboard/climbState",temp.split('-')[1])
    });





    $( "#accordion" ).accordion();



    var availableTags = [
        "ActionScript",
        "AppleScript",
        "Asp",
        "BASIC",
        "C",
        "C++",
        "Clojure",
        "COBOL",
        "ColdFusion",
        "Erlang",
        "Fortran",
        "Groovy",
        "Haskell",
        "Java",
        "JavaScript",
        "Lisp",
        "Perl",
        "PHP",
        "Python",
        "Ruby",
        "Scala",
        "Scheme"
    ];
    $( "#autocomplete" ).autocomplete({
        source: availableTags
    });



    
    $( "#button-icon" ).button({
        icon: "ui-icon-gear",
        showLabel: false
    });







    $( "#controlgroup" ).controlgroup();



    $( "#tabs" ).tabs();



    $( "#dialog" ).dialog({
        autoOpen: false,
        width: 400,
        buttons: [
            {
                text: "Ok",
                click: function() {
                    $( this ).dialog( "close" );
                }
            },
            {
                text: "Cancel",
                click: function() {
                    $( this ).dialog( "close" );
                }
            }
        ]
    });

    // Link to open the dialog
    $( "#dialog-link" ).click(function( event ) {
        $( "#dialog" ).dialog( "open" );
        event.preventDefault();
    });



    $( "#datepicker" ).datepicker({
        inline: true
    });



    $( "#slider" ).slider({
        range: true,
        values: [ 17, 67 ]
    });



    $( "#progressbar" ).progressbar({
        value: 20
    });



    $( "#spinner" ).spinner();



    $( "#menu" ).menu();



    $( "#tooltip" ).tooltip();



    $( "#selectmenu" ).selectmenu();


    // Hover states on the static widgets
    $( "#dialog-link, #icons li" ).hover(
        function() {
            $( this ).addClass( "ui-state-hover" );
        },
        function() {
            $( this ).removeClass( "ui-state-hover" );
        }
    );
})