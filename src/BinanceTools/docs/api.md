#查询代币信息
- GET /bapi/defi/v1/public/wallet-direct/buw/wallet/cex/alpha/all/token/list
- 响应体
```json
{
    "code": "000000",
    "message": null,
    "messageDetail": null,
    "data": [
        {
            "tokenId": "C6D574F70EEC6F03723B866820A91B6D",
            "chainId": "56",
            "chainIconUrl": "https://bin.bnbstatic.com/image/admin_mgs_image_upload/20250228/d0216ce4-a3e9-4bda-8937-4a6aa943ccf2.png",
            "chainName": "BSC",
            "contractAddress": "0x477c2c0459004e3354ba427fa285d7c053203c0e",
            "name": "Bitlight Labs",
            "symbol": "LIGHT",
            "iconUrl": "https://bin.bnbstatic.com/images/web3-data/public/token/logos/316b3084c05f40dfbe1d2dd5b6b7629f.png",
            "price": "0.85217540430661152543",
            "percentChange24h": "-7.72",
            "volume24h": "63391275.6320320444882941718",
            "marketCap": "36692092.52231845",
            "fdv": "357913669.80877684",
            "liquidity": "2069913.188505200304595",
            "totalSupply": "420000000",
            "circulatingSupply": "43056972",
            "holders": "13581",
            "decimals": 6,
            "listingCex": false,
            "hotTag": false,
            "cexCoinName": "",
            "canTransfer": false,
            "denomination": 1,
            "offline": false,
            "tradeDecimal": 8,
            "alphaId": "ALPHA_396",
            "offsell": false,
            "priceHigh24h": "1.2480077678965655465",
            "priceLow24h": "0.68812318353483176149",
            "count24h": "142321",
            "onlineTge": false,
            "onlineAirdrop": true,
            "score": 1901,
            "cexOffDisplay": false,
            "stockState": false,
            "listingTime": 1758970800000,
            "mulPoint": 4,
            "bnExclusiveState": false
        },
        {
            "tokenId": "6A40138BA113DE1D2D6A5DE3DDEB4A33",
            "chainId": "56",
            "chainIconUrl": "https://bin.bnbstatic.com/image/admin_mgs_image_upload/20250228/d0216ce4-a3e9-4bda-8937-4a6aa943ccf2.png",
            "chainName": "BSC",
            "contractAddress": "0x5d7909f951436d4e6974d841316057df3a622962",
            "name": "GOAT Network",
            "symbol": "GOATED",
            "iconUrl": "https://bin.bnbstatic.com/images/web3-data/public/token/logos/ba480062df5e44d88c5f63352403dd8e.png",
            "price": "0.097322934906914386518",
            "percentChange24h": "-17.34",
            "volume24h": "21992604.250120290761847536877",
            "marketCap": "10155453.6116667",
            "fdv": "97322934.90691438",
            "liquidity": "1335099.9217653328562806",
            "totalSupply": "1000000000",
            "circulatingSupply": "104348000",
            "holders": "3096",
            "decimals": 18,
            "listingCex": false,
            "hotTag": false,
            "cexCoinName": "",
            "canTransfer": false,
            "denomination": 1,
            "offline": false,
            "tradeDecimal": 8,
            "alphaId": "ALPHA_395",
            "offsell": false,
            "priceHigh24h": "0.15072541308934062543",
            "priceLow24h": "0.091264931663322845916",
            "count24h": "58904",
            "onlineTge": false,
            "onlineAirdrop": true,
            "score": 1901,
            "cexOffDisplay": false,
            "stockState": false,
            "listingTime": 1758963600000,
            "mulPoint": 4,
            "bnExclusiveState": false
        }
    ],
    "success": true
}
```

#查询交易精度信息
-GET https://www.binance.com/bapi/defi/v1/public/alpha-trade/get-exchange-info

#查询交易量
-GET https://native.mokexapp.me/bapi/defi/v1/private/wallet-direct/buw/wallet/today/user-volume
- 响应体
```json
{
  "code": "000000",
  "message": null,
  "messageDetail": null,
  "data": {
    "totalVolume": 604467.9396990947,
    "tradeVolumeInfoList": [
      {
        "icon": "/images/web3-data/public/token/logos/7b5affd8bcac448d94733cf0df62827f.png",
        "tokenName": "ALEO",
        "volume": 604467.9396990947
      }
    ]
  },
  "success": true
}
```

