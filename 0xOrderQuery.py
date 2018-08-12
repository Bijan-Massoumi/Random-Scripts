from sha3 import keccak_256
import json
import urllib.request
import ssl
import eth_abi
from eth_utils import decode_hex


def format_raw_data(logs,event_name):
    abi = json.loads(json.loads(open("./0x_abi.json").read())['result'])
    types = []
    names = []
    indexed_types = []
    indexed_names = []
    for elem in abi:
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



def get_logs_by_block_range(fromNum, toNum):
    order_fill_topic = keccak_256(b"LogFill(address,address,address,address,address,uint256,"
                                      b"uint256,uint256,uint256,bytes32,bytes32)").hexdigest()
    contract_address = "0x12459C951127e0c374FF9105DdA097662A027093"
    api_url = "https://api.infura.io/v1/jsonrpc/mainnet/eth_getLogs?"
    filter_json = 'params=[{{"address":"{}","fromBlock":"{}","toBlock":"{}","topics":["0x{}"]}}]'
    request_string = api_url + filter_json.format(contract_address, hex(fromNum), hex(toNum),order_fill_topic)
    context = ssl._create_unverified_context()
    response = json.loads(urllib.request.urlopen(request_string,context=context).read())
    return format_raw_data(response['result'],"LogFill") if 'result' in response else []


if __name__ == "__main__":
    print(get_logs_by_block_range(6108695, 6108695))
