#!/usr/bin/env python3
"""
Script demo để test CV Chat Assistant API
"""
import requests
import json


BASE_URL = "http://127.0.0.1:8000"


def test_health():
    """Test health endpoint"""
    print("🔍 Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_suggestions():
    """Test suggestions endpoint"""
    print("💡 Testing /suggestions endpoint...")
    response = requests.get(f"{BASE_URL}/suggestions")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data['suggestions'])} suggestions:")
    for i, suggestion in enumerate(data['suggestions'], 1):
        print(f"  {i}. {suggestion}")
    print()


def test_chat(question: str, include_thinking: bool = True):
    """Test chat endpoint"""
    print(f"💬 Testing /chat with question: '{question}'")
    print(f"   Include thinking: {include_thinking}")
    
    payload = {
        "question": question,
        "include_thinking": include_thinking
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get("thinking"):
            print("\n📝 THINKING PROCESS:")
            print("─" * 60)
            print(data["thinking"])
            print("─" * 60)
        
        print("\n✨ ANSWER:")
        print("─" * 60)
        print(data["answer"])
        print("─" * 60)
    else:
        print(f"Error: {response.text}")
    print()


if __name__ == "__main__":
    print("=" * 70)
    print("CV CHAT ASSISTANT - API TESTING")
    print("=" * 70)
    print()
    
    try:
        # Test 1: Health check
        test_health()
        
        # Test 2: Get suggestions
        test_suggestions()
        
        # Test 3: Chat without thinking
        test_chat("email của bạn là gì?", include_thinking=False)
        
        # Test 4: Chat with thinking (nếu có API key)
        test_chat("Baro có những kỹ năng về AI gì?", include_thinking=True)
        
        # Test 5: Chat với câu hỏi phức tạp
        test_chat("Hãy tóm tắt kinh nghiệm và dự án của Baro", include_thinking=True)
        
    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối đến server!")
        print("   Hãy chắc chắn server đang chạy: python3 main.py")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
