
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
    console.error('Did not receive any printer data from the server; cannot update the printer info.')
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
  // see https://www.nxp.com/docs/en/user-guide/141520.pdf
  // 
  // IC       - Version of the IC. For PN532, the contain of this byte is 0x32.
  // Ver      - Version of the firmware,
  // Rev      - Revision of the firmware,
  // Support  - indicates which are the functionalities supported by the firmware.
  //            When the bits are set to 1, the functionality is supported,
  //            otherwise (bit set to 0) it is not.
  //            Bit 2 is ISO18092
  //            Bit 1 is ISO/IEC 14443 TypeB
  //            Bit 0 is ISO/IEC 14443 TypeA
  if (nfc_data === null) {
    console.warn('null NFC status')
    elem.innerHTML = 'disconnected'
    return
  }

  var firmware_version = nfc_data['ver']+'.'+nfc_data['rev']
  var device_type = 'unknown'
  if (nfc_data['ic'] === 0x32) {
    device_type = 'PN532'
  }

  var supported = []
  if (nfc_data['support'] & 1) {
    supported.push('ISO/IEC 14443 TypeA')
  }
  if (nfc_data['support'] & 2) {
    supported.push('ISO/IEC 14443 TypeB')
  }
  if (nfc_data['support'] & 4) {
    supported.push('ISO18092')
  }
//  console.log('Found '+device_type+' NFC device with firmware version '
//    +firmware_version+' and support for '+JSON.stringify(supported))


  device_info_elem.innerHTML = 'Reader connected: '+device_type + ' version '+firmware_version
  message_elem = nfc_data['message'] || ''
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