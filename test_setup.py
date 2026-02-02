"""
Test script to verify setup and dependencies
"""

import sys

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        import os
        print("✓ os")
    except ImportError as e:
        print(f"✗ os: {e}")
        return False
    
    try:
        import sqlite3
        print("✓ sqlite3")
    except ImportError as e:
        print(f"✗ sqlite3: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError as e:
        print(f"✗ python-dotenv: {e}")
        return False
    
    try:
        from openai import OpenAI
        print("✓ openai")
    except ImportError as e:
        print(f"✗ openai: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow")
    except ImportError as e:
        print(f"✗ Pillow: {e}")
        return False
    
    try:
        import edge_tts
        print("✓ edge-tts")
    except ImportError as e:
        print(f"✗ edge-tts: {e}")
        return False
    
    try:
        import schedule
        print("✓ schedule")
    except ImportError as e:
        print(f"✗ schedule: {e}")
        return False
    
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        print("✓ google-auth-oauthlib")
    except ImportError as e:
        print(f"✗ google-auth-oauthlib: {e}")
        return False
    
    try:
        from googleapiclient.discovery import build
        print("✓ google-api-python-client")
    except ImportError as e:
        print(f"✗ google-api-python-client: {e}")
        return False
    
    print("\nAll imports successful! ✓")
    return True

def test_directories():
    """Test required directories exist"""
    print("\nTesting directories...")
    
    dirs = ['temp_assets', 'logs']
    all_exist = True
    
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/")
        else:
            print(f"✗ {dir_name}/ (missing)")
            all_exist = False
    
    return all_exist

def test_env_file():
    """Test .env file exists"""
    print("\nTesting configuration...")
    
    if os.path.exists('.env'):
        print("✓ .env file exists")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv('LONGCAT_API_KEY'):
            print("✓ LONGCAT_API_KEY is set")
        else:
            print("✗ LONGCAT_API_KEY not found in .env")
            return False
        
        return True
    else:
        print("✗ .env file not found")
        print("  Run: cp .env.example .env")
        return False

def test_modules():
    """Test custom modules can be imported"""
    print("\nTesting custom modules...")
    
    try:
        from db_manager import DBManager
        print("✓ db_manager.py")
    except ImportError as e:
        print(f"✗ db_manager.py: {e}")
        return False
    
    try:
        from topic_manager import TopicManager
        print("✓ topic_manager.py")
    except ImportError as e:
        print(f"✗ topic_manager.py: {e}")
        return False
    
    try:
        from content_generator import ContentGenerator
        print("✓ content_generator.py")
    except ImportError as e:
        print(f"✗ content_generator.py: {e}")
        return False
    
    try:
        from video_producer import VideoProducer
        print("✓ video_producer.py")
    except ImportError as e:
        print(f"✗ video_producer.py: {e}")
        return False
    
    try:
        from youtube_publisher import YouTubePublisher
        print("✓ youtube_publisher.py")
    except ImportError as e:
        print(f"✗ youtube_publisher.py: {e}")
        return False
    
    print("\nAll modules can be imported! ✓")
    return True

def main():
    print("=" * 60)
    print("Kids Educational Content Automation - Setup Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Directories", test_directories()))
    results.append(("Configuration", test_env_file()))
    results.append(("Custom Modules", test_modules()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "PASS ✓" if passed else "FAIL ✗"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! Setup is complete.")
        print("\nNext steps:")
        print("1. Ensure client_secrets.json is in place")
        print("2. Run: python main.py --mode once")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
