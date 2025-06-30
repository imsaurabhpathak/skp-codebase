import requests
import os
import json
import re
import sys


url = "http://localhost:11434/api/generate"  

model = "deepseek-r1:1.5b"



def schema_to_prompt(fields_chunk):
    prompt = "Generate a fake JSON object based on the following schema fields. Treat fields with `[].` as arrays of objects. Output only valid JSON. Do not include explanations or extra text.\n\nFields:\n"
    for field in fields_chunk:
        prompt += f"- {field['name']}: {field['type']}\n"
    prompt += "\nOutput only the JSON object. Ensure array fields are properly nested."
    return prompt

# def extract_json_from_response(response_str):
#     # Look for content inside triple backticks or just extract first JSON-looking object
#     match = re.search(r'\{.*?\}', response_str, re.DOTALL)
#     if match:
#         try:
#             return json.loads(match.group())
#         except json.JSONDecodeError:
#             print("⚠️ JSON parsing failed")
#             return None
#     print("⚠️ No JSON object found")
#     return None

def extract_json_from_response(response_str):
    response_str = response_str.strip()

    # Strip code blocks if present
    response_str = re.sub(r"```(?:json)?", "", response_str).strip("` \n")

    # Try to extract the first JSON object or array
    json_candidate = re.search(r'(\{.*\})', response_str, re.DOTALL)
    if not json_candidate:
        print("⚠️ No JSON object found")
        print("RAW OUTPUT:\n", response_str)
        return None

    json_text = json_candidate.group(1)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        print("⚠️ JSON parsing failed:", e)
        print("⚠️ Problematic JSON:\n", json_text)
        return None

