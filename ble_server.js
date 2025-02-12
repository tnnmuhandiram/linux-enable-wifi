const bleno = require('bleno');

const SERVICE_UUID = '12345678-1234-1234-1234-123456789012';
const CHARACTERISTIC_UUID = '87654321-4321-4321-4321-210987654321';

const characteristic = new bleno.Characteristic({
    uuid: CHARACTERISTIC_UUID,
    properties: ['read', 'write'],
    onReadRequest: (offset, callback) => {
        console.log('Read request received');
        callback(bleno.Characteristic.RESULT_SUCCESS, Buffer.from('Hello from Pi!'));
    },
    onWriteRequest: (data, offset, withoutResponse, callback) => {
        console.log('Write request received:', data.toString());
        callback(bleno.Characteristic.RESULT_SUCCESS);
    }
});

const service = new bleno.PrimaryService({
    uuid: SERVICE_UUID,
    characteristics: [characteristic]
});

bleno.on('stateChange', (state) => {
    if (state === 'poweredOn') {
        bleno.startAdvertising('RaspberryPiBLE', [SERVICE_UUID]);
    } else {
        bleno.stopAdvertising();
    }
});

bleno.on('advertisingStart', (error) => {
    if (!error) {
        console.log('Advertising started...');
        bleno.setServices([service]);
    }
});
