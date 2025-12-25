# MetaSpace.bio Specification Files

This directory contains example `.bio` specification files demonstrating the MetaSpace.bio logical metalanguage.

## Available Specifications

### 1. UAV Integrity Shield
**File:** [`uav_integrity_shield.bio`](uav_integrity_shield.bio)

Complete GPS spoofing detection specification for autonomous UAVs. Includes:
- Spatial continuity invariants (GPS-INS divergence monitoring)
- Signal power limit detection
- State machine with Operational, Suspect, and Isolated states

### 2. AF447 Integrity Layer
**File:** [`AF447_Integrity_Layer.bio`](AF447_Integrity_Layer.bio)

Case study specification for Air France 447 pitot tube icing prevention. Demonstrates:
- Triple redundant velocity shield (TRVS)
- Sensor consistency checking
- Deterministic fallback mode

### 3. Financial Trading Integrity
**File:** [`bank.bio`](bank.bio)

Case study specification for high-frequency trading (HFT) glitch prevention. Demonstrates:
- Position size limits (max 20% of balance)
- Rate limiting (max orders per cycle)
- Logic lock activation on invariant violation

### 4. Aircraft Autopilot
**File:** [`repuloautomata.bio`](repuloautomata.bio)

Aircraft autopilot integrity specification.

## Language Reference

For the complete MetaSpace.bio language specification, see:
- [`../docs/technical/FORMAL_SEMANTICS.md`](../docs/technical/FORMAL_SEMANTICS.md)
- [`../README.md`](../README.md#metaspacebio-language-specification)

## Usage

To use these specifications:

1. **Parse and validate:**
   ```bash
   python src/python/metaspace_core_engine.py specs/uav_integrity_shield.bio
   ```

2. **Compile to hardware:**
   ```bash
   # (Future: VHDL synthesis)
   ```

3. **Run simulations:**
   ```bash
   python src/python/simulation/af447_divergence_sim.py  # For AF447 case study
   python examples/example_4_case_studies/financial_trading.py  # For financial case study
   ```

## Contributing

When adding new `.bio` specifications:
- Follow the language syntax defined in `docs/technical/FORMAL_SEMANTICS.md`
- Include comments explaining invariants and state transitions
- Add corresponding test cases in `validation/`

---

**Last Updated:** 2025-12-25

