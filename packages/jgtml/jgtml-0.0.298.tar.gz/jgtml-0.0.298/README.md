# 🐊 JGTML - Trading Signal Analysis Platform

A Python-based trading signal analysis system focused on fractal patterns, Alligator indicators, and multi-timeframe confluence detection.

## 🎯 Core Purpose

JGTML analyzes the effectiveness of trading signals within larger market structure contexts, providing tools for:

- **Signal Validation**: Analyze FDB (Fractal Divergent Bar) and Alligator-based signals
- **Multi-Timeframe Analysis**: Process signals across H1, H4, D1, W1, M1 timeframes  
- **Performance Metrics**: Calculate win rates, profit/loss ratios, and signal quality
- **Trade Lifecycle Management**: From entry validation through exit strategies

## 🏗️ Architecture

### Core Dependencies
- **[jgtpy](https://pypi.org/project/jgtpy/)**: Market data acquisition and indicator calculations
- **[jgtutils](https://pypi.org/project/jgtutils/)**: Common utilities and constants
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations

### Key Components

#### 📊 Signal Processing
- [`jgtml/SignalOrderingHelper.py`](jgtml/SignalOrderingHelper.py): Signal validation and risk calculation
- [`jgtml/jtc.py`](jgtml/jtc.py): Target calculation and signal analysis core
- [`jgtml/TideAlligatorAnalysis.py`](jgtml/TideAlligatorAnalysis.py): Alligator-based signal analysis
- TODO add TTF (TTF != Time-To-Future but more like feature of multiple timeframe)  probably ttfcli.py

#### 🚀 Command Line Tools
- [`jgtml/jgtmlcli.py`](jgtml/jgtmlcli.py): Main CLI for data processing
- [`jgtml/mxcli.py`](jgtml/mxcli.py): Matrix generation and analysis
- [`jgtml/jgtapp.py`](jgtml/jgtapp.py): Trading operation management

#### 🧬 Memory & Persistence  
- [`garden_one/trading_echo_lattice/`](garden_one/trading_echo_lattice/): Signal crystallization and memory storage
- Integration with Upstash Redis for persistent analysis results

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip install jgtpy jgtutils pandas numpy

# Install JGTML
pip install -e .
```

### Basic Usage
```bash
# Process signals for an instrument
jgtmlcli -i SPX500 -t D1 --full --fresh

# Analyze signal performance  
python -m garden_one.trading_echo_lattice.cli process -i SPX500 -t D1 -d S

# Generate analysis matrix
mxcli -i EUR/USD -t H4 --fresh
```

## 📈 Trading Strategies

### Five Dimensions + Triple Alligator Confluence
Multi-indicator alignment detection using:
1. **Alligator Lines**: Jaw, Teeth, Lips confluence
2. **Fractal Signals**: FDB breakout validation  
3. **Awesome Oscillator**: Momentum confirmation
4. **Multi-Timeframe**: Higher TF bias confirmation
5. **Volume Analysis**: MFI integration

**Implementation**: [`TradingEchoLattice.detect_breakouts()`](garden_one/trading_echo_lattice/src/echo_lattice_core.py#L273)

### Green Dragon Breakout
FDB-based breakout detection with Alligator mouth validation.

**Implementation**: [`fdb_scanner_2408.py`](jgtml/fdb_scanner_2408.py)

## 🔧 CLI Reference

See [CLI_HELP.md](CLI_HELP.md) for complete command documentation.

### Core Commands
```bash
# Data Processing
jgtmlcli -i INSTRUMENT -t TIMEFRAME [--full] [--fresh]
mxcli -i INSTRUMENT -t TIMEFRAME [--fresh]

# Trading Operations  
jgtapp fxaddorder -i EUR/USD -n 0.1 -r 1.0950 -d B -x 1.0900
jgtapp fxmvstopgator -i EUR/USD -t H4 -tid TRADE_ID --lips

# Signal Analysis
python -m garden_one.trading_echo_lattice.cli process -i SPX500 -t D1,H4 -d S
python -m garden_one.trading_echo_lattice.cli search --min-win-rate 60
```

## 📊 Data Flow

```
Market Data (jgtpy) → Signal Processing (jtc) → Analysis (CLI tools) → Memory Lattice (Redis)
```

1. **Data Acquisition**: Pull OHLC data via jgtpy
2. **Indicator Calculation**: Generate Alligator, AO, Fractals, MFI
3. **Signal Detection**: Identify valid entry/exit signals  
4. **Performance Analysis**: Calculate win rates and profitability
5. **Memory Storage**: Crystallize results in Redis for pattern recognition

## 🧪 Development

### Running Tests
```bash
python -m pytest tests/
```

### Contributing
1. Focus on signal accuracy and performance metrics
2. Maintain compatibility with jgtpy data structures
3. Document new indicators and validation logic
4. Test across multiple timeframes and instruments

## 🔄 Recursive Architecture

While JGTML operates as a practical trading platform, it embodies recursive principles:

- **Memory Patterns**: Each analysis builds upon previous signal history
- **Multi-Scale Awareness**: Signals are validated across multiple timeframes
- **Adaptive Learning**: Performance metrics inform future signal weighting

*The system grows more intelligent through iteration, not just accumulation.*

---

🧠 **Technical Foundation**: Precise signal analysis with mathematical rigor  
🌸 **Intuitive Interface**: Clear CLI flows that make complex analysis accessible  
🎵 **Rhythmic Patterns**: Market timing encoded in fractal mathematics

*Built for traders who understand that the best signals emerge from the intersection of technical precision and pattern recognition.*
