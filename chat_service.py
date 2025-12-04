import json
import os
from dotenv import load_dotenv
import openai
import logging
from typing import Any

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DeepSeekService:
    """DeepSeek API integration for Azure OpenAI."""
    
    def __init__(self):
        # Khởi tạo OpenAI client với Azure config
        self.api_key = os.getenv("AZURE_API_KEY")
        if self.api_key:
            self.client = openai.OpenAI(
                base_url="https://cloudptit.services.ai.azure.com/openai/v1/",
                api_key=self.api_key,
            )
            self.model = "DeepSeek-V3-0324"
        else:
            self.client = None
            logger.warning("AZURE_API_KEY not found. DeepSeek API will not be available.")

    def generate_response(self, prompt: str, include_thinking: bool = True) -> dict:
        """Generate response with optional thinking process.
        
        Returns:
            dict with 'thinking' and 'answer' keys
        """
        if not self.client:
            raise Exception("DeepSeek API client not initialized. Please set AZURE_API_KEY.")
        
        try:
            logger.info("Sending request to DeepSeek API")
            
            system_prompt = """Bạn là trợ lý AI chuyên về CV của Nguyễn Hồng Phong.

QUAN TRỌNG - Format trả lời:
1. Phần THINKING (bắt buộc):
<think>
🔍 Phân tích câu hỏi: [phân tích ý định người dùng]
📋 Thông tin liên quan: [liệt kê thông tin từ CV]
💡 Kết luận: [tổng hợp câu trả lời]
</think>

2. Phần ANSWER (bắt buộc):
<answer>
[Câu trả lời ngắn gọn, súc tích cho người dùng]
</answer>

Yêu cầu:
- BẮT BUỘC phải có cả hai phần <think> và <answer>
- Trả lời bằng tiếng Việt
- Thinking để phân tích, answer để trả lời người dùng"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )

            # DeepSeek-R1 may return reasoning in message content or separate field
            message = response.choices[0].message
            full_content = message.content
            
            # Log full response structure for debugging
            logger.info(f"=== RESPONSE DEBUG ===")
            logger.info(f"Message type: {type(message)}")
            logger.info(f"Message dict: {message.model_dump() if hasattr(message, 'model_dump') else 'N/A'}")
            logger.info(f"Full content length: {len(full_content)} chars")
            logger.info(f"Content preview:\n{full_content[:500]}...")
            logger.info(f"=== END DEBUG ===")
            
            # Check if there's a reasoning_content field (DeepSeek-R1 specific)
            thinking = ""
            answer = full_content
            
            # Try to get thinking from various possible fields
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                thinking = message.reasoning_content
                logger.info("✓ Found thinking in reasoning_content field")
                
                # If we have reasoning_content, extract clean answer from content
                # Remove <answer> tags if present
                import re
                answer_match = re.search(r'<answer>(.*?)</answer>', full_content, re.DOTALL | re.IGNORECASE)
                if answer_match:
                    answer = answer_match.group(1).strip()
                    logger.info("✓ Extracted clean answer from <answer> tags")
                else:
                    # Remove any remaining tags
                    answer = re.sub(r'</?answer>', '', full_content).strip()
                    
            elif hasattr(message, 'tool_calls') and message.tool_calls:
                # Sometimes reasoning is in tool_calls
                thinking = str(message.tool_calls)
                logger.info("✓ Found thinking in tool_calls")
            
            # If no separate field, try to parse from content
            # If no separate field, try to parse from content
            if not thinking:
                # Method 1: Extract from <think> and <answer> tags
                import re
                think_match = re.search(r'<think>(.*?)</think>', full_content, re.DOTALL | re.IGNORECASE)
                answer_match = re.search(r'<answer>(.*?)</answer>', full_content, re.DOTALL | re.IGNORECASE)
                
                if think_match and answer_match:
                    thinking = think_match.group(1).strip()
                    answer = answer_match.group(1).strip()
                    logger.info("Extracted thinking and answer from XML tags")
                else:
                    # Method 2: Try to split by markers
                    if "🔍" in full_content or "💭" in full_content:
                        # Split by common answer markers
                        for marker in ["<answer>", "**Câu trả lời:**", "Câu trả lời:", "Answer:", "\n\n---\n", "\n\n**"]:
                            if marker in full_content:
                                parts = full_content.split(marker, 1)
                                if len(parts) == 2:
                                    thinking = parts[0].strip()
                                    answer = parts[1].strip()
                                    logger.info(f"Split by marker: {marker}")
                                    break
                    
                    # Method 3: Check for paragraph structure with thinking indicators
                    if not thinking and "\n\n" in full_content:
                        lines = full_content.split("\n")
                        # Look for thinking indicators in first half
                        thinking_lines = []
                        answer_lines = []
                        in_answer = False
                        
                        for line in lines:
                            if any(indicator in line for indicator in ["🔍", "📋", "💡", "💭", "Think:", "Thinking:"]):
                                thinking_lines.append(line)
                            elif line.strip().startswith("**") and thinking_lines:
                                # Bold text after thinking might be answer
                                in_answer = True
                                answer_lines.append(line)
                            elif in_answer or (not thinking_lines and line.strip()):
                                answer_lines.append(line)
                            elif thinking_lines:
                                thinking_lines.append(line)
                        
                        if thinking_lines:
                            thinking = "\n".join(thinking_lines).strip()
                            answer = "\n".join(answer_lines).strip() if answer_lines else full_content
                            logger.info("Extracted from line-by-line analysis")
            
            # Fallback: if still empty thinking, try to detect reasoning patterns
            if not thinking and len(full_content) > 200:
                # If response is long and has multiple paragraphs, first part might be thinking
                paragraphs = [p.strip() for p in full_content.split("\n\n") if p.strip()]
                if len(paragraphs) >= 2:
                    # Heuristic: if first paragraph has analytical language
                    first_para = paragraphs[0].lower()
                    if any(word in first_para for word in ["phân tích", "xem xét", "dựa trên", "từ cv", "theo như"]):
                        thinking = paragraphs[0]
                        answer = "\n\n".join(paragraphs[1:])
                        logger.info("Extracted thinking from heuristic analysis")
            
            # Final fallback
            if not answer or answer == full_content:
                # If we couldn't separate, put everything in answer
                if not thinking:
                    answer = full_content
                    logger.warning("Could not extract separate thinking, full content in answer")
            
            return {
                "thinking": thinking if include_thinking else "",
                "answer": answer
            }

        except Exception as e:
            logger.error(f"Error calling DeepSeek API: {str(e)}")
            raise Exception(str(e))


class CVChatService:
    """CV-based chat responder with DeepSeek API integration.

    - Loads `data.json` from the project root.
    - Uses DeepSeek API if AZURE_API_KEY is configured.
    - Falls back to keyword mapping and substring search if API unavailable.
    """

    def __init__(self, data_path: str = "data.txt"):
        self.data_path = data_path
        self.data = self._load_data()
        self.flat_text = self._build_flat_text()
        self.deepseek = DeepSeekService()

    def _load_data(self) -> Any:
        """Load CV data from TXT file."""
        if not os.path.exists(self.data_path):
            logger.error(f"{self.data_path} not found")
            return {}
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"raw_text": content}

    def _build_flat_text(self) -> str:
        """Build flat text representation of CV data."""
        return self.data.get("raw_text", "")

    def generate_response(self, question: str, include_thinking: bool = True) -> dict:
        """Generate response with optional thinking process.
        
        Returns:
            dict with 'thinking' and 'answer' keys
        """
        q = question.strip().lower()
        if not q:
            return {"thinking": "", "answer": "Vui lòng gửi câu hỏi liên quan đến CV."}
        
        # Try DeepSeek API first if available
        if self.deepseek.client:
            try:
                # Build context from CV data
                cv_context = f"CV Information:\n{self.flat_text}\n\nQuestion: {question}"
                response = self.deepseek.generate_response(cv_context, include_thinking)
                return response
            except Exception as e:
                error_msg = str(e)
                logger.error(f"DeepSeek API failed: {error_msg}")
                
                # Check if it's an auth error
                if "401" in error_msg or "Auth" in error_msg or "validation failed" in error_msg:
                    return {
                        "thinking": "",
                        "answer": "❌ Lỗi xác thực API: API key không hợp lệ hoặc đã hết hạn. Vui lòng kiểm tra lại AZURE_API_KEY trong file .env"
                    }
                
                # Other API errors
                return {
                    "thinking": "",
                    "answer": f"❌ Lỗi khi gọi API: {error_msg}. Vui lòng thử lại sau."
                }
        
        # No API client available
        return {
            "thinking": "",
            "answer": "⚠️ Chưa cấu hình AZURE_API_KEY. Vui lòng thêm API key vào file .env để sử dụng trợ lý AI.\n\nHướng dẫn:\n1. Tạo file .env\n2. Thêm dòng: AZURE_API_KEY=your_key_here\n3. Khởi động lại server"
        }
    
    def get_suggested_questions(self) -> list:
        """Generate suggested questions using LLM based on CV content."""
        if not self.deepseek.client:
            return [
                "⚠️ Chưa cấu hình API key. Không thể tạo câu hỏi gợi ý.",
                "Vui lòng thêm AZURE_API_KEY vào file .env để sử dụng tính năng này."
            ]
        
        try:
            prompt = f"""Dựa trên thông tin CV sau đây, hãy tạo ra 10 câu hỏi gợi ý thú vị và đa dạng mà người dùng có thể hỏi về CV này.

