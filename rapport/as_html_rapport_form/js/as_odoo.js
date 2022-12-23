$(document).ready(function() {
    $( "#contactForm" ).show();
    $( "#as_mensaje_fin" ).hide();

    $( "form[id='contactForm']" ).submit(function( event ) {
        var as_form_value = $(this).serialize();
        $.ajax({
            url: 'https://rapport.odoo.com' + "/evaluacion_empleado/demo?"+ as_form_value,
            // url: 'http://10.0.10.67:14001' + "/evaluacion_empleado/demo?"+ as_form_value,
            // dataType: "jsonp",
            method: "GET",
            success: function(data, status, xhr) {
                var json = JSON.parse(data);
                if (json.success){
                    $( "#contactForm" ).hide();
                    $( "#as_mensaje_fin" ).show();
                    $( "#as_message_end" ).show();
                    $( "#as_message_error" ).hide();
                }else{
                    $( "#contactForm" ).hide();
                    $( "#as_mensaje_fin" ).show();
                    $( "#as_message_end" ).hide();
                    $( "#as_message_error" ).show();
                }
            
                console.log(data);
            },
            error: function(xhr, status, error) {
                $( "#contactForm" ).hide();
                $( "#as_mensaje_fin" ).show();
                $( "#as_message_end" ).hide();
                $( "#as_message_error" ).show();
                console.log("Result: " + status + " " + error + " " + xhr.status + " " + xhr.statusText)
            }
        });

        console.log( $( this ).serialize() );
        event.preventDefault();
      });

   
      $( "#as_formulario" ).click(function() {
        $( "#contactForm" ).show();
        $( "#as_mensaje_fin" ).hide();
        $( "form[id='contactForm']" )[0].reset();
      
      });
   
    $.ajax({
        // url: window.location.origin + "/evaluacion_empleado/config",
        url: 'https://rapport.odoo.com' + "/evaluacion_empleado/config",
        // url: 'http://10.0.10.67:14001' + "/evaluacion_empleado/config",
        // dataType: "jsonp",
        method: "GET",
        success: function(data, status, xhr) {
            var json = JSON.parse(data);
            $('#as_message').html(json.mensaje.as_ini_massage);
            $('#as_message_end').html(json.mensaje.as_save_massage);
            console.log(data);
        },
        error: function(xhr, status, error) {
            console.log("Result: " + status + " " + error + " " + xhr.status + " " + xhr.statusText)
        }
    });
});