# Paste your full schema definition here
schema = {
    "name": "CtfTripSummary",
    "type": "record",
    "namespace": "com.arity.ctfenrichment.avro",
    "doc": "schema for CTF-V Trip Summary",
    "fields": [
        {"name": "tripId", "type": "string"},
        {"name": "userId", "type": "string"},
        {"name": "tripStartLatitude", "type": "double"},
        {"name": "tripEndLatitude", "type": "double"},
        {"name": "tripStartLongitude", "type": "double"},
        {"name": "tripEndLongitude", "type": "double"},
        {"name": "tripStartTimestamp", "type": "string"},
        {"name": "tripEndTimestamp", "type": "string"},
        {"name": "distance", "type": "double"},
        {"name": "totalTripMiles", "type": "double"},
        {"name": "tripMilesTime_1", "type": "double"},
        {"name": "tripMilesTime_2", "type": "double"},
        {"name": "tripMilesTime_3", "type": "double"},
        {"name": "tripMilesTime_4", "type": "double"},
        {"name": "tripMilesTime_5", "type": "double"},
        {"name": "duration", "type": "double"},
        {"name": "deviceId", "type": "string"},
        {"name": "idleTime", "type": "double"},
        {"name": "demVersion", "type": ["string", "null"]},
        {"name": "tripTerminateId", "type": "string"},
        {"name": "tripTerminateReasonCd", "type": ["string", "null"]},
        {"name": "hostSDK", "type": ["null", "string"], "default": None},
        {
            "name": "eventDetails",
            "type": {
                "type": "array",
                "items": {
                    "name": "CtfEventDetail",
                    "type": "record",
                    "fields": [
                        {"name": "type", "type": "int"},
                        {"name": "sampleSpeed", "type": "double"},
                        {"name": "speedChange", "type": "double"},
                        {"name": "sensorDetectionMethod", "type": ["null", "string"]},
                        {"name": "duration", "type": "double"},
                        {"name": "startTimestamp", "type": "string"},
                        {"name": "endTimestamp", "type": "string"},
                        {"name": "milesDriven", "type": "double"},
                        {"name": "gpsSignalStrength", "type": "int"},
                        {"name": "startLatitude", "type": "double"},
                        {"name": "startLongitude", "type": "double"},
                        {"name": "endLatitude", "type": "double"},
                        {"name": "endLongitude", "type": "double"},
                        {"name": "modelConfigID", "type": ["null", "string"], "default": None},
                        {"name": "modelConfigStatusCode", "type": ["null", "int"], "default": None},
                        {"name": "modelConfigExceptionCodes", "type": {"type": "array", "items": "int"}},
                        {"name": "modelConfigOutput", "type": {"type": "array", "items": "double"}},
                        {"name": "eventOutput", "type": {"type": "array", "items": "double"}},
                        {"name": "eventConfidence", "type": "double", "default": -1.0}
                    ]
                }
            }
        },
        {
            "name": "geoPoints",
            "type": {
                "type": "array",
                "items": {
                    "name": "CtfGeoPoint",
                    "type": "record",
                    "fields": [
                        {"name": "accuracy", "type": ["double", "null"]},
                        {"name": "bearing", "type": ["double", "null"]},
                        {"name": "latitude", "type": "double"},
                        {"name": "longitude", "type": "double"},
                        {"name": "speed", "type": "double"},
                        {"name": "timestamp", "type": "string"},
                        {"name": "pointToPointHaversineDistance", "type": "double", "default": 0}
                    ]
                }
            }
        },
        {
            "name": "accelerationEventsHistogram",
            "type": {
                "type": "array",
                "items": {
                    "name": "CtfAccelerationEvent",
                    "type": "record",
                    "fields": [
                        {"name": "eventCount", "type": ["int", "null"]},
                        {"name": "speedRangeCd", "type": ["string", "null"]}
                    ]
                }
            }
        },
        {
            "name": "brakeEventsHistogram",
            "type": {
                "type": "array",
                "items": {
                    "name": "CtfBrakeEvent",
                    "type": "record",
                    "fields": [
                        {"name": "eventCount", "type": ["int", "null"]},
                        {"name": "speedRangeCd", "type": ["string", "null"]}
                    ]
                }
            }
        },
        {
            "name": "accelerationHistogram",
            "type": {
                "type": "array",
                "items": {
                    "name": "CtfAcceleration",
                    "type": "record",
                    "fields": [
                        {"name": "secCount", "type": ["double", "null"]},
                        {"name": "speedRangeCd", "type": ["string", "null"]}
                    ]
                }
            }
        },
        {
            "name": "brakeHistogram",
            "type": {
                "type": "array",
                "items": {
                    "name": "CtfBrake",
                    "type": "record",
                    "fields": [
                        {"name": "secCount", "type": ["double", "null"]},
                        {"name": "speedRangeCd", "type": ["string", "null"]}
                    ]
                }
            }
        },
        {
            "name": "speedHistogram",
            "type": {
                "type": "array",
                "items": {
                    "name": "CtfSpeed",
                    "type": "record",
                    "fields": [
                        {"name": "secCount", "type": ["double", "null"]},
                        {"name": "speedRangeCd", "type": ["string", "null"]}
                    ]
                }
            }
        },
        {
            "name": "milesDrivenByHour",
            "type": {
                "type": "array",
                "items": {
                    "name": "CtfMilesDrivenByHour",
                    "type": "record",
                    "fields": [
                        {"name": "miles", "type": ["double", "null"]},
                        {"name": "hour", "type": ["string", "null"]}
                    ]
                }
            }
        },
        {"name": "organizationId", "type": "string"},
        {"name": "averageSpeed", "type": ["double", "null"]},
        {"name": "maxSpeed", "type": "double"},
        {"name": "tripRejectReasonCd", "type": "string"},
        {"name": "tripUploadTimestamp", "type": ["string", "null"], "default": "0000-00-00T00:00:00-00:00"},
        {"name": "tripRemoveTimestamp", "type": ["null", "string"], "default": None},
        {"name": "milesAtOrOverMaxSpeed", "type": ["double", "null"]},
        {"name": "mobileAppDevice", "type": ["null", "string"], "default": None},
        {"name": "mobileAppVersion", "type": ["null", "string"], "default": None},
        {"name": "mobileOsVersion", "type": ["null", "string"], "default": None},
        {"name": "tripProcessed_TS", "type": "string"},
        {"name": "locale", "type": ["null", "string"], "default": None},
        {"name": "isSecurityEnabled", "type": ["null", "string"], "default": None},
        {"name": "startTripBatteryLevel", "type": ["null", "double"], "default": None},
        {"name": "endTripBatteryLevel", "type": ["null", "double"], "default": None},
        {"name": "mobileOs", "type": ["null", "string"], "default": None},
        {
            "name": "distanceCalculations",
            "type": [
                "null",
                {
                    "type": "array",
                    "items": {
                        "type": "record",
                        "name": "CftDistanceCalculations",
                        "fields": [
                            {"name": "haversineDistance", "type": "double"},
                            {"name": "integrationDistance", "type": "double"},
                            {"name": "intervalDuration", "type": "int"},
                            {"name": "timeStart", "type": "string"}
                        ]
                    }
                }
            ],
            "default": None
        },
        {
            "name": "featureSupport",
            "type": [
                "null",
                {
                    "type": "record",
                    "name": "CtfFeatureSupport",
                    "fields": [
                        {
                            "name": "PhoneStatePermission",
                            "type": [
                                "null",
                                {
                                    "type": "array",
                                    "items": [
                                        "null",
                                        {
                                            "type": "record",
                                            "name": "CtfPhoneStatePermission",
                                            "fields": [
                                                {"name": "permState", "type": ["null", "int"], "default": None},
                                                {"name": "ts", "type": ["null", "long"], "default": None}
                                            ]
                                        }
                                    ]
                                }
                            ],
                            "default": None
                        },
                        {"name": "accel", "type": ["null", "int"], "default": None},
                        {"name": "baro", "type": ["null", "int"], "default": None},
                        {"name": "gravity", "type": ["null", "int"], "default": None},
                        {"name": "gyro", "type": ["null", "int"], "default": None},
                        {"name": "isSecurityEnabled", "type": ["null", "int"], "default": None},
                        {"name": "motionFitnessPermission", "type": ["null", "boolean"], "default": None}
                    ]
                }
            ],
            "default": None
        },
        {"name": "configId", "type": ["null", "string"], "default": None}
    ]
}


