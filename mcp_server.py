# -*- coding: utf-8 -*-
"""
Glance Retail Media Brand Yield Router MCP Server
Exposes retail media GSP auction and brand yield routing tools via JSON-RPC 2.0 over STDIO.
"""

import sys
import json
from client import GlanceRetailMediaBrandYieldRouter

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "glance-retail-media-brand-yield-router", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "route_retail_media_bid",
                        "description": "Optimizes ad yield, eCPM, and GMV across L Catterton consumer portfolios, luxury fashion, and DTC retail media networks.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "impression_context": {
                                    "type": "object",
                                    "properties": {
                                        "user_cohort_wealth_index": {"type": "number"}
                                    }
                                }
                            },
                            "required": ["impression_context"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "route_retail_media_bid":
            router = GlanceRetailMediaBrandYieldRouter()
            res = router.route_retail_media_bid(
                impression_context=args.get("impression_context", {}),
                brand_campaign_bids=args.get("brand_campaign_bids")
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": f"Method '{method}' not supported"}}

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("MCP Server Discovery Test OK")
        router = GlanceRetailMediaBrandYieldRouter()
        test_res = router.route_retail_media_bid({"user_cohort_wealth_index": 1.5})
        print(f"Test Winner: {test_res['winning_campaign']['brand_name']}")
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
