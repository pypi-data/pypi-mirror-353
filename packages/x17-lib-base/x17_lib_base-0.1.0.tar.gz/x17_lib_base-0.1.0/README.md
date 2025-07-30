# x_base

**x_base** is the foundational module in the `x17` software ecosystem. 
It provides core abstractions and utilities for time, platform, resource structure, and system interaction — designed to accelerate development across all `x17` projects like `shuli`, `manjusri`, and `celestial`.

---

## Features

- **DateTime Utilities** – Human-friendly duration, timestamp, cron expression helpers.
- **Cross-Platform Support** – Terminal wrappers, path resolvers for macOS, Linux, and Windows.
- **Structured Models** – Semi-structured data containers like `SemiStruct`.
- **AWS Helpers** – Utility classes for interacting with AWS services (Redshift, S3, EC2, etc.).
- **Plug-and-Play Design** – Modular components designed for seamless reuse.

---

## Project Structure
x_base/
├── init.py
├── particle/          # Core functional units (datetime, terminal, semistruct, etc.)

---

## Installation

```bash
pip install x-base
```

## Example Usage
```
from x_base.particle.duration import Duration

d = Duration("2h30m")
print(d.to_minutes())  # 150

```


