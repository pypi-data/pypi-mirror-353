import requests
from typing import Dict, Any

class OrderManager:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    def send_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.post(f'{self.api_url}/orders', json=order, headers=headers)
        return response.json()

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.delete(f'{self.api_url}/orders/{order_id}', headers=headers)
        return response.json()

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f'{self.api_url}/orders/{order_id}', headers=headers)
        return response.json()

    def track_order(self, order_id: str) -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f'{self.api_url}/orders/{order_id}/status', headers=headers)
        return response.json()

    def modify_order(self, order_id: str, modifications: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.put(f'{self.api_url}/orders/{order_id}', json=modifications, headers=headers)
        return response.json()
