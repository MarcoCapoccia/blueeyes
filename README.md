# Blue-Eyed Islanders Puzzle

## Project Information

**Course:** Logical Aspects of Multi-Agent Systems  
**Institution:** University of Groningen  
**Group:** AND  
**Date:** January 2026

**Team Members:**
- Eli Baho (e.p.baho@student.rug.nl) - s4807103
- Marco Capoccia (m.capoccia@student.rug.nl) - s4807189

## Live Demo

Visit the live demo: [https://marcocapoccia.github.io/BlueEyes/](https://marcocapoccia.github.io/BlueEyes/)

## Running Locally

1. Clone this repository
2. Start a local HTTP server:
   ```bash
   python3 -m http.server 8080
   ```
3. Open your browser and navigate to `http://localhost:8080/`

## Project Structure

```
.
├── index.html              # Main website with tabbed interface
├── README.md               # Project documentation
├── css/
│   └── style.css          # Website styling
├── python/
│   ├── model.py           # Core agent and world model
│   ├── epistemic.py       # Epistemic logic implementation
│   ├── pal.py             # Public Announcement Logic
│   ├── simulator.py       # Simulation engine
│   └── enumerator.py      # State enumeration utilities
├── docs/
│   ├── Introduction.pdf
│   ├── Model.pdf
│   ├── Strategy.pdf
│   ├── Implementation.pdf
│   ├── Results.pdf
│   ├── Discussion.pdf
│   └── References.pdf
└── assets/
    ├── thumbnail.jpg      # Header background image
    └── ruglogo.png        # University logo
```
