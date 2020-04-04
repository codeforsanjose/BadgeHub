
var ENDPOINT = 'http://' + document.domain + ':' + location.port
// var ENDPOINT = 'http://192.168.86.243/admin'

var cached_printer_info = {};

function get_printer_definitions(printer_info) {
    jQuery.getJSON(ENDPOINT+'/static/js/cups/printers.json', function(data, textStatus, jqXHR) {
        for (const key in data) {
            cached_printer_info[data[key]['model_name']] = data[key]
            if (data[key]['model_name'] === printer_info['printer_model']) {
                get_media_types_for_printer(data[key]['model_name'], data[key]['short_name'])
            }
        }
    })
}

function get_media_types_for_printer(printer_long_name, printer_short_name) {
    console.log('Looking up media types for '+ printer_long_name+' ('+printer_short_name+')')
    jQuery.getJSON(ENDPOINT+'/static/js/cups/'+printer_short_name+'.json', function(data, textStatus, jqXHR) {
        cached_printer_info[printer_long_name]['media_types'] = data
    })
}

function update_printer_list(printer_list_elem, media_select_elem, printer_data){
  // see https://www.cups.org/doc/cupspm.html#basic-destination-information
  if (Object.keys(printer_data).length === 0) {
    console.warn('Did not receive any printer data from the server; cannot update the printer info.')
    return
  }
  printer_list_elem = $(printer_list_elem)
  printer_data.forEach(function(printer){
    if (printer['printer_model'] in cached_printer_info) {
        var printer_facts = cached_printer_info[printer['printer_model']]
        var short_name = printer_facts['short_name']
        var printer_online = printer['online']
        var printer_name = printer['printer_model']
        var printer_elem = printer_list_elem.find('.'+short_name)[0]

        if (printer_elem === undefined){
          printer_list_elem.append(
            $('<li/>')
              .attr('data-printer-online', printer_online)
              .addClass(short_name)
              .text(printer_name))
        } else {
          $(printer_elem[0])
            .attr('data-printer-online', printer_online)
            .text(printer_name)
        }
        if (printer['default_printer'] === true) {
            update_media_list_for_printer(media_select_elem, printer_name, printer['default_media_size'])
        }
    } else {
        // then grab the media definitions and update on the next loop
        get_printer_definitions(printer)
    }
  })
}

function update_media_list_for_printer(media_select_elem, printer_long_name, selected_media) {
    if (media_select_elem.dataset.printer === printer_long_name) {
        // no need to update
        return
    }
    media_select_elem.innerHTML = ''
    media_select_elem.dataset.printer = printer_long_name

    var media_types = cached_printer_info[printer_long_name]['media_types']
    for (const key in media_types) {
        var type = media_types[key]
        var o = new Option(type['label'], type['cups_id'])
        if (selected_media === type['cups_id']){
            o.selected = true;
        }
        media_select_elem.add(o)
    }
}


function update_nfc_info(device_info_elem, message_elem, nfc_data){

  if (nfc_data === null ) {
    console.warn('null NFC status')
    message_elem.innerHTML = 'disconnected'
    return
  }

  var chipset = nfc_data['chipset'] || ''
  var vendor = nfc_data['vendor'] || ''
  var product = nfc_data['product'] || ''
  var path = nfc_data['path'] || ''
  var last_seen_utc = nfc_data['last_seen_utc_ms'] || ''

  if (path.length == 0) {
    message_elem.innerHTML = 'disconnected'
  } else {
    device_info_elem.innerHTML = 'Reader connected:<br/>'+chipset + '<br/>'+vendor+'<br/>'+product+'<br/>'+path
    message_elem = nfc_data['message'] || ''
  }
}




function poll_status(config) {
  console.log('connecting to socket at '+ENDPOINT)
//  var socket = io(ENDPOINT);
  // socket.on('connect', function(socket){
  //   // socket.emit('request', /* */); // emit an event to the socket
  //   // io.emit('broadcast', /* */); // emit an event to all connected sockets
    
  // });
//  socket.on('connect', function(data){ console.log('connected!', data) })
//  socket.on('connection_status', function(data){ console.log('connection_status event', data) })
//
//  socket.on('server_status', function(data){ console.log('server_status event received', data) });
//  socket.on('server_status_event', function(data){ console.log('server_status_event event received', data) });

  // socket.on('server_status_event', function(data){
  //   console.log('server_status_event event received')
  //   update_printer_list(config['printer_elem'], data['printers'])
  //   update_nfc_info(config['nfc_elem'], data['nfc'])
  // });


   setInterval(function(){
     jQuery.getJSON(ENDPOINT+'/admin/status', function(data, textStatus, jqXHR) {
        console.log(data)
       update_printer_list(config['printer_elem'], config['printer_media_select_elem'], data['printers'])
       update_nfc_info(config['nfc_device_info_elem'], config['nfc_message_elem'], data['nfc'])
     })
   }, config['update_interval'])

}