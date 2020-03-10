//to run this use 
// python3 -m pynetworktables2js --team 7468

var defaultOnce = true;
var shooterState = '';
var hoodState = '';

function onRobotConnection(connected) {
    $('#robotstate').text(connected ? "Connected!" : "Disconnected");
    $('#robotAddress').text(connected ? NetworkTables.getRobotAddress() : "disconnected");
    if(connected && defaultOnce){
        $( "#load-defaults" ).click();
        defaultOnce = false;
    }
   
}

function makeTable(container, data) {
    var table = $("<table/>").addClass('calibrations');
    var row = $("<tr/>");
        $.each(['Index', 'Distance','Limelight TY','Shooter RPM','Launch Angle'], function(colIndex, c) { 
            row.append($("<th/>").text(c));
        });
    table.append(row);

    $.each(data, function(rowIndex, r) {
        var row = $("<tr/>");
        row.append($("<td/>").text(rowIndex));
        $.each(['dist','ty','rpm','launchAngle'], function(colIndex, c) { 
            row.append($("<td/>").text(r[c]));
        });
        table.append(row);
    });
    return container.append(table);
}



//shooter calibration
    // dist - distance to target (inches)
    // rpm - rpm of shooter (rpm)
    // launchAngle - hood angle, 0 to 30deg (0 is fully retracted)
    // ty - ty value for the given distance (px)
var shooterCalib = [
    {'dist':1, 'ty':25, 'rpm':1400, 'launchAngle': 3},
    {'dist':3, 'ty':15, 'rpm':1500, 'launchAngle': 5},
    {'dist':10, 'ty':10, 'rpm':1600, 'launchAngle': 10},
    {'dist':20, 'ty':5, 'rpm':1700, 'launchAngle': 20},
];


//this is going to take the info from the Limelight and try to pick settings for the 
//shooter to hit the target. 
function getShooterSettings(ty) {
    numCalibs = shooterCalib.length;
    //if it is shorter than the closest point, let's use the loweest point
    if(ty>shooterCalib[0].ty){
        return shooterCalib[0];
    }
    //if it is farther than the farthest point, let's use the farthest point
    if(ty<shooterCalib[numCalibs-1].ty){
        return shooterCalib[numCalibs-1];
    }
    //else, let's find some value in the middle of two other values
    var output = {'rpm':-1, 'launchAngle':-1};
    $.each(shooterCalib, function(idx, calib){
        if(idx == numCalibs-1){return false}
        if(ty == calib.ty){output = calib; return false;}
        else if(ty < calib.ty && ty > shooterCalib[idx+1].ty){
            //it is between two calibratoins, let's extrapolate
            var ratio = (ty-calib.ty) / (shooterCalib[idx+1].ty-calib.ty);
            output.rpm = calib.rpm + ratio*(shooterCalib[idx+1].rpm-calib.rpm);
            output.launchAngle = calib.launchAngle + ratio*(shooterCalib[idx+1].launchAngle-calib.launchAngle);
            return false;
        }
    });
    return output;
   
}


function onRobotConnection(connected) {
    $('#robotstate').text(connected ? "Connected!" : "Disconnected");
    $('#robotAddress').text(connected ? NetworkTables.getRobotAddress() : "disconnected");
    if(connected && defaultOnce){
        $( "#load-defaults" ).click();
        defaultOnce = false;
    }
   
}

var lastReceive = {'limeTY':Date.now()};


$(document).ready(function(){
    NetworkTables.addRobotConnectionListener(onRobotConnection, true);
        
    attachRobotConnectionIndicator('#robotIndicator');
      
    // attaches the select element to a SendableChooser object
    attachSelectToSendableChooser("#autonomous", "Autonomous Mode");

    var calibrationTable = makeTable($(document.body), shooterCalib);


    NetworkTables.addGlobalListener(function(key, value, isNew){
    // do something with the values as they change
        //console.log(key)
        if(key=="/SmartDashboard/Mytest"){
            console.log('we see it!')
            console.log(value)
        }else if(key=="/limelight/tx"){
            $("#limeTX").text(value.toFixed(2))
            lastReceive.limeTX = Date.now();
        }else if(key=="/limelight/ty"){
            $("#limeTY").text(value.toFixed(2))
            lastReceive.limeTY = Date.now();
            //let's also calculate a shooting position
            var target = getShooterSettings(value);
            if(target.rpm){
                NetworkTables.putValue("/SmartDashboard/rpmTarget",target.rpm);
                NetworkTables.putValue("/SmartDashboard/launchAngleTarget",target.launchAngle);

                $("#rpmTarget").text(target.rpm.toFixed(2)) 
                $("#launchAngleTarget").text(target.launchAngle.toFixed(2)) 
                
                //if we are in auto shooting state, we should set shooter speed to whatever we think it should be
                if(shooterState=='auto'){
                    $( "#shooter-slider" ).slider('value',target.rpm);
                }
                if(hoodState=='auto'){
                    $( "#hood-slider" ).slider('value',target.launchAngle);
                }
            }
        }

        else{
            console.log(key+"  "+value)
        }
    }, true);


    //here we are going to make sure that the data isn't stable
    setInterval(function(){
        if(Date.now() - lastReceive.limeTY > 2000){ 
            NetworkTables.putValue("/SmartDashboard/rpmTarget",-1);
            NetworkTables.putValue("/SmartDashboard/launchAngleTarget",-1);

            $("#rpmTarget").text('Stale') 
            $("#launchAngleTarget").text('Stale') 
        }

    },1000);



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
        $( "#hood-slider" ).slider('value',0);

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

    $( "#hood-slider" ).slider({
        min: 0,
        max: .125,
        step: .001,
        value: 0,
        change: function( event, ui ) {
            console.log('see hood: '+ui.value)
            NetworkTables.putValue("/SmartDashboard/hoodPosition",ui.value)
            $("#hoodReal").text(parseInt(ui.value))
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
    $( "#hood-radioset" ).buttonset();
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
       shooterState = temp.split('-')[1];
    });

    $('#hood-radioset input').on('change', function() {
       var temp = $('input:checked', '#hood-radioset').attr('id');
       NetworkTables.putValue("/SmartDashboard/hoodState",temp.split('-')[1])
       hoodState = temp.split('-')[1];
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