# Flatten nested schema
def flatten_fields(fields, prefix=""):
    flat_fields = []
    for field in fields:
        name = field["name"]
        ftype = field["type"]

        # Handle union types like ["null", "string"]
        if isinstance(ftype, list):
            ftype = next((t for t in ftype if t != "null"), "null")

        # Handle record and array types
        if isinstance(ftype, dict):
            if ftype["type"] == "record":
                flat_fields.extend(flatten_fields(ftype["fields"], prefix=f"{prefix}{name}."))
            elif ftype["type"] == "array":
                items = ftype["items"]
                if isinstance(items, dict) and items.get("type") == "record":
                    flat_fields.extend(flatten_fields(items["fields"], prefix=f"{prefix}{name}[]."))
                else:
                    flat_fields.append({"name": f"{prefix}{name}[]", "type": items})
            else:
                flat_fields.append({"name": f"{prefix}{name}", "type": ftype["type"]})
        else:
            flat_fields.append({"name": f"{prefix}{name}", "type": ftype})
    return flat_fields

# Flatten and chunk
flat_schema_fields = flatten_fields(schema["fields"])
chunk_size = 10
chunks = [flat_schema_fields[i:i + chunk_size] for i in range(0, len(flat_schema_fields), chunk_size)]



for i, chunk in enumerate(chunks, 1):
    prompt = schema_to_prompt(chunk)
    print(f"\n🔹 Prompt for Chunk {i}:\n{prompt}")
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 2048,
        "temperature": 0.7
    }
    response = requests.post(url, json=payload, stream=True)

    response_text = ""
    for line in response.iter_lines():
        if line:
            json_line = json.loads(line.decode("utf-8"))
            if "response" in json_line:
                response_text += json_line["response"]

    json_data = extract_json_from_response(response_text)
    
    print(f"\n🔸 Clean JSON for Chunk {i}:\n{json.dumps(json_data, indent=2)}")