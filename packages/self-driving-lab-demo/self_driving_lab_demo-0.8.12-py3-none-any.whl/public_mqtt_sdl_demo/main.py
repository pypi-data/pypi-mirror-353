"""Run a self-driving lab on a Raspberry Pi Pico W."""

import gc
import json
import os
import ssl
from secrets import HIVEMQ_HOST, HIVEMQ_PASSWORD, HIVEMQ_USERNAME, PASSWORD, SSID
from time import sleep

import ntptime
from as7341_sensor import Sensor
from data_logging import log_to_mongodb
from machine import PWM, WDT, Pin, unique_id  # Removed reset, added WDT
from netman import connectWiFi
from sdl_demo_utils import (
    Experiment,
    encrypt_id,
    get_onboard_led,
    get_traceback,
    heartbeat,
    sign_of_life,
)
from ubinascii import hexlify
from umqtt.simple import MQTTClient

try:
    from secrets import (
        DEVICE_NICKNAME,
        MONGODB_API_KEY,
        MONGODB_APP_NAME,
        MONGODB_CLUSTER_NAME,
        MONGODB_COLLECTION_NAME,
        MONGODB_DATABASE_NAME,
    )
except Exception as e:
    print(get_traceback(e))

##### BEGIN USER-DEFINED IMPORTS #####
from neopixel import NeoPixel

##### END USER-DEFINED IMPORTS #####

# sleep to avoid KeyboardInterrupt overwriting log.txt when opening in Thonny
sleep(5.0)

