process.env['BLENO_HCI_DEVICE_ID'] = '0';
const bleno = require('@abandonware/bleno');
const { exec } = require('child_process');
const fs = require('fs');

const SERVICE_UUID = '12345678-1234-1234-1234-123456789012';
const CHARACTERISTIC_UUID = '87654321-4321-4321-4321-210987654321';

const characteristic = new bleno.Characteristic({
  uuid: CHARACTERISTIC_UUID,
  properties: ['read', 'write', 'writeWithoutResponse'],
  onReadRequest: (offset, callback) => {
    console.log('Read request received');
    callback(bleno.Characteristic.RESULT_SUCCESS, Buffer.from('Hello from Pi!'));
  },
  onWriteRequest: (data, offset, withoutResponse, callback) => {
    try {
      const jsonData = JSON.parse(data.toString());
      const { ssid, password,uuid } = jsonData;
      console.log(`Received Wi-Fi SSID: ${ssid}, Password: ${password}`);

      setWifiCredentials(ssid, password,uuid);
      callback(bleno.Characteristic.RESULT_SUCCESS);
    } catch (error) {
      console.error('Failed to parse Wi-Fi credentials:', error);
      callback(bleno.Characteristic.RESULT_UNLIKELY_ERROR);
    }
  },
});

const service = new bleno.PrimaryService({
  uuid: SERVICE_UUID,
  characteristics: [characteristic],
});

bleno.on('stateChange', (state) => {
  console.log(`State changed: ${state}`);
  if (state === 'poweredOn') {
    bleno.startAdvertising('RaspberryPiBLE', [SERVICE_UUID]);
  } else {
    bleno.stopAdvertising();
  }
});

bleno.on('advertisingStart', (error) => {
  if (!error) {
    console.log('Advertising started...');
    bleno.setServices([service], (error) => {
      if (error) {
        console.error('Set services error:', error);
      } else {
        console.log('Services successfully set!');
      }
    });
  } else {
    console.error('Advertising start error:', error);
  }
});

// function setWifiCredentials(ssid, password) {
//   const wpaSupplicantPath = '/etc/wpa_supplicant/wpa_supplicant.conf';

//   const wifiConfig = `
// ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
// update_config=1
// country=US
// network={
//     ssid="${ssid}"
//     psk="${password}"
//     key_mgmt=WPA-PSK
// }
// `.trim();

//   console.log(`Writing Wi-Fi config to ${wpaSupplicantPath}`);

//   // Step 1: Delete the existing file if it exists
//   fs.access(wpaSupplicantPath, fs.constants.F_OK, (err) => {
//     if (!err) {
//       console.log(`File exists. Removing ${wpaSupplicantPath}...`);
//       fs.unlink(wpaSupplicantPath, (err) => {
//         if (err) {
//           console.error(`Failed to delete existing Wi-Fi config: ${err.message}`);
//           return;
//         }
//         console.log(`Existing Wi-Fi config deleted.`);
//         // Proceed to write the new file
//         writeWifiConfig(wpaSupplicantPath, wifiConfig);
//       });
//     } else {
//       console.log(`File does not exist. Creating a new one.`);
//       // If file does not exist, directly write the file
//       writeWifiConfig(wpaSupplicantPath, wifiConfig);
//     }
//   });
// }

// function writeWifiConfig(wpaSupplicantPath, wifiConfig) {
//   fs.writeFile(wpaSupplicantPath, wifiConfig, (err) => {
//     if (err) {
//       console.error(`Failed to write Wi-Fi credentials: ${err.message}`);
//     } else {
//       console.log('Wi-Fi credentials written successfully. Rebooting now...');
//       setTimeout(() => {
//         exec('sudo reboot', (error, stdout, stderr) => {
//           if (error) {
//             console.error(`Reboot failed: ${error.message}`);
//             return;
//           }
//           console.log(`Reboot initiated: ${stdout}`);
//         });
//       }, 3000);
//     }
//   });


function setWifiCredentials(ssid, password,uuid) {
  const wpaSupplicantPath = '/etc/wpa_supplicant/wpa_supplicant.conf';
  const uuidFilePath = '/etc/device_uuid';

  const wifiConfig = `
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
network={
    ssid="${ssid}"
    psk="${password}"
    key_mgmt=WPA-PSK
}
`.trim();

  console.log(`Writing Wi-Fi config to ${wpaSupplicantPath}`);

  // Step 1: Write Wi-Fi credentials
  fs.writeFile(wpaSupplicantPath, wifiConfig, (err) => {
    if (err) {
      console.error(`Failed to write Wi-Fi credentials: ${err.message}`);
      return;
    }
    console.log('Wi-Fi credentials written successfully.');

    // Step 2: Generate and Write UUID only if not present
    fs.access(uuidFilePath, fs.constants.F_OK, (err) => {
      if (err) {
        
        console.log(` UUID: ${uuid}`);
        fs.writeFile(uuidFilePath, uuid, { mode: 0o600 }, (err) => {
          if (err) {
            console.error(`Failed to write UUID: ${err.message}`);
            return;
          }
          console.log(`UUID written to ${uuidFilePath}`);
          initiateReboot();
        });
      } else {
        console.log(`UUID file already exists at ${uuidFilePath}.`);
        initiateReboot();
      }
    });
  });
}

function initiateReboot() {
  console.log('Rebooting system in 3 seconds...');
  setTimeout(() => {
    exec('sudo reboot', (error, stdout, stderr) => {
      if (error) {
        console.error(`Reboot failed: ${error.message}`);
        return;
      }
      console.log(`Reboot initiated: ${stdout}`);
    });
  }, 3000);
}




