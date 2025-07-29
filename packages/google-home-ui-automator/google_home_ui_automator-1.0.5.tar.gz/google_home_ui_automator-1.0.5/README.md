# Google Home UI Automator

Google Home Automator can help you automate your Google Home App.

## Getting Started

### Prerequisites

#### Python 3

You need a python 3 environment to run the script. Google Home UI Automator
requires python 3.11 or newer.

#### Android phone

1.  Turn on ***User Debugging*** mode on your android phone.
1.  Connect your android phone to computer.

#### Google Home App

1.  You need to install Google Home App on your Android phone.
1.  Login to your Google Home App.
1.  Make sure the Google Home App's version is between `3.1.1.14` and
    `3.32.126.2`. Dogfood version `3.32.192.0-dog-food` is also supported.

NOTE: Please select the correct Google account on Google Home App.

NOTE: This tool only works with the English version of the Google Home App.

### Installation

#### PyPI (recommended)

```shell
$ pip install google-home-ui-automator
```

#### Build from source code

1.  clone this repo.

    ```shell
    $ git clone https://testsuite-smarthome-matter.googlesource.com/ui-automator
    ```

2.  `cd` to the folder.

3.  Run `pip install .`

## Usage

### Commissioning Matter device

Follow the steps below to automatically commission a matter device.

```shell
$ ui-automator --commission DEVICE_NAME,PAIRING_CODE,ROOM_NAME [--google_account <GOOGLE_ACCOUNT>]
```

*   `DEVICE_NAME`: desired Matter device, e.g. `m5stack`
*   `PAIRING_CODE`: pairing code of your Matter device, e.g. `34970112332`
*   `ROOM_NAME`: room that is going to be assigned, e.g. `Office`
*   `GOOGLE_ACCOUNT`: Optional. Account to use in Google Home App, e.g.
    `test@gmail.com`

### Decommissioning Matter device

Follow the steps below to decommission a matter device.

```shell
$ ui-automator --decommission DEVICE_NAME [--google_account <GOOGLE_ACCOUNT>]
```

*   `DEVICE_NAME`: display name of commissioned Matter device on GHA, e.g.
    `m5stack`
*   `GOOGLE_ACCOUNT`: Optional. Account to use in Google Home App, e.g.
    `test@gmail.com`

### Regression Test

Follow the steps below to run a regression test.

```shell
$ ui-automator --commission DEVICE_NAME,PAIRING_CODE,ROOM_NAME --regtest [--repeat <REPEAT_TIMES>] [--hub <HUB_VERSION>] [--dut <MODEL>,<TYPE>,<PROTOCOL>] [--fw <DEVICE_FIRMWARE>] [--google_account <GOOGLE_ACCOUNT>]
```

*   `DEVICE_NAME`: desired Matter device, e.g. `m5stack`
*   `PAIRING_CODE`: pairing code of your Matter device, e.g. `34970112332`
*   `ROOM_NAME`: room that is going to be assigned, e.g. `Office`
*   `--repeat`: Optional. Specifies the number of times to repeat the regression
    test.
    *   `REPEAT_TIMES`: Number of times to repeat the regression test, e.g.,
        `10`.
*   `--hub`: Optional. Includes the hub version in the test report.
    *   `HUB_VERSION`: Version of the hub controlling the devices in GHA, e.g.,
        `1.0.0`
*   `--dut`: Optional. Includes the device under test information in the test
    report.
    *   `MODEL`: Model of the device. e.g. `X123123`
    *   `TYPE`: Type of the device. e.g. `LIGHT`
    *   `PROTOCOL`: Protocol used by the device. e.g. `MATTER`
*   `--fw`: Optional. Includes the device firmware in the test report.
    *   `DEVICE_FIRMWARE`: Firmware of test device.
*   `GOOGLE_ACCOUNT`: Optional. Account to use in Google Home App, e.g.
    `test@gmail.com`

## Roadmap

-   [x] Commissioning Matter device
-   [x] Decommissioning Matter device
-   [x] Regression test of cycling commissioning/decommissioning
-   [ ] Support regression test for devices that need additionally manual
    operations after decommissioning to recover to BLE commissioning mode
-   [ ] Share Fabric
-   [ ] Get pairing code when sharing fabric

## Notice

*   While UI Automation is processing, interfering android phone with any UI
    operation might fail the automation.

## Report issue

-   Click
    [here](https://issuetracker.google.com/issues/new?component=655104&template=1694023)
    to report any encountered issues.

## Disclaimer

This project is not an official Google project. It is not supported by Google
and Google specifically disclaims all warranties as to its quality,
merchantability, or fitness for a particular purpose.
