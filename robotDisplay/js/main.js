//to run this use 
// python3 -m pynetworktables2js --team 7468


function onRobotConnection(connected) {
    $('#robotstate').text(connected ? "Connected!" : "Disconnected");
    $('#robotAddress').text(connected ? NetworkTables.getRobotAddress() : "disconnected");
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
            $("#limeTX").text(value)
        }else if(key=="/limelight/ty"){
            $("#limeTY").text(value)
        }

        else{
            console.log(key+"  "+value)
        }
    }, true);


    $( "#load-defaults" ).button();
    $( "#load-defaults" ).click(function( event ) {
        console.log('loading defaults');
        $( "#xRatio-slider" ).trigger("change");
        NetworkTables.putValue("/SmartDashboard/xRatio",$("#xRatio-slider").slider("option","value"));
        NetworkTables.putValue("/SmartDashboard/yRatio",$("#yRatio-slider").slider("option","value"));
        NetworkTables.putValue("/SmartDashboard/spinRatio",$("#spinRatio-slider").slider("option","value"));

        NetworkTables.putValue("/SmartDashboard/steeringTrim",$("#spinRatio-slider").slider("option","value"));

        NetworkTables.putValue("/SmartDashboard/indexerSpeed",$("#indexer-slider").slider("option","value"));
        NetworkTables.putValue("/SmartDashboard/intakeSpeed",$("#intake-slider").slider("option","value"));
        NetworkTables.putValue("/SmartDashboard/shooterSpeed",$("#shooter-slider").slider("option","value"));

        $("#xRatioReal").text($("#xRatio-slider").slider("option","value"));
        $("#yRatioReal").text($("#yRatio-slider").slider("option","value"));
        $("#spinRatioReal").text($("#spinRatio-slider").slider("option","value"));
        $("#trimReal").text($("#trim-slider").slider("option","value"));
        $("#indexerReal").text($("#indexer-slider").slider("option","value"));
        $("#intakeReal").text($("#intake-slider").slider("option","value"));
        $("#shooterReal").text($("#shooter-slider").slider("option","value"));


    });


    $( "#intake-control" ).controlgroup();
    $( "#indexer-control" ).controlgroup();
    $( "#shooter-control" ).controlgroup();



    $( "#xRatio-slider" ).slider({
        min: 1,
        max: 6,
        step: .2,
        value: 3,
        change: function( event, ui ) {
            console.log('see xslider: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/xRatio",ui.value)
            $("#xRatioReal").text(ui.value)
        }
    });
    $( "#yRatio-slider" ).slider({
        min: 1,
        max: 6,
        step: .2,
        value: 4,
        change: function( event, ui ) {
            console.log('see yslider: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/yRatio",ui.value)
            $("#yRatioReal").text(ui.value)
        }
    });
    $( "#spinRatio-slider" ).slider({
        min: 1,
        max: 6,
        step: .2,
        value: 3,
        change: function( event, ui ) {
            console.log('see yslider: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/spinRatio",ui.value)
            $("#spinRatioReal").text(ui.value)
        }
    });
    $( "#trim-slider" ).slider({
        min: -.3,
        max: .3,
        step: .05,
        value: -.05,
        change: function( event, ui ) {
            console.log('see yslider: '+ui.value)
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
            $("#indexerReal").text(ui.value)
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
            $("#intakeReal").text(ui.value)
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
            $("#shooterReal").text(ui.value)
        }
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



    $( "#radioset" ).buttonset();



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