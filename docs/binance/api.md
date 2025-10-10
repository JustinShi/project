#查询交易量
-GET /bapi/defi/v1/private/wallet-direct/buw/wallet/today/user-volume
-响应体
```响应成功json
{
  "code": "000000",
  "message": null,
  "messageDetail": null,
  "data": {
    "totalVolume": 197.43566840519998,
    "tradeVolumeInfoList": [
      {
        "icon": "/images/web3-data/public/token/logos/2B8C050763AA46D003997E55EEF92A15.png",
        "tokenName": "AITECH",
        "volume": 197.43566840519998
      }
    ]
  },
  "success": true
}
```

```登录失败json
{
    "code": "100002001",
    "message": "登录状态已经失效，请重新登录！",
    "success": false
}
```

#查询代币信息
- GET /bapi/defi/v1/public/alpha-trade/aggTicker24?dataType=aggregate
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
      "price": "0.92207942985659043632",
      "percentChange24h": "-13.60",
      "volume24h": "92337367.987163773328517135635",
      "marketCap": "39701948.19311117",
      "fdv": "387273360.53976798",
      "liquidity": "2097717.9456696158616323",
      "totalSupply": "420000000",
      "circulatingSupply": "43056972",
      "holders": "10291",
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
      "priceHigh24h": "1.1927171162392443752",
      "priceLow24h": "0.75348175706405345686",
      "count24h": "262679",
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
      "tokenId": "F5286563D58FB0D0705EEE5CC369982A",
      "chainId": "8453",
      "chainIconUrl": "https://bin.bnbstatic.com/image/admin_mgs_image_upload/20250227/f9f5b212-4e34-44da-8230-65608cee4b22.png",
      "chainName": "Base",
      "contractAddress": "0x4f9fd6be4a90f2620860d680c0d4d5fb53d1a825",
      "name": "aixbt by Virtuals",
      "symbol": "AIXBT",
      "iconUrl": "https://bin.bnbstatic.com/images/web3-data/public/token/logos/dba6135dfe834907ac0b768c5e1acb6c.png",
      "price": "0.092698092779279334004",
      "percentChange24h": "1.36",
      "volume24h": "566888.352351323318805566128",
      "marketCap": "91278898.43224467",
      "fdv": "92698092.77927933",
      "liquidity": "5493468.9888328191850542",
      "totalSupply": "1000000000",
      "circulatingSupply": "984690145.1315308",
      "holders": "404938",
      "decimals": 18,
      "listingCex": true,
      "hotTag": false,
      "cexCoinName": "AIXBT",
      "canTransfer": false,
      "denomination": 1,
      "offline": true,
      "tradeDecimal": 8,
      "alphaId": "ALPHA_5",
      "offsell": true,
      "priceHigh24h": "0.0947757980690686554",
      "priceLow24h": "0.08953224685319805428",
      "count24h": "4046",
      "onlineTge": false,
      "onlineAirdrop": false,
      "score": 60,
      "cexOffDisplay": true,
      "stockState": false,
      "listingTime": 1734516000000,
      "mulPoint": 1,
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
- POST /bapi/asset/v1/private/alpha-trade/oto-order/place
- 请求体
```json
{"baseAsset":"ALPHA_22","quoteAsset":"USDT","workingSide":"BUY","workingPrice":48.01706542,"workingQuantity":0.2082,"paymentDetails":[{"amount":"9.99715302","paymentWalletType":"CARD"}],"pendingPrice":0.001}
```
- 响应体 
```json
{"code":"000000","message":null,"messageDetail":null,"data":{"workingOrderId":176849327,"pendingOrderId":176849328},"success":true}
```

# 获取ListenKey
-POST /bapi/defi/v1/private/alpha-trade/get-listen-key
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

