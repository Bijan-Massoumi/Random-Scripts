from sha3 import keccak_256
import json
import urllib.request
import ssl
import eth_abi
from eth_utils import decode_hex

class LogCollector:

    def __init__(self, contract_address, abi_json):
        self.contract_address = contract_address
        self.abi = json.load(open(abi_json))
        

    def format_raw_data(self, logs, event_name):
        types = []
        names = []
        indexed_types = []
        indexed_names = []
        for elem in self.abi:
            if 'name' in elem and elem['name'] == event_name:
                for input in elem['inputs']:
                    if input['indexed']:
                        indexed_types.append(input["type"])
                        indexed_names.append(input["name"])
                    else:
                        types.append(input["type"])
                        names.append(input["name"])
                break

        return_list = []
        for log in logs:
            encoded_topics = list(map(lambda x: decode_hex(x), log['topics'][1:]))
            indexed_values = [eth_abi.decode_single(t, v) for t, v in zip(indexed_types, encoded_topics)]
            values = eth_abi.decode_abi(types, decode_hex(log['data']))
            next_dict = dict(zip(indexed_names + names, indexed_values + list(values)))
            next_dict["blockNumber"] = log['blockNumber']
            return_list.append(next_dict)

        return return_list



    def get_logs_by_block_range(self, fromNum, toNum, event_sig):
        order_fill_topic = keccak_256(self.event_to_topic(event_sig)).hexdigest()
        api_url = "https://api.infura.io/v1/jsonrpc/mainnet/eth_getLogs?"
        filter_json = 'params=[{{"address":"{}","fromBlock":"{}","toBlock":"{}","topics":["0x{}"]}}]'
        request_string = api_url + filter_json.format(self.contract_address, hex(fromNum), hex(toNum),order_fill_topic)
        context = ssl._create_unverified_context()
        response = json.loads(urllib.request.urlopen(request_string,context=context).read())
        return self.format_raw_data(response['result'], event_sig.split("(")[0]) if 'result' in response else []

        
    def event_to_topic(self, event_text):
        param_begin = event_text.find("(")
        parameters = event_text[param_begin:]
        
        types = []
        for param in parameters.split(","):
            types.append(param.split()[0])
        return bytes(event_text[:param_begin] + ",".join(types) + ")", 'utf8')

if __name__ == "__main__":
    """contract_address = "0x12459C951127e0c374FF9105DdA097662A027093"
    abi_path = "./0x_abi.json"
    obj = LogCollecter(contract_address, abi_path)
    out = obj.get_logs_by_block_range(6108695, 6108695, b"LogFill(address,address,address,address,address,uint256,"
                                          b"uint256,uint256,uint256,bytes32,bytes32)" )
    """
    contract_address = "0x75228dce4d82566d93068a8d5d49435216551599"
    abi_path = "./augur_abi.json"
    obj = LogCollector(contract_address, abi_path)
    event = 'OrderFilled(address indexed universe, address indexed shareToken, address filler, bytes32 orderId, uint256 numCreatorShares, uint256 numCreatorTokens, uint256 numFillerShares, uint256 numFillerTokens, uint256 marketCreatorFees, uint256 reporterFees, uint256 amountFilled, bytes32 tradeGroupId)'
    print(obj.get_logs_by_block_range(7942147, 7942147, event))