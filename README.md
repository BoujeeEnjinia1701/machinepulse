# MachinePulse

**Area:** Automation · **Status:** Concept · **Prototype budget:** about $80 USD · **Difficulty:** 2 of 5

A clip-on monitor for older machines: current clamp, vibration and temperature sensors report run time, load and early fault signs from lathes, pumps and compressors that have no electronics of their own.

## Concept rationale

Retrofitting is how most of the world's machines will ever become connected.

## Burning platform

Small and medium manufacturers make up most industrial employment but have the least access to predictive maintenance.

## Where it could be used

### By industry

| Industry | Use |
| --- | --- |
| _To be developed_ | |

### By country or region

| Country or region | Why it matters there |
| --- | --- |
| _To be developed_ | |

## What sparked the idea

It came out of a September 2026 review of Design Molecule's applied research areas against the open projects already in the lab. It extends automation into industrial monitoring and feeds TwinKit.

## Problem

Small factories run machines that have no monitoring, so breakdowns arrive without warning and utilization is unknown.

## Concept

A clip-on monitor for older machines: current clamp, vibration and temperature sensors report run time, load and early fault signs from lathes, pumps and compressors that have no electronics of their own.

Full design precis: [docs/02-concept.md](docs/02-concept.md)

## Key components

- Split-core current transformer
- Vibration sensor (accelerometer)
- Surface temperature sensor
- Microcontroller with Wi-Fi or LoRa
- Magnetic mount enclosure
- TwinKit connection

The working bill of materials is in [bom/bom.csv](bom/bom.csv).

## Safety

> Install current clamps only on insulated conductors with the machine isolated; opening electrical cabinets is for qualified people.

## Repository layout

| Folder | Contents |
| --- | --- |
| `docs/` | Problem, concept, requirements, calculations and design decisions |
| `cad/src/` | build123d Python source, the source of truth for all geometry |
| `cad/step/`, `cad/stl/` | Exported models for FreeCAD, other CAD tools and printing |
| `cad/drawings/` | 2D sketches and dimensioned drawings |
| `bom/` | Bill of materials |
| `electronics/` | KiCad schematics and PCB layouts |
| `firmware/` | Microcontroller code |
| `media/` | Renders, perspectives and photos |
| `build-log/` | Dated prototyping notes |

## Licenses

- **Hardware** (CAD, drawings, BOM, electronics): [CERN-OHL-S v2](LICENSE)
- **Software** (firmware, scripts, notebooks): [MIT](LICENSE-SOFTWARE)

A project of the [Design Molecule](https://designmolecule.com) lab. Extending strong areas set.
