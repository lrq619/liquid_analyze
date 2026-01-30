import requests
import json

url = "http://localhost:8000/simulate"

data = {
    "model": "meta-llama/Llama-3.1-8B",
    "prefill_target_ms": 200,
    "workloads": [
        {"arrival": 0, "prefill_len": 2007, "decode_len": 51},
        {"arrival": 411.8974208831787, "prefill_len": 435, "decode_len": 9},
        {"arrival": 489.1974925994873, "prefill_len": 203, "decode_len": 60},
        {"arrival": 535.8200073242188, "prefill_len": 2666, "decode_len": 303},
        {"arrival": 616.8103218078613, "prefill_len": 551, "decode_len": 50},
        {"arrival": 1086.4176750183105, "prefill_len": 3526, "decode_len": 420},
        {"arrival": 1340.1572704315186, "prefill_len": 5521, "decode_len": 20},
        {"arrival": 1345.797061920166, "prefill_len": 227, "decode_len": 3},
        {"arrival": 1378.4923553466797, "prefill_len": 2568, "decode_len": 184},
        {"arrival": 1783.3688259124756, "prefill_len": 2083, "decode_len": 14},
        {"arrival": 1850.125789642334, "prefill_len": 603, "decode_len": 8},
        {"arrival": 2034.9953174591064, "prefill_len": 584, "decode_len": 37},
        {"arrival": 2094.059705734253, "prefill_len": 596, "decode_len": 21},
        {"arrival": 2095.1144695281982, "prefill_len": 2748, "decode_len": 353},
        {"arrival": 2360.0597381591797, "prefill_len": 2970, "decode_len": 3},
        {"arrival": 2602.280378341675, "prefill_len": 250, "decode_len": 53},
        {"arrival": 2602.689027786255, "prefill_len": 1042, "decode_len": 262},
        {"arrival": 2624.4866847991943, "prefill_len": 4306, "decode_len": 46},
        {"arrival": 2754.3256282806396, "prefill_len": 3427, "decode_len": 189},
        {"arrival": 2756.108522415161, "prefill_len": 2182, "decode_len": 254},
        {"arrival": 3041.1105155944824, "prefill_len": 756, "decode_len": 3},
        {"arrival": 3789.415121078491, "prefill_len": 592, "decode_len": 42},
        {"arrival": 3880.96022605896, "prefill_len": 2088, "decode_len": 352},
        {"arrival": 3990.8370971679688, "prefill_len": 558, "decode_len": 22},
        {"arrival": 3992.412328720093, "prefill_len": 4004, "decode_len": 37},
        {"arrival": 4293.853759765625, "prefill_len": 3208, "decode_len": 255},
        {"arrival": 4338.923454284668, "prefill_len": 621, "decode_len": 34},
        {"arrival": 4490.898370742798, "prefill_len": 3574, "decode_len": 13},
        {"arrival": 4735.176086425781, "prefill_len": 261, "decode_len": 49},
        {"arrival": 5290.054798126221, "prefill_len": 5540, "decode_len": 392},
        {"arrival": 5876.55234336853, "prefill_len": 550, "decode_len": 18},
        {"arrival": 6070.037841796875, "prefill_len": 439, "decode_len": 11},
        {"arrival": 6095.137119293213, "prefill_len": 387, "decode_len": 40},
        {"arrival": 6238.039970397949, "prefill_len": 505, "decode_len": 54},
        {"arrival": 6240.879058837891, "prefill_len": 417, "decode_len": 45},
        {"arrival": 6288.3782386779785, "prefill_len": 3095, "decode_len": 346},
        {"arrival": 6343.242406845093, "prefill_len": 461, "decode_len": 100},
        {"arrival": 6587.610244750977, "prefill_len": 627, "decode_len": 34},
        {"arrival": 7127.21848487854, "prefill_len": 2914, "decode_len": 314},
        {"arrival": 7254.362344741821, "prefill_len": 2097, "decode_len": 269},
        {"arrival": 8239.243268966675, "prefill_len": 342, "decode_len": 8},
        {"arrival": 8259.88745689392, "prefill_len": 1692, "decode_len": 18},
        {"arrival": 8285.6764793396, "prefill_len": 498, "decode_len": 11},
        {"arrival": 8739.091157913208, "prefill_len": 1751, "decode_len": 222},
        {"arrival": 8756.867408752441, "prefill_len": 554, "decode_len": 20},
        {"arrival": 8784.162998199463, "prefill_len": 1232, "decode_len": 51},
        {"arrival": 9341.979503631592, "prefill_len": 2346, "decode_len": 235},
        {"arrival": 9639.028072357178, "prefill_len": 4825, "decode_len": 3},
        {"arrival": 9657.634973526001, "prefill_len": 1661, "decode_len": 13},
        {"arrival": 9856.864213943481, "prefill_len": 1984, "decode_len": 3}
    ]
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response:")
print(response.text)