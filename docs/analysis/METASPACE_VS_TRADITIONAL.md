# A divergence gate versus a filter-only autopilot

**Subject:** reaction to GNSS spoofing. This is a reasoned comparison, not a measurement; no autopilot was tested.

## 1. A known weakness of filter-based fusion
Autopilots such as ArduPilot and PX4 fuse GNSS and inertial data with an extended Kalman filter (EKF). A slow spoof ("walking") can be absorbed by the filter's adaptation, so the vehicle follows a wrong position. Autopilots have their own consistency checks and failsafes; their strength varies by configuration, and none were evaluated here.

## 2. What a divergence gate adds
A fixed-threshold check on the distance between the GNSS position and an independent inertial estimate is simple, cheap and easy to verify (this repository: Z3 checks of the specification and the float32 step function; about 144-467 instructions per tick on a soft-float RISC-V core, estimated 2-4 µs at 160 MHz).

| Aspect | Filter-only fusion | Divergence gate |
|---|---|---|
| Basis | probabilistic weighting of sensors | fixed threshold on a physical quantity |
| Spoofing reaction | may adapt to a slow spoof | alarm when the divergence exceeds the limit |
| Verification effort | statistical tests | small enough for solver proofs (shown here) |
| Blind spots | slow spoof absorbed | slow spoof below the threshold, a spoof consistent with the INS, INS drift over long outages, threshold choice |
| Reaction time | not measured | decision in microseconds (estimated); end-to-end time depends on the whole system, not measured |

## 3. What happens during an attack (illustrative)
A spoofer shifts the GNSS position by 100 m. In the first tick the distance exceeds 20 m: the gate moves from `Normal` to `Suspect` and raises the alarm in that same tick. In the next tick the distance still exceeds 50 m and the gate escalates to `Isolated`, which is latched (transition-first semantics, proved at the model level). What the vehicle does afterwards (failsafe, hover, return) is up to the flight controller and is not part of this repository.

## 4. Conclusions that can be drawn
* A divergence gate is a reasonable, cheap complement to a filter. It does not make a vehicle "unable to crash" and does not give immunity to electronic warfare: it detects a certain class of inconsistency.
* Claims such as "MetaSpace can only be defeated by physical force" and "a MetaSpace-equipped machine cannot crash due to false sensor values" in earlier versions were not supported and are withdrawn.
