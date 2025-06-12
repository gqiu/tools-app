import json
import requests
from sseclient import SSEClient
from typing import Optional, Dict, List

class DeepResearchAPI:
    def __init__(self, base_url: str, access_password: Optional[str] = None):
        """
        Initialize the DeepSearch API client
        
        Args:
            base_url (str): The base URL of the API
            access_password (Optional[str]): Access password if required
        """
        self.base_url = base_url.rstrip('/')
        self.access_password = access_password

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.access_password:
            headers["Authorization"] = f"Bearer {self.access_password}"
        return headers

    def search(self, 
              query: str,
              provider: str,
              thinking_model: str,
              task_model: str,
              search_provider: str,
              language: Optional[str] = "zh-cn",
              max_result: Optional[int] = 5,
              enable_citation_image: Optional[bool] = True,
              enable_references: Optional[bool] = True,
              callback=None):
        """
        Perform a deep search with streaming response handling
        
        Args:
            query (str): Research topic
            provider (str): AI provider (google, openai, anthropic, etc.)
            thinking_model (str): Thinking model ID
            task_model (str): Task model ID
            search_provider (str): Search provider (model, tavily, etc.)
            language (Optional[str]): Response language
            max_result (Optional[int]): Maximum number of search results
            enable_citation_image (Optional[bool]): Include content-related images
            enable_references (Optional[bool]): Include citation links
            callback: Optional callback function for event handling
        """
        url = f"{self.base_url}/api/sse"
        
        # Prepare request body
        body = {
            "query": query,
            "provider": provider,
            "thinkingModel": thinking_model,
            "taskModel": task_model,
            "searchProvider": search_provider
        }

        # Add optional parameters if provided
        if language is not None:
            body["language"] = language
        if max_result is not None:
            body["maxResult"] = max_result
        if enable_citation_image is not None:
            body["enableCitationImage"] = enable_citation_image
        if enable_references is not None:
            body["enableReferences"] = enable_references

        # Make POST request with streaming response
        response = requests.post(
            url, 
            json=body,
            headers=self._get_headers(),
            stream=True
        )
        
        # Create SSE client from response
        client = SSEClient(response)
        
        # Process events
        results = []
        start=False
        try:
            for event in client.events():
                if event.event == "progress":
                    print(f"Progress: {event.event}, Data: {event.data}")
                if event.event == "progress" and event.data == '{"step":"final-report","status":"start"})}':
                    start = True
                    continue
                if start:
                    if event.event == "message":
                        data = event.data[:-2] # Remove trailing '})'
                        data = json.loads(data)
                        results.append(data['text'])
        finally:
            response.close()
        print("Final results received.")
        print("Final results size:", len(results))
        final_result = ''.join(results)
        if final_result != '':
           final_result.strip()
           # remove <final-report> and </final-report>  
           final_result = final_result.replace('<final-report>', '').replace('</final-report>', '') 
        final_result.strip()
        return final_result

def format_final_result(result: str) -> str:
    if result != '':
       result=result.strip()
      # remove <final-report> and </final-report>  
       result = result.replace('<final-report>', '').replace('</final-report>', '') 
    return result.strip()

def example_callback(event_type: str, data: Dict):
    """Example callback function to handle SSE events"""
    print(f"Event Type: {event_type}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print("-" * 50)

def example_usage():
    """Example usage of the DeepSearchAPI class"""
    # Initialize client
    api = DeepResearchAPI(
        base_url="https://deep-search.qiulanfang.uk"
    )
    
    # Perform search with callback
    api.search(
        query="eBay最新财报分析，关注公司利润，市场反应，行业趋势，政策影响，风险分析，用于股票中短期投资分析，数据可以用表格展示。",
        provider="google",
        thinking_model="gemini-2.0-flash-thinking-exp",
        task_model="gemini-2.0-flash-exp",
        search_provider="model",
        language="zh-cn",
        max_result=5,
        enable_citation_image=True,
        enable_references=True,
        callback=example_callback
    )

if __name__ == "__main__":
   final_str="<final-report>\n📈# eBay投资价值。\n</final-report>\n\n"
   print(format_final_result(final_str))
   pass
   # example_usage()
