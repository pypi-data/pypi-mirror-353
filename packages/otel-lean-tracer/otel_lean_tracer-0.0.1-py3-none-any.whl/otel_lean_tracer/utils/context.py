# Context analysis utilities for measuring context efficiency
# コンテキスト効率測定のためのコンテキスト分析ユーティリティ

import json
from typing import Dict, Any, Optional
import sys


class ContextAnalyzer:
    """
    Utility class for analyzing context usage efficiency
    コンテキスト使用効率を分析するユーティリティクラス
    """
    
    def __init__(self):
        """
        Initialize context analyzer
        コンテキストアナライザーを初期化
        """
        pass
    
    def calculate_context_bytes(self, content: Any) -> int:
        """
        Calculate the byte size of context content
        コンテキストコンテンツのバイトサイズを計算
        """
        if isinstance(content, str):
            return len(content.encode('utf-8'))
        elif isinstance(content, (dict, list)):
            return len(json.dumps(content, ensure_ascii=False).encode('utf-8'))
        elif hasattr(content, '__dict__'):
            return len(str(content).encode('utf-8'))
        else:
            return sys.getsizeof(content)
    
    def estimate_useful_bytes(
        self,
        total_context: Any,
        response: str,
        similarity_threshold: float = 0.3
    ) -> int:
        """
        Estimate useful context bytes based on response content
        レスポンス内容に基づいて有用なコンテキストバイト数を推定
        
        This is a simplified estimation. In a real implementation,
        you might use more sophisticated NLP techniques.
        これは簡略化された推定です。実際の実装では、
        より洗練されたNLP技術を使用する可能性があります。
        """
        total_bytes = self.calculate_context_bytes(total_context)
        
        if not response or not total_context:
            return 0
        
        # Simple heuristic: if response is substantial, assume higher context usage
        # 簡単なヒューリスティック：レスポンスが充実していれば、より高いコンテキスト使用率を仮定
        response_length = len(response)
        
        if response_length < 50:  # Very short response
            return int(total_bytes * 0.1)
        elif response_length < 200:  # Short response
            return int(total_bytes * 0.3)
        elif response_length < 500:  # Medium response
            return int(total_bytes * 0.5)
        elif response_length < 1000:  # Long response
            return int(total_bytes * 0.7)
        else:  # Very long response
            return int(total_bytes * 0.9)
    
    def analyze_context_efficiency(
        self,
        total_bytes: int,
        useful_bytes: int
    ) -> Dict[str, Any]:
        """
        Analyze context efficiency and provide insights
        コンテキスト効率を分析し、洞察を提供
        """
        if total_bytes == 0:
            return {
                "efficiency_ratio": 0.0,
                "efficiency_percentage": 0.0,
                "waste_bytes": 0,
                "classification": "no_context",
                "recommendations": ["No context was provided"]
            }
        
        efficiency_ratio = useful_bytes / total_bytes
        efficiency_percentage = efficiency_ratio * 100
        waste_bytes = total_bytes - useful_bytes
        
        # Classify efficiency
        # 効率を分類
        if efficiency_ratio >= 0.8:
            classification = "highly_efficient"
            recommendations = ["Context usage is excellent"]
        elif efficiency_ratio >= 0.6:
            classification = "efficient"
            recommendations = ["Context usage is good", "Consider minor optimizations"]
        elif efficiency_ratio >= 0.4:
            classification = "moderately_efficient"
            recommendations = [
                "Context usage could be improved",
                "Review prompt structure",
                "Remove unnecessary information"
            ]
        elif efficiency_ratio >= 0.2:
            classification = "inefficient"
            recommendations = [
                "Context usage is poor",
                "Significant optimization needed",
                "Consider chunking or filtering context",
                "Review information relevance"
            ]
        else:
            classification = "highly_inefficient"
            recommendations = [
                "Context usage is very poor",
                "Major restructuring needed",
                "Implement context filtering",
                "Use more targeted prompts",
                "Consider using RAG techniques"
            ]
        
        return {
            "efficiency_ratio": efficiency_ratio,
            "efficiency_percentage": efficiency_percentage,
            "waste_bytes": waste_bytes,
            "classification": classification,
            "recommendations": recommendations
        }
    
    def get_waste_category(self, efficiency_ratio: float) -> str:
        """
        Categorize waste type based on Lean principles
        リーン原則に基づいて無駄のタイプを分類
        """
        if efficiency_ratio >= 0.8:
            return "minimal_waste"
        elif efficiency_ratio >= 0.6:
            return "transportation_waste"  # Moving unnecessary information
        elif efficiency_ratio >= 0.4:
            return "inventory_waste"  # Excess information stored
        elif efficiency_ratio >= 0.2:
            return "overprocessing_waste"  # Processing unnecessary data
        else:
            return "overproduction_waste"  # Producing too much context
    
    def suggest_optimizations(
        self,
        total_bytes: int,
        useful_bytes: int,
        context_type: str = "unknown"
    ) -> list:
        """
        Suggest specific optimizations based on context analysis
        コンテキスト分析に基づいて具体的な最適化を提案
        """
        efficiency_ratio = useful_bytes / total_bytes if total_bytes > 0 else 0
        suggestions = []
        
        if efficiency_ratio < 0.5:
            suggestions.extend([
                "Implement semantic chunking to reduce context size",
                "Use vector similarity to filter relevant information",
                "Apply summarization before including in context"
            ])
        
        if total_bytes > 10000:  # Large context
            suggestions.extend([
                "Consider breaking down into smaller, focused contexts",
                "Implement hierarchical context selection",
                "Use compression techniques for repetitive content"
            ])
        
        if context_type == "conversation":
            suggestions.extend([
                "Implement conversation memory with sliding window",
                "Summarize older conversation turns",
                "Focus on recent and relevant exchanges"
            ])
        elif context_type == "document":
            suggestions.extend([
                "Extract key sections only",
                "Use document outline for navigation",
                "Implement progressive disclosure"
            ])
        
        return suggestions