#查询alpha钱包余额
- GET https://native.mokexapp.me/bapi/defi/v1/private/wallet-direct/cloud-wallet/alpha?includeCex=1
- 响应体
```json
{
  "code": "000000",
  "message": null,
  "messageDetail": null,
  "data": {
    "totalValuation": "47.52828923",
    "list": [
      {
        "chainId": "56",
        "contractAddress": "0xff7d6a96ae471bbcd7713af9cb1feeb16cf56b41",
        "cexAsset": false,
        "name": "Bedrock",
        "symbol": "BR",
        "tokenId": "ALPHA_118",
        "free": "0.006657",
        "freeze": "0",
        "locked": "0",
        "withdrawing": "0",
        "amount": "0.006657",
        "valuation": "0.00051714"
      },
      {
        "chainId": "56",
        "contractAddress": "0x0a8d6c86e1bce73fe4d0bd531e1a567306836ea5",
        "cexAsset": false,
        "name": "ChainOpera AI",
        "symbol": "COAI",
        "tokenId": "ALPHA_391",
        "free": "250",
        "freeze": "0",
        "locked": "0",
        "withdrawing": "0",
        "amount": "250",
        "valuation": "47.26643294"
      }
    ]
  },
  "success": true
}
```

#反向订单
- POST https://native.mokexapp.me/bapi/defi/v1/private/alpha-trade/oto-order/place
- 请求体
```json
{
  "workingPrice": "0.22983662",
  "paymentDetails": [
    {
      "amount": "99.99961499",
      "paymentWalletType": "CARD"
    }
  ],
  "pendingPrice": "0.0001",
  "workingSide": "BUY",
  "workingQuantity": "435.09",
  "baseAsset": "ALPHA_373",
  "quoteAsset": "USDT"
}
```
- 响应体 
```json
{
  "code": "000000",
  "message": null,
  "messageDetail": null,
  "data": {
    "workingOrderId": 51398040,
    "pendingOrderId": 51398041
  },
  "success": true
}
```

# 获取ListenKey
-POST /bapi/defi/v1/private/alpha-trade/stream/get-listen-key
-响应体
``` json
{
  "listenKey": "string"
}
```



#websocket 成交记录推送
- wss://nbstream.binance.com/w3w/wsa/stream
- 订阅消息
``` json
{"method":"SUBSCRIBE","params":["came@allTokens@ticker24","alpha_373usdt@aggTrade"],"id":1}
```
- 响应消息
```json
{"id":1}
```

```json
{"stream":"alpha_373usdt@aggTrade","data":{"e":"aggTrade","E":1759043580233,"s":"ALPHA_373USDT","a":798462,"p":"0.22690468","q":"26959.29000000","f":798462,"l":798462,"T":1759043579983,"m":false}}
```

#websocket 订单消息推送
- wss://nbstream.binance.com/w3w/stream
- 订阅消息
```JSON
{"method":"SUBSCRIBE","params":["alpha@ff950c2e0d3da25cb0f320669c3f986f"],"id":2}
```
-响应消息
```json
{"result":null,"id":2}
```

```json
{"stream":"alpha@ff950c2e0d3da25cb0f320669c3f986f","data":{"s":"ALPHA_373USDT","c":"web_164e079573c1491795e1ee245d5ed293","S":"BUY","o":"LIMIT","f":"GTC","q":"869.56000000","p":"0.23000000","ap":"0","P":"0","x":"NEW","X":"NEW","i":"51481849","l":"0","z":"0","L":"0","t":"0","m":false,"ot":"LIMIT","st":1,"O":1759043608334,"Z":"0","Y":"0","Q":"0","ba":"ALPHA_373","qa":"USDT","id":12501197286,"il":"89863105","ct":"OTO","cp":"OTO_WORKING","e":"executionReport","T":1759043608334,"u":1759043608334,"E":1759043608346}}
```

