; MetaSpace SMT-LIB v2.6 Constraint File
; Quadcopter Kinematic Invariants
;
; This file defines kinematic constraints for quadcopter UAVs
; used in GPS spoofing detection via SMT solver (Z3)
;
; Reference: OSIM Patent Pending 20251221-2230
; Author: LemonScript Laboratory

(set-logic QF_NRA)

; ============================================
; VARIABLE DECLARATIONS
; ============================================

; Position (meters)
(declare-fun pos_x () Real)
(declare-fun pos_y () Real)
(declare-fun pos_z () Real)

; Velocity (m/s)
(declare-fun vel_x () Real)
(declare-fun vel_y () Real)
(declare-fun vel_z () Real)

; Acceleration (m/s²)
(declare-fun acc_x () Real)
(declare-fun acc_y () Real)
(declare-fun acc_z () Real)

; GPS measurement (potentially spoofed)
(declare-fun gps_x () Real)
(declare-fun gps_y () Real)
(declare-fun gps_z () Real)

; IMU measurement (trusted)
(declare-fun imu_x () Real)
(declare-fun imu_y () Real)
(declare-fun imu_z () Real)

; Time delta (seconds)
(declare-fun dt () Real)

; ============================================
; QUADCOPTER KINEMATIC PARAMETERS
; ============================================

; Maximum acceleration: 2g = 19.6 m/s²
(define-fun max_acceleration () Real 19.6)

; Maximum velocity: 15 m/s (54 km/h)
(define-fun max_velocity () Real 15.0)

; Maximum turn rate: 45°/s = 0.785 rad/s
(define-fun max_turn_rate () Real 0.785)

; GPS accuracy: ±2.5m (static)
(define-fun gps_accuracy () Real 2.5)

; Maximum divergence: 50m (spoofing threshold)
(define-fun max_divergence () Real 50.0)

; Minimum time step: 0.1s
(define-fun min_dt () Real 0.1)

; Maximum time step: 2.0s
(define-fun max_dt () Real 2.0)

; ============================================
; HELPER FUNCTIONS
; ============================================

; Euclidean distance
(define-fun distance ((x1 Real) (y1 Real) (z1 Real) 
                      (x2 Real) (y2 Real) (z2 Real)) Real
  (sqrt (+ (* (- x1 x2) (- x1 x2))
           (* (- y1 y2) (- y1 y2))
           (* (- z1 z2) (- z1 z2)))))

; Velocity magnitude
(define-fun velocity_magnitude () Real
  (sqrt (+ (* vel_x vel_x) (* vel_y vel_y) (* vel_z vel_z))))

; Acceleration magnitude
(define-fun acceleration_magnitude () Real
  (sqrt (+ (* acc_x acc_x) (* acc_y acc_y) (* acc_z acc_z))))

; ============================================
; KINEMATIC INVARIANTS
; ============================================

; Constraint 1: Maximum acceleration
(assert (<= acceleration_magnitude max_acceleration))

; Constraint 2: Maximum velocity
(assert (<= velocity_magnitude max_velocity))

; Constraint 3: Position change limit (velocity * time)
(assert (<= (distance pos_x pos_y pos_z 
                      (+ pos_x (* vel_x dt))
                      (+ pos_y (* vel_y dt))
                      (+ pos_z (* vel_z dt)))
             (* max_velocity dt)))

; Constraint 4: GPS-IMU divergence limit
(assert (<= (distance gps_x gps_y gps_z imu_x imu_y imu_z)
            max_divergence))

; Constraint 5: GPS accuracy bound
(assert (<= (distance gps_x gps_y gps_z pos_x pos_y pos_z)
            gps_accuracy))

; Constraint 6: Time step bounds
(assert (and (>= dt min_dt) (<= dt max_dt)))

; ============================================
; SPOOFING DETECTION QUERY
; ============================================

; If GPS measurement violates kinematic constraints,
; the system is UNSAT (spoofing detected)

; Example query: Check if GPS position at (100, 100, 10) is valid
; given IMU position at (50, 50, 10) and velocity constraints

; (assert (= gps_x 100.0))
; (assert (= gps_y 100.0))
; (assert (= gps_z 10.0))
; (assert (= imu_x 50.0))
; (assert (= imu_y 50.0))
; (assert (= imu_z 10.0))
; (assert (= dt 1.0))

; (check-sat)
; Expected: UNSAT (spoofing detected - divergence > 50m)

; ============================================
; NOTES
; ============================================

; This is a simplified constraint model.
; Real implementation includes:
; - Temporal constraints (rate of change)
; - Sensor noise models
; - Aircraft-specific parameters
; - Environmental factors (wind, etc.)

; See docs/ARCHITECTURE.md for full architecture
; See docs/LIMITATIONS.md for limitations

