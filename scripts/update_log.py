import json
import os
import re

def parse_transcript():
    transcript_path = "/home/codespace/.gemini/antigravity-cli/brain/52e3ad8b-5012-46b1-be22-0156a4bbd081/.system_generated/logs/transcript_full.jsonl"
    log_dir = "/workspaces/NigeriaBAY/data/log"
    log_file = os.path.join(log_dir, "log.txt")
    
    os.makedirs(log_dir, exist_ok=True)
    
    if not os.path.exists(transcript_path):
        print(f"Transcript file not found at {transcript_path}")
        return

    print(f"Parsing transcript from {transcript_path}...")
    log_entries = []
    
    with open(transcript_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                step = json.loads(line)
                step_idx = step.get("step_index", "?")
                source = step.get("source", "")
                type_ = step.get("type", "")
                created_at = step.get("created_at", "")
                content = step.get("content", "")
                tool_calls = step.get("tool_calls", [])
                
                # Format User Inputs
                if type_ == "USER_INPUT" and source == "USER_EXPLICIT":
                    # Extract request content
                    match = re.search(r'<USER_REQUEST>(.*?)</USER_REQUEST>', content, re.DOTALL)
                    user_req = match.group(1).strip() if match else content.strip()
                    entry = (
                        f"================================================================================\n"
                        f"[{created_at}] [STEP {step_idx}] USER INSTRUCTION:\n"
                        f"--------------------------------------------------------------------------------\n"
                        f"{user_req}\n"
                    )
                    log_entries.append(entry)
                    
                # Format Model Responses (Thoughts & Tool Calls)
                elif type_ == "PLANNER_RESPONSE" and source == "MODEL":
                    entry_parts = [
                        f"================================================================================\n"
                        f"[{created_at}] [STEP {step_idx}] AGENT ACTION:\n"
                        f"--------------------------------------------------------------------------------\n"
                    ]
                    # Check for text content / thoughts
                    if content:
                        entry_parts.append(f"Response:\n{content.strip()}\n")
                    
                    # Check for tool calls
                    if tool_calls:
                        entry_parts.append("Tool Calls:\n")
                        for tc in tool_calls:
                            tc_name = tc.get("name", "")
                            tc_args = tc.get("args", {})
                            tc_args_str = json.dumps(tc_args, indent=2)
                            entry_parts.append(f"  - Call {tc_name} with arguments:\n{tc_args_str}\n")
                            
                    log_entries.append("".join(entry_parts))
                    
                # Format Tool Outputs
                elif source == "MODEL" and type_ != "PLANNER_RESPONSE":
                    # This represents the output of a tool
                    entry = (
                        f"================================================================================\n"
                        f"[{created_at}] [STEP {step_idx}] TOOL OUTPUT ({type_}):\n"
                        f"--------------------------------------------------------------------------------\n"
                        f"{content.strip()}\n"
                    )
                    log_entries.append(entry)
                    
                # Format System checkpoint notifications
                elif source == "SYSTEM" and content:
                    # Ignore standard checkpoints to avoid clutter, unless they contain message content
                    if "Resuming from a compaction" not in content:
                        entry = (
                            f"================================================================================\n"
                            f"[{created_at}] SYSTEM MESSAGE:\n"
                            f"--------------------------------------------------------------------------------\n"
                            f"{content.strip()}\n"
                        )
                        log_entries.append(entry)
                        
            except Exception as e:
                print(f"Error parsing line: {e}")
                
    # Write to log.txt
    with open(log_file, 'w') as out_f:
        out_f.write("".join(log_entries))
        
    print(f"Log updated successfully at {log_file}")

if __name__ == "__main__":
    parse_transcript()
