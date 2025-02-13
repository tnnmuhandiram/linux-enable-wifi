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
      const { ssid, password } = jsonData;
      console.log(`Received Wi-Fi SSID: ${ssid}, Password: ${password}`);

      setWifiCredentials(ssid, password);
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

function setWifiCredentials(ssid, password) {
  const wpaSupplicantPath = '/etc/wpa_supplicant/wpa_supplicant.conf';

  const wifiConfig = `
network={
    ssid="${ssid}"
    psk="${password}"
    key_mgmt=WPA-PSK
}
`;

  console.log(`Writing Wi-Fi config to ${wpaSupplicantPath}`);

  fs.appendFile(wpaSupplicantPath, wifiConfig, (err) => {
    if (err) {
      console.error(`Failed to update Wi-Fi credentials: ${err.message}`);
    } else {
      console.log('Wi-Fi credentials updated successfully. Rebooting now...');

      // Optional: Delay reboot a bit to finish BLE operation
      setTimeout(() => {
        exec('sudo reboot', (error, stdout, stderr) => {
          if (error) {
            console.error(`Reboot failed: ${error.message}`);
            return;
          }
          console.log(`Reboot initiated: ${stdout}`);
        });
      }, 3000); // 3 seconds delay before reboot
    }
  });
}
