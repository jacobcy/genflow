from dotenv import load_dotenv
load_dotenv()

from app import create_app
import os

# 获取Flask应用实例
application = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FRONTEND_PORT', '6060'))
    application.run(port=port)
