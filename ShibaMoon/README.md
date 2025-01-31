# Crypto Scanner

A modular cryptocurrency scanner that analyzes trading opportunities using technical indicators and custom strategies.

## Features

- Modular indicator system
- Pluggable trading strategies
- Support for both spot and futures trading
- Automated report generation
- Real-time market data analysis

## Project Structure

```
ShibaMoon/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── indicators/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── momentum.py
│   │   ├── trend.py
│   │   └── volume.py
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── spot.py
│   │   └── futures.py
│   ├── scanner/
│   │   ├── __init__.py
│   │   └── crypto_scanner.py
│   └── utils/
│       ├── __init__.py
│       └── reporting.py
└── reports/
    └── .gitkeep
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ShibaMoon.git
cd ShibaMoon
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scanner:
```bash
python src/main.py
```

## Adding New Indicators

1. Create a new indicator class in the appropriate category file under `src/indicators/`
2. Inherit from the `Indicator` base class
3. Implement the required methods:
   - `calculate(df: pd.DataFrame) -> pd.DataFrame`
   - `get_name() -> str`
4. Add the new indicator to `src/indicators/__init__.py`
5. Initialize the indicator in `CryptoScanner`

Example:
```python
from .base import Indicator

class NewIndicator(Indicator):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        # Add your indicator calculation logic here
        return df

    def get_name(self) -> str:
        return "NewIndicator"
```

## Adding New Strategies

1. Create a new strategy class in `src/strategies/`
2. Inherit from the `Strategy` base class
3. Implement the required `analyze` method
4. Add the strategy to `src/strategies/__init__.py`
5. Initialize the strategy in `CryptoScanner`

Example:
```python
from .base import Strategy

class NewStrategy(Strategy):
    def analyze(self, df: pd.DataFrame) -> Optional[Dict]:
        # Add your strategy logic here
        return result_dict
```

## Reports

The scanner generates two types of reports in the `reports/` directory:
- Detailed JSON report (`detailed_report_TIMESTAMP.json`)
- Summary text report (`summary_report_TIMESTAMP.txt`)

## License

MIT License 