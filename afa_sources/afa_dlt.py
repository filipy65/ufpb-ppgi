import bitcoinlib, json, urllib.request


afa_btc_network_name = "testnet"
afa_btc_wallet_name = "tbtc2"
btc_network_transaction_fee = 10000


def confirm_page_info(dlt_page):
    try:
        blockchain_transaction_info = json.load(urllib.request.urlopen("https://blockstream.info/testnet/api/tx/" + dlt_page['anchors']['txid']))
        info_to_confirm = ('j@' + dlt_page['anchors']['hash']).encode('utf-8')
        return bool(info_to_confirm.hex() == blockchain_transaction_info['vout'][0]['scriptpubkey'] and blockchain_transaction_info['status']['confirmed'])
    except:
        return False


def confirm_page_register(dlt_page):
    try:
        blockchain_transaction_info = json.load(urllib.request.urlopen("https://blockstream.info/testnet/api/tx/" + dlt_page['anchors']['txid']))
        if blockchain_transaction_info['status']['confirmed']:
            dlt_page['anchors']['timestamp'] = blockchain_transaction_info['status']['block_time']
    except:
        pass
    return dlt_page


def register_page(pages_status, dlt_page):
    afa_btc_wallet = bitcoinlib.wallets.wallet_create_or_open(afa_btc_wallet_name, network=afa_btc_network_name)
    afa_btc_wallet.transactions_update()
    
    if afa_btc_wallet.balance() > btc_network_transaction_fee:
        afa_btc_lock_script = bytes("\x6a", "utf-8") + bitcoinlib.encoding.varstr(dlt_page['anchors']['hash'])
        afa_btc_transaction_request = bitcoinlib.transactions.Output(btc_network_transaction_fee, lock_script=afa_btc_lock_script)
        afa_btc_transaction_response = afa_btc_wallet.send([afa_btc_transaction_request])
        dlt_page['anchors']['network'] = afa_btc_transaction_response.as_dict()['network']
        dlt_page['anchors']['txid'] = afa_btc_transaction_response.as_dict()['txid']
        dlt_page['anchors']['add_info'] = afa_btc_transaction_response.as_dict()
        #afa_log.update_file(dlt_page_file, dlt_page)
        
        if dlt_page['id'] not in pages_status['registered_pages_awaiting_confirmation']:
            pages_status['registered_pages_awaiting_confirmation'].append(dlt_page['id'])
            pages_status['not_registered_closed_pages'].remove(dlt_page['id'])
        #afa_log.update_file(pages_status_file, pages_status) # ...update the pages status...
        
        dlt_info = f"<br>Register of page {dlt_page['id']} submited on {afa_btc_network_name}."
        return True, dlt_info, dlt_page, pages_status

    else:
        dlt_info = f"<br>Insufficient balance on wallet '{afa_btc_wallet_name}' for submit transaction on the '{afa_btc_network_name}' network. Add funds to the address '{afa_btc_wallet.addresslist()[0]}' and wait it to be confirmed."
        return False, dlt_info

