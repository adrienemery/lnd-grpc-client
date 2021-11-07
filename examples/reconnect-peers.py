pk = "0219426a5b641ed05ee639bfda80c1e0199182944977686d1dd1ea2dcb89e5dd55"

node_info = ln.lnd.get_node_info(pk, include_channels=False)
all_addresses = node_info.node.addresses
if len(all_addresses) == 1:
    addr_index = 0
else:
    addr_index = 1

ln.lnd.connect_peer(pk, all_addresses[addr_index].addr)
print(f"connected to: {node_info.node.alias}")
ln.list_channels()

for address in all_addresses:
    if "onion" in address.addr:
        tor_address = address.addr