```json
{"stream":"alpha@ff950c2e0d3da25cb0f320669c3f986f","data":{"s":"ALPHA_373USDT","c":"web_732ffda298914d2590743f2d4be9241e","S":"SELL","o":"LIMIT","f":"GTC","q":"0","p":"0.00010000","ap":"0","P":"0","x":"NEW","X":"PENDING","i":"51481850","l":"0","z":"0","L":"0","t":"0","m":false,"ot":"LIMIT","st":1,"O":1759043608334,"Z":"0","Y":"0","Q":"0","ba":"ALPHA_373","qa":"USDT","id":12501197287,"il":"89863105","ct":"OTO","cp":"OTO_PENDING","e":"executionReport","T":1759043608334,"u":1759043608334,"E":1759043608346}}
```

```json
{"stream":"alpha@ff950c2e0d3da25cb0f320669c3f986f","data":{"s":"ALPHA_373USDT","c":"web_164e079573c1491795e1ee245d5ed293","S":"BUY","o":"LIMIT","f":"GTC","q":"869.56000000","p":"0.23000000","ap":"0.226904689","P":"0","x":"TRADE","X":"FILLED","i":"51481849","l":"869.56000000","z":"869.56000000","L":"0.22690469","n":"0.08695600","N":"ALPHA_373","t":"798491","m":false,"ot":"LIMIT","st":1,"O":1759043608334,"Z":"197.30724223","Y":"197.30724223","Q":"0","ba":"ALPHA_373","qa":"USDT","id":12501200714,"il":"89863105","ct":"OTO","cp":"OTO_WORKING","e":"executionReport","T":1759043609181,"u":1759043609181,"E":1759043609340}}
```

```json
{"stream":"alpha@ff950c2e0d3da25cb0f320669c3f986f","data":{"s":"ALPHA_373USDT","c":"web_732ffda298914d2590743f2d4be9241e","S":"SELL","o":"LIMIT","f":"GTC","q":"869.47000000","p":"0.00010000","ap":"0","P":"0","x":"NEW","X":"NEW","i":"51481850","l":"0","z":"0","L":"0","t":"0","m":false,"ot":"LIMIT","st":1,"O":1759043608334,"Z":"0","Y":"0","Q":"0","ba":"ALPHA_373","qa":"USDT","id":12501200716,"il":"89863105","ct":"OTO","cp":"OTO_PENDING","e":"executionReport","T":1759043609181,"u":1759043609181,"E":1759043609341}}
```

```json
{"stream":"alpha@ff950c2e0d3da25cb0f320669c3f986f","data":{"s":"ALPHA_373USDT","c":"web_732ffda298914d2590743f2d4be9241e","S":"SELL","o":"LIMIT","f":"GTC","q":"869.47000000","p":"0.00010000","ap":"0.226904680","P":"0","x":"TRADE","X":"PARTIALLY_FILLED","i":"51481850","l":"200","z":"200","L":"0.22690468","n":"0.00453809","N":"USDT","t":"798492","m":true,"ot":"LIMIT","st":1,"O":1759043608334,"Z":"45.38093600","Y":"45.38093600","Q":"0","ba":"ALPHA_373","qa":"USDT","id":12501205152,"il":"89863105","ct":"OTO","cp":"OTO_PENDING","e":"executionReport","T":1759043610496,"u":1759043610496,"E":1759043610678}}
```

```json
{"stream":"alpha@ff950c2e0d3da25cb0f320669c3f986f","data":{"s":"ALPHA_373USDT","c":"web_732ffda298914d2590743f2d4be9241e","S":"SELL","o":"LIMIT","f":"GTC","q":"869.47000000","p":"0.00010000","ap":"0.226904679","P":"0","x":"TRADE","X":"FILLED","i":"51481850","l":"669.47000000","z":"869.47000000","L":"0.22690468","n":"0.01519059","N":"USDT","t":"798492","m":true,"ot":"LIMIT","st":1,"O":1759043608334,"Z":"197.28681211","Y":"151.90587611","Q":"0","ba":"ALPHA_373","qa":"USDT","id":12501205154,"il":"89863105","ct":"OTO","cp":"OTO_PENDING","e":"executionReport","T":1759043610496,"u":1759043610496,"E":1759043610678}}
```

