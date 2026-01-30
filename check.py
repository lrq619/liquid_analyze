import re
# router_file = "/mnt/network_drive/lrq/logs/logs_2025-07-25-17-09-11/run_0/router.err"
router_file = "/mnt/network_drive/lrq/logs/logs_2025-07-26-23-02-51/run_0/router.err"

prefill_routed_str = "is routed to prefill: 7dd3aeb6"
prefill_finished_str = "finished on prefill instance: 7dd3aeb6"

decode_routed_str = ", decode: 168fc33b"
decode_finished_str = "finished on decode instance: 168fc33b"


def extract_req_id_from_router(line):
    match = re.search(r"meta-llama/Llama-3\.1-8B-(\d+)", line)
    if match:
        return int(match.group(1))
    return None

prefill_routed_id = set()
prefill_finished_id = set()

with open(router_file, 'r') as file:
    lines = file.readlines()
    for line in lines:
        if prefill_routed_str in line:
            req_id = extract_req_id_from_router(line)
            if req_id is not None:
                prefill_routed_id.add(req_id)
        elif prefill_finished_str in line:
            req_id = extract_req_id_from_router(line)
            if req_id is not None:
                prefill_finished_id.add(req_id)

print(f"length of prefill_routed_id: {len(prefill_routed_id)}")
print(f"length of prefill_finished_id: {len(prefill_finished_id)}")
print(f"missing prefill_req_ids: {prefill_routed_id - prefill_finished_id}")


decode_routed_id = set()
decode_finished_id = set()

with open(router_file, 'r') as file:
    lines = file.readlines()
    for line in lines:
        if decode_routed_str in line:
            req_id = extract_req_id_from_router(line)
            if req_id is not None:
                decode_routed_id.add(req_id)
        elif decode_finished_str in line:
            req_id = extract_req_id_from_router(line)
            if req_id is not None:
                decode_finished_id.add(req_id)

print(f"length of decode_routed_id: {len(decode_routed_id)}")
print(f"length of decode_finished_id: {len(decode_finished_id)}")
print(f"missing decode_req_ids: {decode_routed_id - decode_finished_id}")

