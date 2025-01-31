import logging
import os
from dotenv import load_dotenv
from .scanner.crypto_scanner import CryptoScanner

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    # 檢查是否輸出 JSON
    no_json = os.environ.get('NO_JSON', '0') == '1'
    
    try:
        scanner = CryptoScanner()
        opportunities = scanner.scan_market(output_json=not no_json)
        
        if opportunities:
            logger.info(f"✨ 找到 {len(opportunities)} 個交易機會！")
        else:
            logger.info("😔 未找到符合條件的交易機會。")
            
    except Exception as e:
        logger.error(f"❌ 程序執行出錯：{str(e)}")
        raise

if __name__ == "__main__":
    main() 