try:
    gc.collect()
    port = 8883

    logfile = open("log.txt", "w")
    # duplicate stdout and stderr to the log file
    os.dupterm(logfile)

    # https://medium.com/@johnlpage/introduction-to-microcontrollers-and-the-pi-pico-w-f7a2d9ad1394

    # Setup watchdog timer with a timeout of 8 seconds (max for rp2040)
    wdt = WDT(timeout=8000)

    # you can request a MongoDB collection specific to you by emailing
    # sterling.baird@utah.edu
    mongodb_url = f"https://data.mongodb-api.com/app/{MONGODB_APP_NAME}/endpoint/data/v1/action/insertOne"  # noqa: E501

    my_id = hexlify(unique_id()).decode()
    my_encrypted_id = encrypt_id(my_id, verbose=True)

    # # aside: for sgbaird's public test demo only
    # my_id = "test"
    # my_encrypted_id = "test"

    with open("pico_id.txt", "w") as f:
        f.write(my_id)

    trunc_device_id = str(my_encrypted_id)[0:10]
    prefix = f"sdl-demo/picow/{my_id}/"

    print("")
    print(f"PICO_ID: {my_id}")
    print("")

    print(f"Unencrypted PICO ID (keep private): {my_id}")
    print(f"Encrypted PICO ID (OK to share publicly): {my_encrypted_id}")
    print(f"Truncated, encrypted PICO ID (OK to share publicly): {trunc_device_id}")
    print(f"MQTT prefix: {prefix}")

    try:
        connectWiFi(SSID, PASSWORD, country="US")
    except RuntimeError as e:
        wdt.feed()
        print("WiFi connection failed. Retrying in 5 seconds...")
        sleep(5.0)
        try:
            wdt.feed()
            connectWiFi(SSID, PASSWORD, country="US")
        except RuntimeError as e:
            raise RuntimeError(
                "WiFi connection failed. Ensure you are using a 2.4 GHz WiFi network with WPA-2 authentication. See the additional prerequisites section from https://doi.org/10.1016/j.xpro.2023.102329 or the https://github.com/sparks-baird/self-driving-lab-demo/issues/76 for additional troubleshooting help."
            ) from e

    sdcard_backup_fpath = "/sd/experiments.txt"

    # To validate certificates, a valid time is required
    ntptime.timeout = 30  # type: ignore
    ntptime.host = "pool.ntp.org"
    try:
        wdt.feed()
        ntptime.settime()
    except Exception as e:
        print(get_traceback(e))
        print("Retrying ntptime.settime(), still with pool.ntp.org")
        try:
            wdt.feed()
            ntptime.settime()
        except Exception as e:
            print(get_traceback(e))
            print("Retrying ntptime.settime() with time.google.com")
            ntptime.host = "time.google.com"
            ntptime.settime()

    der_fname = "hivemq-com-chain.der"
    try:
        print("Obtaining CA Certificate")
        with open(der_fname, "rb") as f:
            cacert = f.read()
    except FileNotFoundError as e:
        print(get_traceback(e))
        print(
            f"{der_fname} file not found. For versions 0.4.2+, this file is required. Please upload this to the Pico W directly from the unzipped folder or at https://github.com/sparks-baird/self-driving-lab-demo/blob/main/src/public_mqtt_sdl_demo/hivemq-com-chain.der (permalink: https://github.com/sparks-baird/self-driving-lab-demo/blob/a27ebda49f7307fa17fca9e8b8531c59585b6b98/src/public_mqtt_sdl_demo/hivemq-com-chain.der)"
        )

    logfile.close()
    os.dupterm(None)

    ######################################
    #### BEGIN USER-DEFINED FUNCTIONS ####
    ######################################

    # at minimum, the following functions should be defined:
    # - run_experiment (use a parameters dict to run experiment and return sensor data)
    # - initialize_devices (return dict mapping device name --> device object or empty dict)
    # - reset_experiment (reset experiment to initial state)
    # - emergency_shutdown (can be same as reset_experiment if needed)

    # device objects should be defined here
    pixels = NeoPixel(Pin(28), 1)  # one NeoPixel on Pin 28 (GP28)
    sensor = Sensor()

    def get_devices():
        # enforce instantiation of the devices a single time (i.e. singleton function)
        return {"pixels": pixels, "sensor": sensor}

    def run_experiment(parameters, devices=None):
        if devices is None:
            devices = get_devices()

        pixels = devices["pixels"]
        sensor = devices["sensor"]

        r, g, b = [parameters[key] for key in ["R", "G", "B"]]
        atime = parameters.get("atime", 100)
        astep = parameters.get("astep", 999)
        gain = parameters.get("gain", 128)

        assert 0 <= r <= 255, f"Invalid R: {r} (must be between 0 and 255)"
        assert 0 <= g <= 255, f"Invalid G: {g} (must be between 0 and 255)"
        assert 0 <= b <= 255, f"Invalid B: {b} (must be between 0 and 255)"
        assert 0 <= atime <= 255, f"Invalid atime: {atime} (must be between 0 and 255)"
        assert (
            0 <= astep <= 65536
        ), f"Invalid astep: {astep} (must be between 0 and 65536)"
        assert 0.5 <= gain <= 512, f"Invalid gain: {gain} (must be between 0.5 and 512)"

        sensor._atime = atime
        sensor._astep = astep
        sensor._gain = gain

        pixels[0] = (0, 0, 0)
        pixels.write()
        background_data = sensor.all_channels

        pixels[0] = (r, g, b)
        pixels.write()

        sensor_data = sensor.all_channels

        CHANNEL_NAMES = [
            "ch410",
            "ch440",
            "ch470",
            "ch510",
            "ch550",
            "ch583",
            "ch620",
            "ch670",
        ]

        sensor_data = {ch: datum for ch, datum in zip(CHANNEL_NAMES, sensor_data)}
        background_data = {
            ch: datum for ch, datum in zip(CHANNEL_NAMES, background_data)
        }
        sensor_data["background"] = background_data
        return sensor_data

    def reset_experiment(parameters, devices=None):
        if devices is None:
            devices = get_devices()

        pixels = devices["pixels"]

        # Turn off the LED
        pixels[0] = (0, 0, 0)
        pixels.write()

    ######################################
    ##### END USER-DEFINED FUNCTIONS #####
    ######################################

    devices = get_devices()

    onboard_led = get_onboard_led()
    buzzer = PWM(Pin(18))

    # MQTT Resources:
    # https://gist.github.com/sammachin/b67cc4f395265bccd9b2da5972663e6d
    # http://www.steves-internet-guide.com/into-mqtt-python-client/

    # sdcard_ready = initialize_sdcard()
    sdcard_ready = False  # deprecating sdcard functionality to avoid confusion
    experiment = Experiment(
        run_experiment_fn=run_experiment,
        reset_experiment_fn=reset_experiment,
        emergency_shutdown_fn=reset_experiment,
        devices=devices,
        buzzer=buzzer,
        sdcard_ready=sdcard_ready,
    )

    def callback(topic, msg, retain=None, dup=None):
        t = topic.decode("utf-8").lstrip(prefix)
        print(t)

        if t[:5] == "GPIO/":
            payload_data = experiment.try_experiment(msg)

            if experiment.sdcard_ready:
                payload_data = experiment.write_to_sd_card(
                    payload_data, fpath=sdcard_backup_fpath
                )

            # prefer qos=1, but causes recursion error if too many messages in short period
            # of time
            payload_data["device_nickname"] = DEVICE_NICKNAME
            payload_data["encrypted_device_id_truncated"] = trunc_device_id
            try:
                parameters = json.loads(msg)
                if parameters.get("mongodb") is True:
                    log_to_mongodb(
                        payload_data,
                        url=mongodb_url,
                        api_key=MONGODB_API_KEY,
                        cluster_name=MONGODB_CLUSTER_NAME,
                        database_name=MONGODB_DATABASE_NAME,
                        collection_name=MONGODB_COLLECTION_NAME,
                        verbose=True,
                        retries=2,
                    )
                    payload_data["logged_to_mongodb"] = True
                else:
                    payload_data["logged_to_mongodb"] = False
            except Exception as e:
                payload_data["logged_to_mongodb"] = False
                print(get_traceback(e))

            payload = json.dumps(payload_data)
            print(payload)

            client.publish(prefix + "as7341/", payload, qos=0)

    client = MQTTClient(
        prefix,
        HIVEMQ_HOST,
        user=HIVEMQ_USERNAME,
        password=HIVEMQ_PASSWORD,
        keepalive=3600,
        ssl=True,
        port=port,
        ssl_params={
            "server_side": False,
            "key": None,
            "cert": None,
            "cert_reqs": ssl.CERT_REQUIRED,
            "cadata": cacert,
            "server_hostname": HIVEMQ_HOST,
        },
    )
    del cacert
    try:
        wdt.feed()
        client.connect()
    except OSError as e:
        print(get_traceback(e))
        print("Retrying client.connect() in 2 seconds...")
        sleep(2.0)
        try:
            wdt.feed()
            client.connect()
        except OSError as e:
            print(get_traceback(e))
            print(
                "Failed to connect on second attempt. Ensure you have the correct 'hivemq-com-chain.der' file *specific* to your HiveMQ Cloud broker instance (now required as of June 2024). The default file works for the self-driving-lab-demo, but for your own instance, generate and upload the correct CA file to your microcontroller. Your certificate can be generated via https://colab.research.google.com/github/sparks-baird/self-driving-lab-demo/blob/main/notebooks/7.2.1-hivemq-openssl-certificate.ipynb. See also https://github.com/sparks-baird/self-driving-lab-demo/issues/245"
            )  # noqa: E501

    client.set_callback(callback)
    client.subscribe(prefix + "GPIO/#")

    heartbeat(client, True)
    sign_of_life(onboard_led, True)

    print("")
    print("Waiting for experiment requests...")
    print("")

    while True:
        try:
            client.check_msg()
            heartbeat(client, False)
            sign_of_life(onboard_led, False)
            wdt.feed()  # Feed the watchdog timer to prevent reset
        except Exception as e:
            print(get_traceback(e))
            print("Reconnecting to WiFi...")
            connectWiFi(SSID, PASSWORD, country="US")
            client.connect(clean_session=False)
            client.set_callback(callback)
            client.subscribe(prefix + "GPIO/#")
            wdt.feed()  # Ensure watchdog is fed even after reconnecting
except Exception as e:
    print(get_traceback(e))
    fname = "error.txt"
    logfile = open(fname, "w")
    logfile.write(get_traceback(e))
    logfile.close()

# %% Code Graveyard

#             logfile = open("log.txt", "a")
#             logfile.write(get_traceback(e))
#             os.dupterm(logfile)
#             logfile.close()
#             os.dupterm(None)
