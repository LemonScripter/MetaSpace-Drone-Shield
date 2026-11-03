# Navigation after the shield engages: what is and is not supported

**Status: concept note. Nothing in this repository implements or tests autonomous navigation.**

The gate decides *that* the GNSS position is inconsistent with the inertial estimate. It does not navigate. A possible reaction is to continue on inertial dead reckoning (INS/IMU) and return to a safe point, but:

* **Dead reckoning drifts.** The position error of a low-cost inertial unit grows with time (velocity error integrates into position error; an uncorrected bias grows roughly quadratically). Without another source (barometer, vision, odometry, terrain matching), the INS-only position is trustworthy for seconds to minutes, depending on the sensor grade. A "provable" return to base needs a bound on this error, which the repository does not provide.
* **A flight plan encoded in the specification is not a verified model of the vehicle.** The current `.bio` example has no flight plan, no velocity or acceleration limits and no model of the dynamics. The earlier claims "formally verified flight model", "Digital Twin" and "mathematically guaranteed to remain within physical bounds" are withdrawn.
* **Immunity to electronic warfare is not claimed.** A system that ignores GNSS is not affected by GNSS spoofing, but it is limited by the INS error and by every other sensor it still relies on.
* **Latency.** Only the decision step was measured (emulator instruction counts, estimated 2-4 µs). A switch of navigation source involves the flight controller; no time for that was measured, and no "nanosecond fail-over" has been shown (no FPGA implementation exists here).

Open work: a quantified INS-error bound for a specific sensor, a reaction policy, tests in a software-in-the-loop simulator, then hardware tests.
