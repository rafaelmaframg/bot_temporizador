

<b>required features:</b><br>
-adjustable attempts<br>
-adjustable martingale <br>
-timer to try again<br>
-stop loss separate from the general amount<br>
(according to the client, he doesn't want a "real" amount)

<b>basic operation:</b><br>
0-check the first candle<br>
1-buy or sell according to the check<br>
2-if attempts > 0 repeat the operation<br>
3-else change the direction (buy > sell)<br>
4-if timmer > 0, after the attempts wait the time to start again 0<br>
5- else keeps changing the direction until stop loss.<br>

<b>about API:</b><br>
Lu-Yi-Hsun v5.2<br>
https://github.com/Lu-Yi-Hsun/iqoptionapi/archive/refs/tags/5.2.zip