CV Information:
{self.flat_text}

Yêu cầu:
- Tạo đúng 10 câu hỏi
- Câu hỏi phải đa dạng: kỹ năng, kinh nghiệm, dự án, mục tiêu, học vấn, sở thích, v.v.
- Câu hỏi ngắn gọn, rõ ràng, hấp dẫn
- Bằng tiếng Việt
- Trả về ĐÚNG FORMAT JSON: ["câu hỏi 1", "câu hỏi 2", ...]
- KHÔNG thêm bất kỳ text nào khác ngoài JSON array"""

            response = self.deepseek.generate_response(prompt, include_thinking=False)
            answer_text = response.get("answer", "")
            
            # Extract JSON array from response
            import re
            # Try to find JSON array in the response
            json_match = re.search(r'\[.*\]', answer_text, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group(0))
                if isinstance(suggestions, list) and len(suggestions) >= 5:
                    logger.info(f"Generated {len(suggestions)} suggestions from LLM")
                    return suggestions[:10]  # Return max 10
            
            logger.error("LLM response format invalid")
            return [
                "❌ Lỗi: Không thể tạo câu hỏi gợi ý (định dạng không hợp lệ)",
                "Vui lòng thử lại sau."
            ]
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to generate suggestions from LLM: {error_msg}")
            
            if "401" in error_msg or "Auth" in error_msg:
                return [
                    "❌ Lỗi xác thực API: API key không hợp lệ",
                    "Vui lòng kiểm tra lại AZURE_API_KEY trong file .env"
                ]
            
            return [
                f"❌ Lỗi khi tạo gợi ý: {error_msg}",
                "Vui lòng thử lại sau."
            ]


# Singleton instance
deepseek_service = DeepSeekService()
