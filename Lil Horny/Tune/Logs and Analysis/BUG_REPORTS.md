# Bug report drafts: motors spin to full throttle on save/disconnect (3D mode)

Fill in the `[brackets]` before posting. Post the Betaflight one first, then link it from the AM32 one (and vice versa).

- Betaflight Configurator issues: https://github.com/betaflight/betaflight-configurator/issues
- AM32 issues: https://github.com/am32-firmware/AM32/issues

---

## 1. Betaflight (Configurator / firmware)

**Title:** 3D mode + bidirectional DShot: motors run up to full throttle on CLI `save` / Configurator disconnect while battery connected

**Description**
With `feature 3D` enabled and DShot600 bidirectional, all motors spin up to full throttle when I save settings or disconnect Configurator with a battery plugged in. It only happens while connected to Configurator over USB. Normal arming, disarming, flight and power cycling all behave correctly.

**Steps to reproduce**
1. Enable 3D (`feature 3D`), DShot600 with `dshot_bidir = ON`, ESCs (AM32) in bidirectional mode.
2. Connect battery + USB, open Configurator.
3. Run `save` in the CLI **or** click Disconnect: [which one(s)]
4. Motors spin up to full throttle [forward/reverse?] and [stop by themselves after ~X s / keep running until the battery is unplugged].

**Expected:** motors stay stopped (3D neutral) through save/reboot and disconnect.

**Environment**
- Firmware: Betaflight 4.5.1 (77d01ba3b), AT32F435M, target TBS_LUCID_AIO
- Configurator version: [x.y.z]
- Motor protocol: DShot600, bidirectional, 8k/8k, `dshot_idle_value = 400`, `motor_poles = 12`
- 3D settings: [paste `get 3d` output]
- ESC: on-board AM32 [version], bidirectional mode ON
- Receiver: CRSF

**Attachments:** `diff all`, a short phone video of it happening (props off).

---

## 2. AM32

**Title:** Bidirectional mode: motors go to full throttle when FC reboots / Configurator disconnects (TBS Lucid AIO)

**Description**
In bidirectional (3D) mode, the motors run up to full throttle when the flight controller reboots after a Betaflight `save`, or when Betaflight Configurator disconnects. The battery is connected and the props are off. The ESC behaves correctly when armed/disarmed normally and on power cycle. My guess is that the ESC misreads the signal line during the FC reboot or the Configurator stop command (e.g. treating it as a PWM/servo input or a non-neutral 3D value). I haven't confirmed that.

**Steps to reproduce**
1. AM32 [version] on TBS Lucid AIO ESC (target: [target name shown in esc-configurator]), bidirectional ON, motor poles 12.
2. Betaflight 4.5.1, 3D feature, DShot600 bidirectional.
3. Battery + USB connected, then `save` in the Betaflight CLI / Disconnect in Configurator.
4. Motors spin to full throttle [direction], [duration / until battery removed].

**Notes**
- [Did this happen on the previous AM32 version? yes / no / not tested]
- ESC settings: [screenshot from esc-configurator]
- Linked Betaflight issue: [link]
