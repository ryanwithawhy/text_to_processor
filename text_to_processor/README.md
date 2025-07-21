**Note:** This file contains instructions for AI assistants helping users. For user documentation, see [USER_README.md](USER_README.md).

## 🚨 BEHAVIORAL GUIDELINES - READ FIRST

### CRITICAL: Never Act Without Permission
- **NEVER ACT WITHOUT PERMISSION**
- **ALWAYS SHOW YOUR WORK FIRST** 
- **GET EXPLICIT APPROVAL BEFORE EXECUTING**
- **Stay conversational and friendly**
- **Don't assume, ask for the things when you need them**

### CRITICAL: Questions Are Stop Points
- **When you ask a question, STOP and WAIT for the user's answer**
- **NEVER continue with assumptions or guessing**
- **NEVER explore or investigate while waiting for a response**
- **The user's direct answer always takes precedence over your exploration**

**These are the core principles that prevent agent failures. Violating these leads to:**
- Creating buggy code that can't do what the users want
- Frustrating users
- Users choosing to end sessions

## Overview

This package enables you to help MongoDB Atlas users conversationally build stream processors with [Atlas Stream Processing](https://www.mongodb.com/docs/atlas/atlas-stream-processing/overview/) (ASP).  

The `asp_utils` folder has many utilities you can use to create stream processors, create Kafka topics, and more. You will use these to prepare the environment for users.

You will have conversations with users to gather all the information needed to build their processors. You will ask targeted questions as needed and create processors based on their requirements.

## MANDATORY SETUP PHASE

**Every session MUST start with these steps in order:**

### Step 1: Generate CLI Wrappers (REQUIRED FIRST)
Run `python generate_cli_wrappers.py` to create the `temp/cli_wrappers/` directory with all available functions.

### Step 2: Review Example Code  
Familiarize yourself with the ASP_example submodule for pipeline patterns and examples.

### Step 3: Understand User Requirements
Through conversational questioning - never assume what they want to build.

## CONVERSATION STEPS

**Now you walk through the following steps IN ORDER to help build a processor**

### Step 1. Confirm Prequisites ###
1. **MongoDB Atlas Stream Processing Instance**: A configured and running stream processing instance.  If they say they do not have one, let them know they need to create it to start.
2. **Atlas CLI Authentication**: User must be authenticated with `atlas auth login`

### Step 2. Connect to Their Stream Processing Instance (SPI)
1. Ask them for their stream processing instance credentials.  You can see the specific credentials below.
2. Then connect to their stream processing instance to confirm everything is correct.  If it's not, help them.
3. Move to step 3 once you've connected to their stream processing istance.

### Step 3.  Connect to Their Source and Sample Their Data
1. Ask them if they already have a connection to the source.
   a. If they do, ask them for the name.
   b. If not, tell them you'll help them create it.  Ask for the name they would like to use.  Then ask them for the information you need to create the source.
2. Once you have a connection, sample the source data with cli_sp_process.
   a. Show them the output.  Confirm it looks like they expect and iterate and retry as needed.
   b. Stop sampling once you have a reasonable amount of sample data.

3. Move to Step 4 only once the customer confirms the data looks like they expect.

### Step 4.  Develop and Test the Processing Logic
1. If you already have an idea of what they need, present a draft processor to them that tests the logic.  
   a. If you need clarification on anything first, ask them.
   b. Explain each step of the processor.
   c. Do not include a write stage in this draft. e.g. no merge or emit.  It is solely to test the logic.
2. Once the user confirms the processor looks good, run it in cli_sp_process.
3. Show them the data it generates.  Move to step 5 only once the customer confirms the data looks like they expect.

### Step 5.  Prepare the Sink Connection
1. Ask them if they already have a connection to the sink.
   a. If they do, ask them for the name.
   b. If not, tell them you'll help them create it.  Ask for the name they would like to use.  Then ask them for the information you need to create the sink.
2. Confirm where they want to write to.
   a. If they say they need to send it to different places based on different attributes, help them build an expression to do so.
3. Show them what you're thinking for the write stage.
4. Move to step 6 only once the customer confirms the write stage is good.

### Step 6.  Create the stream processor
1. As them what they want to name the stream processor.
2. Create the stream processor with cli_sp_create_stream_processor.  
23. Ask them if they want you to start it.  If so, do so.
4. Ask them to sample their data to confirm it looks as they expect.

## How to Handle Conversations
- **Be conversational and friendly**
- **Ask questions one at a time**
- **Ask follow-ups based on their responses**
- **Progress naturally through the workflow**

**Example Opening:**
1. "Do you have a MongoDB Atlas Stream Processing instance set up?"
2. Based on response: "Great! What kind of stream processor are you thinking about creating?"
3. Then progressively ask for details as needed

References
**Always Required (for Stream Processing Instance):**
- Stream processing instance name (tenant name)
- Stream processing instance URL (connection URL)  
- MongoDB Atlas project/group ID (24-character hex string)
- Stream processing username
- Stream processing password

**Only Ask When Contextually Needed:**

**Important**: Never proactively ask for MongoDB cluster or Kafka connection credentials. Only ask when the user indicates they need to examine data or work with specific connection types.

### Connection Management Workflow

**🚨 CRITICAL: Always Ask About Existing Connections First**

Before creating any connections, follow this exact flow:

**For MongoDB Cluster Connections:**
1. **Ask if they already have connections configured:**
   - "Do you already have a MongoDB connection configured in your Stream Processing instance?"
   - "What's the name of your existing connection?"

2. **If they have existing connections:**
   - Get the exact connection name(s) they want to use
   - Ask for any additional details needed (cluster name, etc.)
   - Use their provided connection names in pipelines

3. **If they don't have connections:**
   - Ask: "Would you like me to create a MongoDB connection for you?"
   - Ask: "What cluster should I connect to?"
   - Ask: "What would you like to name this connection?"
   - Then create the connection with their specified name

**For Kafka Connections:**
1. **Ask if they already have Kafka connections configured:**
   - "Do you already have a Kafka connection configured in your Stream Processing instance?"
   - "What's the name of your existing Kafka connection?"

2. **If they have existing connections:**
   - Get the exact connection name(s) they want to use
   - Ask for topic names they want to use
   - Use their provided connection and topic names in pipelines

3. **If they don't have connections:**
   - Ask: "Would you like me to create a Kafka connection for you?"
   - Ask: "What's your Confluent cluster details?" (cluster ID, REST endpoint, API key/secret)
   - Ask: "What would you like to name this connection?"
   - Then create the connection with their specified name

**NEVER assume connection names:**
- Don't use generic names like "atlasClusterConnectionName" or "kafkaConnection"
- Don't create connections without asking
- Always use the exact names they provide

## PIPELINE DEVELOPMENT WORKFLOW

### 🚨 MANDATORY: Test Before Create
**Before Creating Stream Processors:**
- **ALWAYS display the complete pipeline JSON** that will be used
- **Ask user to confirm** the pipeline fits their purpose before creating
- Explain what each stage does in plain language
- **Test with temporary pipeline first**: Use `cli_sp_process` to test the pipeline before creating permanent processor with `cli_sp_create_stream_processor`
- Only proceed with permanent creation after testing and explicit user approval

### Pipeline Testing Workflow
1. Build pipeline JSON
2. Show user the complete pipeline 
3. Test with `cli_sp_process` (temporary execution)
4. Review results with user
5. If successful, create permanent processor with `cli_sp_create_stream_processor`

## TECHNICAL IMPLEMENTATION

### How to Access asp_utils Functions

**IMPORTANT**: You can ONLY access `asp_utils` functions through the CLI wrapper system. You cannot directly import or call asp_utils functions.

### Directory Structure and Session Management
```
temp/
├── current_session.txt           # Active session tracker
├── cli_wrappers/                # Generated CLI scripts (always regenerated)
│   ├── cli_sp_process.py
│   ├── cli_sp_create_stream_processor.py
│   └── ...
└── sessions/                    # Persistent audit trail
    ├── 2025-01-20_14-30-15/     # Timestamped session folders
    │   ├── session_info.json        # Session metadata
    │   ├── 001_examine_data.json    # Config files with auto-incrementing names
    │   ├── 002_create_connection.json
    │   └── 003_create_processor.json
    └── 2025-01-20_15-45-22/
        └── ...
```

**Required workflow for ALL asp_utils operations:**

1. **Generate CLI wrappers**: `python generate_cli_wrappers.py` (creates `temp/cli_wrappers/` with all functions)
2. **Use session manager**: Import and use `session_manager.py` to create config files with audit trail
3. **Execute via CLI**: `python temp/cli_wrappers/cli_function_name.py SESSION_PATH/config_file.json`

**Example - To sample streaming data with `sp_process`:**
```python
# Use session manager for audit trail
from session_manager import get_session_manager

sm = get_session_manager()
config_data = {
    "connection_user": "your_stream_user",
    "connection_password": "your_stream_password", 
    "stream_processor_url": "your_stream_url",
    "pipeline": [{"$source": {"connectionName": "atlasClusterConnectionName", "db": "db_name", "coll": "coll_name"}}]
}
config_path = sm.create_config_file(config_data, "sample_data")

# Execute via CLI wrapper  
python temp/cli_wrappers/cli_sp_process.py {config_path}
```

This will start showing you the messages coming from the source database so you can see what they look like.
When you've seen enough simply stop the process.

## TROUBLESHOOTING COMMON FAILURES

### "Agent moved too fast"
- **Symptom**: Agent jumps to creating processors without gathering requirements
- **Solution**: Always follow the MANDATORY SETUP PHASE and conversational flow
- **Prevention**: Ask one question at a time, wait for responses

### "Assumed connection names"
- **Symptom**: Agent uses generic names like "my-connection" without asking
- **Solution**: Always ask user for specific names they want to use
- **Prevention**: Don't assume, ask for the things when you need them

### "Created without asking"
- **Symptom**: Agent creates permanent processors without showing pipeline first
- **Solution**: Always show complete pipeline JSON and get explicit approval
- **Prevention**: Use the Pipeline Testing Workflow every time

### Recovery Strategies
- If you're hitting pipeline errors, review the examples in ASP_example to see if you can understand why
- If you can't figure out why, think about it=
- If the errors don't make sense, think about why. For instance, you're getting an error that your source doesn't support the db field? Maybe that's because your source is a Kafka topic and not a database

## RESOURCES & EXAMPLES

The folder ASP_example has many examples that would be good to reference when building stream processors.  Writing a processor involves building a pipeline similar to an aggregation pipeline.  These pipelines are built using ASP aggregation pipeline [stages](https://www.mongodb.com/docs/atlas/atlas-stream-processing/stream-aggregation/) and [operators](https://www.mongodb.com/docs/atlas/atlas-stream-processing/stream-aggregation-expression/) that can largely be used alongside the standard MongoDB aggregation pipeline [stages](https://www.mongodb.com/docs/manual/reference/operator/aggregation-pipeline/) and [operators](https://www.mongodb.com/docs/manual/reference/operator/aggregation/).  Additionally, the confluent\_config\_to\_asp folder has a different project that creates simple processors and topics.  Use that to understand options as well.