

required features:
-adjustable attempts
-adjustable martingale 
-timer to try again
-stop loss separate from the general amount
(according to the client, he doesn't want a "real" amount)

basic operation:
0-check the first candle
1-buy or sell according to the check
2-if attempts > 0 repeat the operation
3-else change the direction (buy > sell)
4-if timmer > 0, after the attempts wait the time to start again 0
5- else keeps changing the direction until stop loss.

about API:
Lu-Yi-Hsun v5.2
https://github.com/Lu-Yi-Hsun/iqoptionapi/archive/refs/tags/5.2.zip