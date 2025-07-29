# Cost calculation utilities for LLM API calls
# LLM API呼び出しのコスト計算ユーティリティ

from typing import Dict, Optional
import os


class CostCalculator:
    """
    Utility class for calculating LLM API costs
    LLM APIコストを計算するユーティリティクラス
    """
    
    # Default pricing per 1K tokens (USD)
    # デフォルト価格（1Kトークンあたり、USD）
    DEFAULT_PRICING = {
        "openai": {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        },
        "anthropic": {
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
        },
        "google": {
            "gemini-pro": {"input": 0.0005, "output": 0.0015},
            "gemini-pro-vision": {"input": 0.0005, "output": 0.0015},
        },
    }
    
    def __init__(self, custom_pricing: Optional[Dict] = None):
        """
        Initialize cost calculator with optional custom pricing
        カスタム価格設定を使用してコスト計算機を初期化
        """
        self.pricing = self.DEFAULT_PRICING.copy()
        if custom_pricing:
            self._merge_pricing(custom_pricing)
        
        # Load pricing from environment variables
        # 環境変数から価格を読み込み
        self._load_env_pricing()
    
    def _merge_pricing(self, custom_pricing: Dict) -> None:
        """
        Merge custom pricing with default pricing
        カスタム価格設定をデフォルト価格設定とマージ
        """
        for provider, models in custom_pricing.items():
            if provider not in self.pricing:
                self.pricing[provider] = {}
            self.pricing[provider].update(models)
    
    def _load_env_pricing(self) -> None:
        """
        Load pricing from environment variables
        環境変数から価格設定を読み込み
        
        Format: OTEL_LEAN_PRICE_{PROVIDER}_{MODEL}_INPUT=0.001
                OTEL_LEAN_PRICE_{PROVIDER}_{MODEL}_OUTPUT=0.002
        """
        for key, value in os.environ.items():
            if key.startswith("OTEL_LEAN_PRICE_"):
                try:
                    parts = key.replace("OTEL_LEAN_PRICE_", "").split("_")
                    if len(parts) >= 3:
                        provider = parts[0].lower()
                        token_type = parts[-1].lower()  # input or output
                        model = "_".join(parts[1:-1]).lower()
                        
                        if provider not in self.pricing:
                            self.pricing[provider] = {}
                        if model not in self.pricing[provider]:
                            self.pricing[provider][model] = {}
                        
                        self.pricing[provider][model][token_type] = float(value)
                except (ValueError, IndexError):
                    continue
    
    def calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate the total cost for API call
        API呼び出しの総コストを計算
        """
        provider = provider.lower()
        model = model.lower()
        
        # Get pricing for the model
        # モデルの価格を取得
        model_pricing = self._get_model_pricing(provider, model)
        if not model_pricing:
            return 0.0
        
        # Calculate input and output costs
        # 入力と出力のコストを計算
        input_cost = (input_tokens / 1000) * model_pricing.get("input", 0.0)
        output_cost = (output_tokens / 1000) * model_pricing.get("output", 0.0)
        
        return input_cost + output_cost
    
    def _get_model_pricing(self, provider: str, model: str) -> Optional[Dict[str, float]]:
        """
        Get pricing for a specific provider and model
        特定のプロバイダーとモデルの価格を取得
        """
        if provider not in self.pricing:
            return None
        
        provider_pricing = self.pricing[provider]
        
        # Try exact match first
        # 完全一致を最初に試行
        if model in provider_pricing:
            return provider_pricing[model]
        
        # Try partial matches for model variants
        # モデルバリアントの部分一致を試行
        for pricing_model in provider_pricing:
            if model.startswith(pricing_model) or pricing_model in model:
                return provider_pricing[pricing_model]
        
        return None
    
    def get_supported_models(self) -> Dict[str, list]:
        """
        Get list of supported providers and models
        サポートされているプロバイダーとモデルの一覧を取得
        """
        return {
            provider: list(models.keys())
            for provider, models in self.pricing.items()
        }
    
    def add_custom_model(
        self,
        provider: str,
        model: str,
        input_price: float,
        output_price: float
    ) -> None:
        """
        Add custom model pricing
        カスタムモデル価格を追加
        """
        provider = provider.lower()
        model = model.lower()
        
        if provider not in self.pricing:
            self.pricing[provider] = {}
        
        self.pricing[provider][model] = {
            "input": input_price,
            "output": output_price
        }