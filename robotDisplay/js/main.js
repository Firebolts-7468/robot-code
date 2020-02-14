
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
        }else{
            //console.log(value)
        }
    }, true);




    console.log('we are here')


    $( "#intake-control" ).controlgroup();
    $( "#indexer-control" ).controlgroup();
    $( "#shooter-control" ).controlgroup();


    $( "#actual-shooter-speed").text("434")
    

    $( "#shooter-speed" ).spinner({
        change: function( event, ui ) {
            console.log('see spin change')
            $("#shooter-slider").slider( "value", $( this ).val() )

        },
        min: 1,
        max: 100,
    });


    $( "#intake-speed" ).val(3);
    $( "#indexer-speed" ).val(3);
    $( "#shooter-speed" ).val(33);



    $( "#shooter-slider" ).slider({
        min: 0,
        max: 100,
        value: 30,
        change: function( event, ui ) {
            console.log('see slider: '+ui.value)
            $( "#shooter-speed" ).val(ui.value);
            NetworkTables.putValue("/SmartDashboard/robotTime",ui.value)
            console.log('sending'+ui.value)
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



    $( "#button" ).button();
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