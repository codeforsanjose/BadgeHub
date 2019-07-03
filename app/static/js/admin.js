
var ENDPOINT = 'http://' + document.domain + ':' + location.port+ '/admin'
// var ENDPOINT = 'http://192.168.86.243/admin'


function decode_cups_status(status) {
  if (status === 3) {
    return 'idle'
  } else if (status === 4) {
    return 'printing'
  } else if (status === 5) {
    return 'stopped'
  }
  return 'unknown'
}

function update_printer_list(elem, printer_data){
  // see https://www.cups.org/doc/cupspm.html#basic-destination-information
  var plist = $(elem_selector)
  for (var printer in printer_data){
    console.log(printer)
    var printer_elem = plist.find('.'+printer)[0]
    var printer_status = decode_cups_status(printer_data[printer]['printer-state'])
    var printer_name = printer_data[printer]['printer-make-and-model']
    if (printer_elem === undefined){
      plist.append(
        $('<li/>')
          .attr('data-status', printer_status)
          .addClass(printer)
          .text(printer_name))
    } else {
      $(printer_elem)
        .attr('data-status', printer_status)
        .text(printer_name)
    }
  }
  
}

function update_nfc_info(elem, nfc_data){
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
  console.log('Found '+device_type+' NFC device with firmware version '
    +firmware_version+' and support for '+JSON.stringify(supported))
  
  var device_elem = document.createElement('span');
  device_elem.innerHTML = device_type + ' version '+firmware_version
  elem.appendChild(device_elem)
}




function poll_status(config) {
  console.log('connecting to socket at '+ENDPOINT)
  var socket = io(ENDPOINT);
  // socket.on('connect', function(socket){
  //   // socket.emit('request', /* */); // emit an event to the socket
  //   // io.emit('broadcast', /* */); // emit an event to all connected sockets
    
  // });
  socket.on('connect', function(data){ console.log('connected!', data) })
  socket.on('connection_status', function(data){ console.log('connection_status event', data) })

  socket.on('server_status', function(data){ console.log('server_status event received', data) });
  socket.on('server_status_event', function(data){ console.log('server_status_event event received', data) });

  // socket.on('server_status_event', function(data){
  //   console.log('server_status_event event received')
  //   update_printer_list(config['printer_elem'], data['printers'])
  //   update_nfc_info(config['nfc_elem'], data['nfc'])
  // });

// function poll_status(config, interval) {
//   setInterval(function(){
//     jQuery.getJSON(ENDPOINT+'/api/status', function(data, textStatus, jqXHR) {
//       // console.log(data)
//       update_printer_list(config['printer_elem'], data['printers'])
//       update_nfc_info(config['nfc_elem'], data['nfc'])
//     })
//   }, config['update_interval'])
// }
}